import pytest

from src import ingest


def run_with(monkeypatch, codes: dict[str, int]) -> tuple[int, list[str]]:
    called = []

    def step(name):
        def run(argv):
            called.append(name)
            assert argv == ["--log-level", "INFO"]
            return codes.get(name, 0)
        return run

    monkeypatch.setattr(ingest, "STEPS", tuple((name, step(name)) for name, _ in ingest.STEPS))
    return ingest.main([]), called


@pytest.mark.parametrize(
    ("codes", "expected_code", "expected_steps"),
    [
        ({}, 0, ["grabber", "preprocessing", "embeddings"]),
        ({"grabber": 2}, 2, ["grabber", "preprocessing", "embeddings"]),  # часть файлов не скачана: индексируем
        ({"grabber": 1}, 1, ["grabber"]),  # источник недоступен: дальше не идём
        ({"preprocessing": 1}, 1, ["grabber", "preprocessing"]),
    ],
)
def test_ingest_runs_steps_in_order_and_stops_on_error(monkeypatch, codes, expected_code, expected_steps):
    code, called = run_with(monkeypatch, codes)
    assert (code, called) == (expected_code, expected_steps)
