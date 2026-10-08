"""Статическая проверка манифестов k8s/ без кластера: связность объектов и соответствие коду сервисов Lab2.

Ловит то, что kubectl apply пропустит молча: опечатку в имени переменной (сервис возьмёт значение по умолчанию),
порт не тот, что слушает uvicorn, Service, не попадающий в поды, ссылку на несуществующий ключ Secret.
Запуск (нужны PyYAML и pydantic-settings — есть в venv Lab2): ../lab2/.venv/Scripts/python -m pytest tests
"""

import importlib
import re
import sys
from pathlib import Path

import pytest
import yaml

LAB3 = Path(__file__).resolve().parent.parent
LAB2 = LAB3.parent / "lab2"
K8S = LAB3 / "k8s"
PACKAGES = {  # Deployment → (каталог в lab2, Python-пакет с Settings)
    "auth-service": ("services/auth-service", "auth_service"),
    "ingestion-service": ("services/ingestion-service", "ingestion_service"),
    "inference-service": ("services/inference-service", "inference_service"),
    "indexing-service": ("services/indexing-service", "indexing_service"),
    "retrieval-service": ("services/retrieval-service", "retrieval_service"),
    "chat-service": ("services/chat-service", "chat_service"),
    "analytics-service": ("services/analytics-service", "analytics_service"),
    "gateway": ("gateway", "gateway_service"),
}
WEB = "web"  # веб-интерфейс: nginx, не Python — проверяется отдельно (test_web_*)
PUBLIC = {"gateway", WEB}  # открыты наружу (NodePort)
EXTERNAL_ENV = {"OMP_NUM_THREADS", "HF_HUB_OFFLINE"}  # читают PyTorch и huggingface_hub, а не Settings
COMPOSED_ONLY = {"DB_PASSWORD", "RABBITMQ_PASSWORD"}  # только для подстановки $(VAR) в DATABASE_URL / RABBITMQ_URL


def _load() -> list[dict]:
    files = yaml.safe_load((K8S / "kustomization.yaml").read_text(encoding="utf-8"))["resources"]
    documents = []
    for name in files:
        path = K8S / name
        if name == "secrets/secret.yaml" and not path.exists():
            path = K8S / "secrets" / "secret.example.yaml"  # на чистой копии настоящего Secret нет
        documents += [doc for doc in yaml.safe_load_all(path.read_text(encoding="utf-8")) if doc]
    return documents


DOCS = _load()


def of_kind(kind: str) -> dict[str, dict]:
    return {doc["metadata"]["name"]: doc for doc in DOCS if doc["kind"] == kind}


DEPLOYMENTS, STATEFULSETS, SERVICES, CONFIGMAPS = (of_kind(kind) for kind in ("Deployment", "StatefulSet", "Service", "ConfigMap"))
SECRET_KEYS = set(of_kind("Secret")["rag-secrets"]["stringData"])


def container(workload: dict) -> dict:
    [main] = workload["spec"]["template"]["spec"]["containers"]
    return main


def settings_fields(deployment: str) -> set[str]:
    directory, package = PACKAGES[deployment]
    for path in (LAB2 / directory, LAB2 / "libs" / "common"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    settings = importlib.import_module(f"{package}.config").Settings
    return {name.upper() for name in settings.model_fields}


def test_all_resources_in_namespace_and_every_service_has_deployment():
    assert {doc["metadata"].get("namespace") for doc in DOCS if doc["kind"] != "Namespace"} == {"rag"}
    assert set(DEPLOYMENTS) == set(PACKAGES) | {WEB}
    assert set(STATEFULSETS) == {"postgres", "rabbitmq", "qdrant"}
    assert set(SERVICES) == set(DEPLOYMENTS) | set(STATEFULSETS)


@pytest.mark.parametrize("name", sorted(PACKAGES))
def test_deployment_has_image_port_probes_resources_and_security(name):
    deployment = DEPLOYMENTS[name]
    pod = deployment["spec"]["template"]["spec"]
    main = container(deployment)
    assert deployment["spec"]["selector"]["matchLabels"] == deployment["spec"]["template"]["metadata"]["labels"]
    assert re.fullmatch(rf"rag/{name}:\d+\.\d+\.\d+", main["image"]) and main["imagePullPolicy"] == "IfNotPresent"

    dockerfile = (LAB2 / PACKAGES[name][0] / "Dockerfile").read_text(encoding="utf-8")
    uvicorn_port = int(re.search(r'"--port", "(\d+)"', dockerfile).group(1))
    assert main["ports"] == [{"name": "http", "containerPort": uvicorn_port}]  # тот порт, что слушает uvicorn

    assert main["livenessProbe"]["httpGet"] == {"path": "/health", "port": "http"}
    assert main["readinessProbe"]["httpGet"] == {"path": "/ready", "port": "http"}
    for bound in ("requests", "limits"):
        assert set(main["resources"][bound]) == {"cpu", "memory"}
    assert pod["securityContext"]["runAsNonRoot"] and pod["securityContext"]["runAsUser"] == 10001
    assert main["securityContext"]["allowPrivilegeEscalation"] is False and pod["enableServiceLinks"] is False


@pytest.mark.parametrize("name", sorted(SERVICES))
def test_service_selects_pods_and_targets_named_container_port(name):
    service = SERVICES[name]
    workload = DEPLOYMENTS.get(name) or STATEFULSETS[name]
    assert service["spec"]["selector"].items() <= workload["spec"]["template"]["metadata"]["labels"].items()
    container_ports = {port["name"] for port in container(workload)["ports"]}
    assert {port["targetPort"] for port in service["spec"]["ports"]} <= container_ports
    expected_type = "NodePort" if name in PUBLIC else "ClusterIP"  # наружу — только gateway и веб-интерфейс
    assert service["spec"].get("type", "ClusterIP") == expected_type
    assert (service["spec"].get("clusterIP") == "None") == (name in STATEFULSETS)  # headless для StatefulSet


@pytest.mark.parametrize("name", sorted(PACKAGES))
def test_environment_matches_service_settings_and_references_resolve(name):
    main = container(DEPLOYMENTS[name])
    fields = settings_fields(name)
    defined = set()
    for source in main.get("envFrom", []):
        configmap = CONFIGMAPS[source["configMapRef"]["name"]]
        if source["configMapRef"]["name"] != "rag-common":  # общий ConfigMap читают разные сервисы — свои ключи
            assert set(configmap["data"]) - EXTERNAL_ENV <= fields, "ключ ConfigMap не совпадает ни с одной настройкой"
        defined |= set(configmap["data"])
    for variable in main.get("env", []):
        for reference in re.findall(r"\$\((\w+)\)", variable.get("value", "")):
            assert reference in defined, f"$({reference}) не определена до {variable['name']}"
        if secret := variable.get("valueFrom", {}).get("secretKeyRef"):
            assert secret["name"] == "rag-secrets" and secret["key"] in SECRET_KEYS
        assert variable["name"] in fields | EXTERNAL_ENV | COMPOSED_ONLY, f"{variable['name']} сервис не читает"
        defined.add(variable["name"])
    for key in {"DATABASE_URL", "RABBITMQ_URL", "JWT_SECRET"} & fields:
        assert key in defined, f"{name}: не задан {key} (сработало бы значение по умолчанию с localhost)"


def test_service_urls_in_configmap_point_to_kubernetes_services():
    common = CONFIGMAPS["rag-common"]["data"]
    for key, url in common.items():
        if key.endswith("_URL"):
            host, port = re.fullmatch(r"http://([\w-]+):(\d+)", url).groups()
            assert host in SERVICES and int(port) in {p["port"] for p in SERVICES[host]["spec"]["ports"]}, key
    assert "localhost" not in yaml.safe_dump(CONFIGMAPS)


def test_secrets_are_not_in_configmaps_and_real_secret_is_ignored_by_git():
    for configmap in CONFIGMAPS.values():
        assert not set(configmap["data"]) & SECRET_KEYS, "секретный ключ в ConfigMap"
    assert "k8s/secrets/secret.yaml" in (LAB3 / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_web_deployment_matches_nginx_image_and_proxies_to_gateway():
    deployment = DEPLOYMENTS[WEB]
    pod = deployment["spec"]["template"]["spec"]
    main = container(deployment)
    assert re.fullmatch(r"rag/web:\d+\.\d+\.\d+", main["image"]) and main["imagePullPolicy"] == "IfNotPresent"

    template = (LAB2 / "ui" / "nginx" / "default.conf.template").read_text(encoding="utf-8")
    listen = int(re.search(r"listen (\d+);", template).group(1))
    assert main["ports"] == [{"name": "http", "containerPort": listen}]  # тот порт, что слушает nginx
    assert "location = /healthz" in template and "${GATEWAY_URL}" in template
    for probe in ("livenessProbe", "readinessProbe"):
        assert main[probe]["httpGet"] == {"path": "/healthz", "port": "http"}
    for bound in ("requests", "limits"):
        assert set(main["resources"][bound]) == {"cpu", "memory"}

    dockerfile = (LAB2 / "ui" / "Dockerfile").read_text(encoding="utf-8")
    assert "nginx-unprivileged" in dockerfile  # образ работает от uid 101
    assert pod["securityContext"]["runAsNonRoot"] and pod["securityContext"]["runAsUser"] == 101
    assert main["securityContext"]["allowPrivilegeEscalation"] is False and pod["enableServiceLinks"] is False

    [source] = main["envFrom"]
    gateway_url = CONFIGMAPS[source["configMapRef"]["name"]]["data"]["GATEWAY_URL"]
    host, port = re.fullmatch(r"http://([\w-]+):(\d+)", gateway_url).groups()
    assert host == "gateway" and int(port) in {p["port"] for p in SERVICES["gateway"]["spec"]["ports"]}
