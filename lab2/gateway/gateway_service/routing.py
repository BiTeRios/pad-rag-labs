"""Таблица маршрутов и rate limiter."""

import math
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Route:
    prefix: str
    service: str
    auth: str = "required"            # public | required
    roles: tuple[str, ...] = ()
    rate_limit_per_minute: int | None = None
    timeout_s: float | None = None

    def matches(self, path: str) -> bool:
        return path == self.prefix or path.startswith(self.prefix.rstrip("/") + "/")


def load_routes(path: Path, services: set[str]) -> list[Route]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    routes = [Route(**{**item, "roles": tuple(item.get("roles", ()))}) for item in data["routes"]]
    unknown = {route.service for route in routes} - services
    if unknown:
        raise ValueError(f"в {path} неизвестные сервисы: {sorted(unknown)}")
    if bad := [route.prefix for route in routes if route.auth not in ("public", "required")]:
        raise ValueError(f"auth должен быть public или required: {bad}")
    return routes


def find_route(routes: list[Route], path: str) -> Route | None:
    return next((route for route in routes if route.matches(path)), None)


@dataclass
class _Bucket:
    tokens: float
    updated: float


@dataclass
class RateLimiter:
    """Token bucket в памяти процесса: ёмкость = лимит в минуту, пополнение равномерное.

    При нескольких репликах gateway лимит действует на реплику; общий лимит потребовал бы Redis.
    """

    buckets: dict[str, _Bucket] = field(default_factory=dict)
    clock: callable = time.monotonic
    max_keys: int = 10_000  # защита памяти: при переполнении забываются корзины, простаивающие > 10 мин

    def check(self, key: str, per_minute: int) -> float | None:
        """None — запрос разрешён; иначе через сколько секунд повторить."""
        if per_minute <= 0:
            return None
        now = self.clock()
        if len(self.buckets) > self.max_keys:
            self.buckets = {k: b for k, b in self.buckets.items() if now - b.updated < 600}
        bucket = self.buckets.get(key)
        if bucket is None:
            bucket = self.buckets[key] = _Bucket(per_minute, now)
        bucket.tokens = min(per_minute, bucket.tokens + (now - bucket.updated) * per_minute / 60)
        bucket.updated = now
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return None
        return math.ceil((1 - bucket.tokens) * 60 / per_minute)
