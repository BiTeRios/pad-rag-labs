import json

import httpx
import pytest
from fastapi.testclient import TestClient

from gateway_service.config import Settings
from gateway_service.main import create_app
from rag_common.auth import create_token

SECRET = "gateway-test-secret-gateway-test-secret"


def token(user_id="u1", role="user", ttl=60) -> str:
    return create_token(user_id, role, secret=SECRET, algorithm="HS256", ttl_minutes=ttl, issuer="rag-auth")


def bearer(user_id="u1", role="user", ttl=60) -> dict:
    return {"Authorization": f"Bearer {token(user_id, role, ttl)}"}


class Upstreams:
    """Все сервисы: эхо запроса; отдельные хосты можно «замедлить» или «уронить»."""

    def __init__(self):
        self.calls: list[httpx.Request] = []
        self.failures: dict[str, Exception] = {}
        self.not_ready: set[str] = set()

    def transport(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            host = request.url.host
            if host in self.failures:
                raise self.failures[host]
            if request.url.path == "/ready":
                return httpx.Response(503 if host in self.not_ready else 200, json={})
            if request.url.path == "/openapi.json":
                return httpx.Response(200, json={"openapi": "3.1.0", "paths": {
                    "/api/chat/ask": {"post": {"parameters": [{"name": "X-User-Id", "in": "header"},
                                                              {"name": "limit", "in": "query"}]}},
                    "/internal/search": {"post": {}}, "/health": {"get": {}}}})
            self.calls.append(request)
            if request.url.path == "/api/chat/conversations/missing":
                return httpx.Response(404, json={"error": {"code": "not_found", "message": "Диалог не найден"}})
            return httpx.Response(200, json={"host": host, "path": request.url.path, "query": request.url.query.decode(),
                                             "headers": dict(request.headers), "body": request.content.decode()})
        return httpx.MockTransport(handle)


@pytest.fixture
def upstreams() -> Upstreams:
    return Upstreams()


@pytest.fixture
def client(upstreams):
    settings = Settings(jwt_secret=SECRET, rate_limit_per_minute=1000, **{
        f"{name}_url": f"http://{name}" for name in ("auth", "ingestion", "inference", "indexing", "retrieval", "chat", "analytics")})
    with TestClient(create_app(settings, transport=upstreams.transport())) as client:
        yield client


def test_public_route_works_without_token_and_strips_spoofed_identity(client, upstreams):
    response = client.post("/api/auth/login", json={"email": "a@b.c", "password": "x"},
                           headers={"X-User-Id": "admin-1", "X-User-Role": "admin"})
    echo = response.json()
    assert response.status_code == 200 and echo["host"] == "auth" and json.loads(echo["body"])["email"] == "a@b.c"
    assert "x-user-id" not in echo["headers"] and "x-user-role" not in echo["headers"]


def test_protected_route_requires_valid_token(client, upstreams):
    assert client.get("/api/chat/conversations").json()["error"]["code"] == "unauthorized"
    assert client.get("/api/chat/conversations", headers={"Authorization": "Bearer junk"}).json()["error"]["code"] == "invalid_token"
    expired = client.get("/api/chat/conversations", headers=bearer(ttl=-1))
    assert expired.status_code == 401 and expired.json()["error"]["code"] == "token_expired"
    assert upstreams.calls == []  # до сервисов запросы не дошли


def test_identity_request_id_and_query_are_forwarded(client):
    response = client.get("/api/chat/conversations", params={"limit": 5},
                          headers={**bearer("u7", "user"), "X-Request-ID": "req-42", "X-User-Role": "admin"})
    echo = response.json()
    assert echo["host"] == "chat" and echo["query"] == "limit=5"
    assert echo["headers"]["x-user-id"] == "u7" and echo["headers"]["x-user-role"] == "user"  # подделка заменена
    assert echo["headers"]["x-request-id"] == "req-42" and response.headers["X-Request-ID"] == "req-42"
    assert "authorization" not in echo["headers"]  # токен сервисам не нужен


def test_roles_are_checked_at_gateway(client, upstreams):
    denied = client.get("/api/analytics/summary", headers=bearer(role="user"))
    assert denied.status_code == 403 and upstreams.calls == []
    assert client.get("/api/analytics/summary", headers=bearer(role="admin")).json()["host"] == "analytics"


def test_unknown_and_internal_paths_are_not_routed(client):
    assert client.get("/api/unknown", headers=bearer()).status_code == 404
    assert client.post("/internal/search", json={}).status_code == 404
    assert client.get("/api/chat/conversations/missing", headers=bearer()).json()["error"]["message"] == "Диалог не найден"


def test_rate_limit_per_route_and_user(client):
    for _ in range(10):
        assert client.post("/api/chat/ask", json={"question": "q"}, headers=bearer("u1")).status_code == 200
    limited = client.post("/api/chat/ask", json={"question": "q"}, headers=bearer("u1"))
    assert limited.status_code == 429 and int(limited.headers["Retry-After"]) > 0
    assert client.post("/api/chat/ask", json={"question": "q"}, headers=bearer("u2")).status_code == 200  # другой пользователь
    assert client.get("/api/chat/conversations", headers=bearer("u1")).status_code == 200  # другой маршрут


@pytest.mark.parametrize("error, status, code", [
    (httpx.ReadTimeout("slow"), 504, "upstream_timeout"),
    (httpx.ConnectError("refused"), 502, "upstream_error"),
])
def test_upstream_failures(client, upstreams, error, status, code):
    upstreams.failures["chat"] = error
    response = client.get("/api/chat/conversations", headers=bearer())
    assert response.status_code == status and response.json()["error"]["code"] == code
    assert "chat-service" in response.json()["error"]["message"] and "Traceback" not in response.text


def test_status_aggregates_readiness(client, upstreams):
    assert client.get("/api/status").json()["status"] == "ok"
    upstreams.not_ready.add("inference")
    upstreams.failures["analytics"] = httpx.ConnectError("down")
    response = client.get("/api/status")
    assert response.status_code == 503
    assert response.json()["services"]["inference"] == "not_ready" and response.json()["services"]["analytics"] == "unreachable"


def test_service_openapi_is_adapted_for_gateway(client):
    spec = client.get("/openapi/chat.json").json()
    assert list(spec["paths"]) == ["/api/chat/ask"]  # без /internal и проб
    assert [p["name"] for p in spec["paths"]["/api/chat/ask"]["post"]["parameters"]] == ["limit"]
    assert spec["security"] == [{"bearer": []}]
    assert "swagger" in client.get("/docs/chat").text.lower()
    assert client.get("/docs/inference").status_code == 404


def test_bad_routes_file_fails_fast(tmp_path):
    routes = tmp_path / "routes.yaml"
    routes.write_text("routes:\n  - {prefix: /api/x, service: nope}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="неизвестные сервисы"):
        create_app(Settings(jwt_secret=SECRET, routes_file=routes))
