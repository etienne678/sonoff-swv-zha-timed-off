"""Unit tests for the SONOFF SWV timed-off policy."""

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

QUIRK_PATH = Path(__file__).parents[1] / "custom_zha_quirks" / "sonoff_swv_timed_off.py"


@pytest.fixture(scope="module")
def quirk_module() -> ModuleType:
    """Load the custom quirk from its distributable file."""
    spec = importlib.util.spec_from_file_location("sonoff_swv_timed_off", QUIRK_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, 1800),
        ("not-a-number", 1800),
        (-1, 1800),
        (0, 1800),
        (1, 1),
        ("10", 10),
        (1799, 1799),
        (1800, 1800),
        (1801, 1800),
    ],
)
def test_normalize_on_time(quirk_module: ModuleType, value: Any, expected: int) -> None:
    """Only values inside the permitted interval pass through."""
    assert quirk_module.normalize_on_time(value) == expected


class FakeTask:
    """Minimal task object used to verify cancellation behavior."""

    def __init__(self) -> None:
        self.cancelled = False

    def cancel(self) -> None:
        """Record cancellation."""
        self.cancelled = True


def make_cluster_harness(
    quirk_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Any, list[tuple[tuple[Any, ...], dict[str, Any]]]]:
    """Construct the cluster without radio transport and capture requests."""
    cluster_class = quirk_module.TimedOnOffCluster
    cluster = object.__new__(cluster_class)
    requests: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    async def fake_request(self: Any, *args: Any, **kwargs: Any) -> str:
        requests.append((args, kwargs))
        return "sent"

    def fake_create_catching_task(self: Any, coroutine: Any) -> FakeTask:
        coroutine.close()
        return FakeTask()

    monkeypatch.setattr(cluster_class, "request", fake_request)
    monkeypatch.setattr(cluster_class, "create_catching_task", fake_create_catching_task)
    return cluster, requests


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("command_id", "params", "expected_command", "expected_on_time"),
    [
        (0x01, {}, 0x42, 1800),
        (0x42, {"on_time": 10}, 0x42, 10),
        (0x42, {"on_time": 0}, 0x42, 1800),
        (0x00, {}, 0x00, None),
        (0x02, {}, 0x00, None),
    ],
)
async def test_command_rewriting(
    quirk_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    command_id: int,
    params: dict[str, Any],
    expected_command: int,
    expected_on_time: int | None,
) -> None:
    """Outgoing commands obey the timed-on and fail-closed policies."""
    cluster, requests = make_cluster_harness(quirk_module, monkeypatch)

    assert await cluster.command(command_id, **params) == "sent"
    assert len(requests) == 1
    request_args, request_kwargs = requests[0]
    assert request_args[1] == expected_command

    if expected_on_time is None:
        assert "on_time" not in request_kwargs
    else:
        assert request_kwargs["on_time"] == expected_on_time
        assert request_kwargs["on_off_control"] == 0
        assert request_kwargs["off_wait_time"] == 10


@pytest.mark.asyncio
async def test_unsupported_command_fails(
    quirk_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unreviewed On/Off commands are rejected."""
    cluster, requests = make_cluster_harness(quirk_module, monkeypatch)

    with pytest.raises(ValueError, match="Unsupported SWV OnOff command"):
        await cluster.command(0x40)
    assert requests == []


@pytest.mark.asyncio
async def test_off_cancels_old_refresh_and_schedules_reconciliation(
    quirk_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OFF must replace, rather than merely cancel, the pending state refresh."""
    cluster, requests = make_cluster_harness(quirk_module, monkeypatch)
    old_task = FakeTask()
    cluster._turn_off_task = old_task

    assert await cluster.command(0x00) == "sent"
    assert old_task.cancelled is True
    assert cluster._turn_off_task is not old_task
    assert isinstance(cluster._turn_off_task, FakeTask)
    assert len(requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["_refresh_after_off", "_refresh_after_timeout"])
async def test_state_reconciliation_bypasses_cache(
    quirk_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
) -> None:
    """Timer and OFF reconciliation must read the physical device, not cache."""
    calls: list[tuple[list[str], dict[str, Any]]] = []

    async def fake_sleep(_delay: int) -> None:
        return None

    class FakeOnOff:
        async def read_attributes(self, attributes: list[str], **kwargs: Any) -> None:
            calls.append((attributes, kwargs))

    class FakeEndpoint:
        on_off = FakeOnOff()

    cluster = object.__new__(quirk_module.TimedOnOffCluster)
    cluster._endpoint = FakeEndpoint()
    monkeypatch.setattr(quirk_module.asyncio, "sleep", fake_sleep)

    coroutine = getattr(cluster, method)
    if method == "_refresh_after_timeout":
        await coroutine(10)
    else:
        await coroutine()

    assert calls == [(["on_off"], {"allow_cache": False})]
