import json
import logging

import httpx
import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from rag_common.app import ServiceSettings, create_app
from rag_common.errors import AppError, UpstreamError, UpstreamTimeout
from rag_common.events import Event, InMemoryEventBus
from rag_common.http import ServiceClient
from rag_common.logging import JsonFormatter, request_id_var

router = APIRouter()


@router.get("/boom")
async def boom():
    raise RuntimeError("секретная деталь реализации")


@router.get("/log")
async def log_something():
    logging.getLogger("test").info("внутри запроса", extra={"answer": 42})
    return {"ok": True}


@pytest.fixture
def client():
    with TestClient(create_app(ServiceSettings(service_name="test-service"), title="t", description="d",
                               routers=[router])) as client:
        yield client


def test_json_log_has_required_fields():
    record = logging.LogRecord("svc", logging.WARNING, __file__, 1, "Заказ %s создан", ("42",), None)
    record.duration_ms = 12.5
    token = request_id_var.set("req-1")
    try:
        payload = json.loads(JsonFormatter("order-service").format(record))
    finally:
        request_id_var.reset(token)
    assert {k: payload[k] for k in ("service", "level", "request_id", "message")} == {
        "service": "order-service", "level": "WARNING", "request_id": "req-1", "message": "Заказ 42 создан"}
    assert payload["timestamp"].endswith("+00:00") and payload["duration_ms"] == 12.5


def test_unhandled_error_is_500_without_stack_trace(client, caplog):
    with caplog.at_level(logging.ERROR):
        response = client.get("/boom", headers={"X-Request-ID": "req-9"})
    assert response.status_code == 500 and response.json()["error"] == {
        "code": "internal_error", "message": "Внутренняя ошибка сервиса", "request_id": "req-9"}
    assert "секретная" not in response.text and "Traceback" not in response.text
    assert any(record.exc_info for record in caplog.records)  # stack trace — в логе


def test_request_id_reaches_application_logs(client, caplog):
    with caplog.at_level(logging.INFO):
        response = client.get("/log")
    request_id = response.headers["X-Request-ID"]
    [record] = [r for r in caplog.records if r.getMessage() == "внутри запроса"]
    assert len(request_id) == 32 and JsonFormatter("s").format(record).count(request_id) == 1


@pytest.mark.parametrize("handler, error, status", [
    (lambda r: (_ for _ in ()).throw(httpx.ReadTimeout("t")), UpstreamTimeout, 504),
    (lambda r: (_ for _ in ()).throw(httpx.ConnectError("c")), UpstreamError, 502),
    (lambda r: httpx.Response(500, json={"error": {"code": "x", "message": "boom"}}), UpstreamError, 502),
    (lambda r: httpx.Response(404, json={"error": {"code": "not_found", "message": "нет"}}), AppError, 404),
])
async def test_service_client_maps_failures(handler, error, status):
    client = ServiceClient("neighbour", "http://n", 1.0, transport=httpx.MockTransport(handler))
    with pytest.raises(error) as raised:
        await client.get("/x")
    assert raised.value.status_code == status
    await client.close()


async def test_service_client_propagates_request_id():
    seen = {}

    def handler(request):
        seen.update(request.headers)
        return httpx.Response(200, json={"ok": 1})

    client = ServiceClient("n", "http://n", 1.0, transport=httpx.MockTransport(handler))
    token = request_id_var.set("req-77")
    try:
        assert await client.get("/x") == {"ok": 1}
    finally:
        request_id_var.reset(token)
    assert seen["x-request-id"] == "req-77"
    await client.close()


async def test_events_roundtrip_and_in_memory_delivery():
    event = Event("documents.changed", {"changed": ["a"]}, source="ingestion-service", request_id="r")
    assert Event.from_json(event.to_json()) == event

    bus, received = InMemoryEventBus("x"), []

    async def handler(e):
        received.append(e)

    bus.subscribe("q", ["documents.changed"], handler)
    await bus.publish("documents.changed", {"changed": []})
    await bus.publish("other.event", {})
    assert [e.type for e in received] == ["documents.changed"] and len(bus.published) == 2
