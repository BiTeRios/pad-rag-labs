"""Демонстрация Lab3 в Minikube: ресурсы кластера → API через gateway → логи → масштабирование → восстановление пода.

    python scripts/demo.py                       # весь сценарий
    python scripts/demo.py --skip-ask            # без вопроса к LLM (если индекс ещё строится)
    python scripts/demo.py --scale auth-service --replicas 3

Gateway открывается через kubectl port-forward на localhost:<port>. Пароль admin читается из Secret rag-secrets.
Только стандартная библиотека Python и kubectl.
"""

import argparse
import base64
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

QUESTION = "Как ограничить потребление памяти контейнером?"


class Demo:
    def __init__(self, namespace: str, port: int):
        self.namespace = namespace
        self.base_url = f"http://127.0.0.1:{port}"

    def kubectl(self, *args: str, show: bool = True) -> str:
        command = ["kubectl", "-n", self.namespace, *args]
        if show:
            print(f"$ kubectl {' '.join(args)}")
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
        if show:
            print(result.stdout.rstrip())
        return result.stdout

    def http(self, method: str, path: str, body: dict | None = None, token: str | None = None,
             request_id: str | None = None, timeout: float = 200) -> tuple[int, dict, dict]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if request_id:
            headers["X-Request-ID"] = request_id
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, json.loads(response.read() or b"{}"), dict(response.headers)
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read() or b"{}"), dict(error.headers)

    def secret(self, key: str) -> str:
        value = self.kubectl("get", "secret", "rag-secrets", "-o", f"jsonpath={{.data.{key}}}", show=False)
        return base64.b64decode(value).decode()

    def wait_gateway(self, timeout_s: float = 30) -> None:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            try:
                if self.http("GET", "/health", timeout=2)[0] == 200:
                    return
            except OSError:
                time.sleep(0.5)
        raise TimeoutError("gateway не отвечает через port-forward")


def step(title: str) -> None:
    print(f"\n=== {title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Демонстрация Lab3 в Minikube")
    parser.add_argument("--namespace", default="rag")
    parser.add_argument("--port", type=int, default=8000, help="локальный порт для port-forward к gateway")
    parser.add_argument("--scale", default="auth-service", help="какой Deployment масштабировать")
    parser.add_argument("--replicas", type=int, default=3)
    parser.add_argument("--requests", type=int, default=30, help="параллельных запросов после масштабирования")
    parser.add_argument("--skip-ask", action="store_true", help="не задавать вопрос LLM")
    args = parser.parse_args()
    demo = Demo(args.namespace, args.port)

    step("1–3. Ресурсы кластера")
    demo.kubectl("get", "deployments,statefulsets")
    demo.kubectl("get", "pods", "-o", "wide")
    demo.kubectl("get", "services")

    step(f"Gateway: kubectl port-forward svc/gateway {args.port}:8000")
    forward = subprocess.Popen(["kubectl", "-n", args.namespace, "port-forward", "svc/gateway", f"{args.port}:8000"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        demo.wait_gateway()
        return scenario(demo, args)
    finally:
        forward.terminate()


def scenario(demo: Demo, args) -> int:
    step("5. Работа API через gateway")
    status, body, _ = demo.http("GET", "/api/status")
    print(f"GET /api/status → {status}: " + ", ".join(f"{name}={state}" for name, state in body["services"].items()))
    _, body, _ = demo.http("POST", "/api/auth/login", {"email": demo.secret("ADMIN_EMAIL"), "password": demo.secret("ADMIN_PASSWORD")})
    admin = body["access_token"]
    credentials = {"email": f"k8s-{uuid.uuid4().hex[:6]}@example.com", "password": "demo-password"}
    status, body, _ = demo.http("POST", "/api/auth/register", credentials)
    print(f"POST /api/auth/register → {status}: {body.get('email')}")
    user = demo.http("POST", "/api/auth/login", credentials)[1]["access_token"]
    print(f"GET /api/chat/conversations без токена → {demo.http('GET', '/api/chat/conversations')[0]}")
    print(f"POST /api/ingestion/runs от user → {demo.http('POST', '/api/ingestion/runs', token=user)[0]}")
    _, index, _ = demo.http("GET", "/api/indexing/status", token=admin)
    print(f"Индекс: документов {index['documents']}, chunks {index['points']}, идёт задача: {bool(index['running'])}")

    if not args.skip_ask:
        request_id = f"demo-{uuid.uuid4().hex[:8]}"
        started = time.perf_counter()
        status, answer, _ = demo.http("POST", "/api/chat/ask", {"question": QUESTION}, token=user, request_id=request_id)
        print(f"POST /api/chat/ask → {status} за {time.perf_counter() - started:.1f} с\n  Вопрос: {QUESTION}")
        if status == 200:
            print("  " + answer["answer"].replace("\n", "\n  "))
            for source in answer["sources"]:
                print(f"  [{source['n']}] {source['title']} — {source['url']}")

        step(f"4. Логи: один request_id ({request_id}) в gateway → chat → retrieval → inference")
        for app in ("gateway", "chat-service", "retrieval-service", "inference-service"):
            lines = [line for line in demo.kubectl("logs", "-l", f"app={app}", "--prefix", "--tail", "500", show=False).splitlines()
                     if request_id in line]
            for line in lines[-2:]:
                pod, _, record = line.partition(" ")
                entry = json.loads(record)
                print(f"  {pod.split('/')[1]:<38} {entry['level']:<5} {entry['message']} {entry.get('path', '')}")

    target = args.scale
    step(f"6. Масштабирование: {target} → {args.replicas} реплики")
    before = int(demo.kubectl("get", "deployment", target, "-o", "jsonpath={.spec.replicas}", show=False))
    demo.kubectl("scale", "deployment", target, f"--replicas={args.replicas}")
    demo.kubectl("rollout", "status", f"deployment/{target}", "--timeout=180s")
    demo.kubectl("get", "pods", "-l", f"app={target}")
    batch = f"scale-{uuid.uuid4().hex[:6]}"
    with ThreadPoolExecutor(max_workers=args.requests) as pool:
        codes = list(pool.map(lambda n: demo.http("GET", "/api/auth/me", token=user, request_id=f"{batch}-{n}")[0],
                              range(args.requests)))
    served = Counter(line.split(" ", 1)[0].split("/")[1]
                     for line in demo.kubectl("logs", "-l", f"app={target}", "--prefix", "--tail", "1000", show=False).splitlines()
                     if batch in line)
    print(f"{args.requests} параллельных GET /api/auth/me: коды {dict(Counter(codes))}; обработали поды:")
    for pod, count in sorted(served.items()):
        print(f"  {pod}: {count}")

    step("7. Восстановление: удаляем под — Deployment создаёт новый")
    victim = demo.kubectl("get", "pods", "-l", f"app={target}", "-o", "jsonpath={.items[0].metadata.name}", show=False)
    demo.kubectl("delete", "pod", victim, "--wait=false")
    time.sleep(2)
    demo.kubectl("get", "pods", "-l", f"app={target}")
    demo.kubectl("rollout", "status", f"deployment/{target}", "--timeout=180s")
    demo.kubectl("get", "pods", "-l", f"app={target}")
    print(f"GET /api/auth/me после восстановления → {demo.http('GET', '/api/auth/me', token=user)[0]}")

    step(f"Возврат: {target} → {before} реплики")
    demo.kubectl("scale", "deployment", target, f"--replicas={before}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
