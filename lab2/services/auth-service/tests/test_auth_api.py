from auth_helpers import ADMIN, USER

from rag_common.auth import decode_token
from rag_common.testing import as_user


def register(client, credentials=USER):
    return client.post("/api/auth/register", json=credentials)


def login(client, credentials):
    return client.post("/api/auth/login", json=credentials)


def test_register_and_login_issue_valid_jwt(client, settings, bus):
    created = register(client)
    assert created.status_code == 201 and created.json()["role"] == "user"
    assert "password" not in created.text and "password_hash" not in created.text

    token = login(client, USER).json()
    identity = decode_token(token["access_token"], secret=settings.jwt_secret, algorithm="HS256", issuer=settings.jwt_issuer)
    assert identity.user_id == created.json()["id"] and identity.role == "user"
    assert token["expires_in"] == settings.token_ttl_minutes * 60

    [event] = bus.of_type("user.registered")
    assert event.payload == {"user_id": identity.user_id, "role": "user"}  # без email


def test_register_rejects_duplicates_weak_passwords_and_bad_email(client):
    register(client)
    duplicate = register(client, {"email": "USER@example.com ", "password": "another-password"})
    assert duplicate.status_code == 409 and duplicate.json()["error"]["code"] == "email_taken"

    weak = register(client, {"email": "new@example.com", "password": "123"})
    assert weak.status_code == 400 and weak.json()["error"]["code"] == "weak_password"

    invalid = register(client, {"email": "not-an-email", "password": "long-enough"})
    body = invalid.json()["error"]
    assert invalid.status_code == 422 and body["code"] == "validation_error"
    assert body["details"][0]["field"] == "email" and "Traceback" not in invalid.text


def test_login_errors_do_not_reveal_whether_email_exists(client):
    register(client)
    wrong_password = login(client, {"email": USER["email"], "password": "wrong-password"})
    unknown_email = login(client, {"email": "nobody@example.com", "password": "wrong-password"})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json()["error"]["message"] == unknown_email.json()["error"]["message"]


def test_me_requires_identity(client):
    user_id = register(client).json()["id"]
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers=as_user(user_id)).json()["email"] == USER["email"]
    assert client.get("/api/auth/me", headers={"X-User-Id": user_id, "X-User-Role": "root"}).status_code == 401


def test_admin_manages_roles(client, settings):
    user_id = register(client).json()["id"]
    admin_token = login(client, ADMIN).json()["access_token"]
    admin = decode_token(admin_token, secret=settings.jwt_secret, algorithm="HS256", issuer=settings.jwt_issuer)

    assert client.get("/api/auth/users", headers=as_user(user_id)).status_code == 403
    page = client.get("/api/auth/users", headers=as_user(admin.user_id, "admin")).json()
    assert page["total"] == 2 and {u["role"] for u in page["items"]} == {"admin", "user"}

    promoted = client.patch(f"/api/auth/users/{user_id}/role", json={"role": "admin"}, headers=as_user(admin.user_id, "admin"))
    assert promoted.json()["role"] == "admin"
    missing = client.patch("/api/auth/users/nope/role", json={"role": "user"}, headers=as_user(admin.user_id, "admin"))
    assert missing.status_code == 404


def test_last_admin_cannot_be_demoted(client, settings):
    admin_token = login(client, ADMIN).json()["access_token"]
    admin = decode_token(admin_token, secret=settings.jwt_secret, algorithm="HS256", issuer=settings.jwt_issuer)
    response = client.patch(f"/api/auth/users/{admin.user_id}/role", json={"role": "user"}, headers=as_user(admin.user_id, "admin"))
    assert response.status_code == 409 and response.json()["error"]["code"] == "last_admin"


def test_errors_carry_request_id_and_health_endpoints(client):
    response = client.get("/api/auth/me", headers={"X-Request-ID": "req-123"})
    assert response.headers["X-Request-ID"] == "req-123" and response.json()["error"]["request_id"] == "req-123"
    assert client.get("/health").json() == {"status": "ok", "service": "auth-service"}
    ready = client.get("/ready").json()
    assert ready["status"] == "ready" and ready["checks"] == {"database": "ok"}
    assert client.get("/no-such-path").json()["error"]["code"] == "not_found"


def test_replica_starts_when_admin_was_created_concurrently(client, settings, monkeypatch):
    """Kubernetes: две реплики стартуют одновременно; вторая не видит администратора, вставка упирается в дубль."""
    from fastapi.testclient import TestClient

    from auth_service.main import create_app
    from auth_service.service import UserService
    from rag_common.events import InMemoryEventBus

    original, calls = UserService._by_email, []

    async def missed_first_lookup(self, email):
        calls.append(email)
        return None if len(calls) == 1 else await original(self, email)

    monkeypatch.setattr(UserService, "_by_email", missed_first_lookup)
    with TestClient(create_app(settings, event_bus=InMemoryEventBus("auth-service"))) as replica:
        assert replica.get("/ready").status_code == 200
    assert login(client, ADMIN).status_code == 200