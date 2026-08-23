"""SONOFF SWV custom ZHA quirk with a mandatory hardware timed-off policy.

This file is derived from the Apache-2.0 licensed SONOFF SWV quirk in
zigpy/zha-device-handlers and contains substantial safety-related modifications.
See NOTICE and SAFETY.md before use.
"""

import asyncio
import typing

import zigpy.types as t
from zhaquirks import NoReplyMixin
from zigpy.zcl import foundation
from zigpy.zcl.clusters.general import OnOff
from zigpy.zcl.foundation import BaseAttributeDefs, ZCLAttributeDef

try:
    from zhaquirks.builder import QuirkBuilder
    from zhaquirks.clusters import CustomCluster
except ImportError:  # Compatibility with the API bundled with HA 2026.8.2.
    from zigpy.quirks import CustomCluster
    from zigpy.quirks.v2 import QuirkBuilder


DEFAULT_ON_TIME_SECONDS = 1800
MIN_ON_TIME_SECONDS = 1
MAX_ON_TIME_SECONDS = 1800


def normalize_on_time(value: typing.Any) -> int:
    """Return a permitted timed-on value or the 30-minute fallback."""
    try:
        on_time = int(value)
    except (TypeError, ValueError):
        return DEFAULT_ON_TIME_SECONDS

    if MIN_ON_TIME_SECONDS <= on_time <= MAX_ON_TIME_SECONDS:
        return on_time
    return DEFAULT_ON_TIME_SECONDS


class ValveState(t.enum8):
    """Water valve state reported by the manufacturer-specific cluster."""

    Normal = 0
    Water_Shortage = 1
    Water_Leakage = 2
    Water_Shortage_And_Leakage = 3


class CustomSonoffCluster(CustomCluster):
    """SONOFF manufacturer-specific cluster."""

    cluster_id = 0xFC11

    class AttributeDefs(BaseAttributeDefs):
        """Attribute definitions."""

        water_valve_state = ZCLAttributeDef(
            id=0x500C,
            type=ValveState,
        )

        # This attribute is intentionally not exposed as a duration entity.
        # It controls water-shortage auto-close behavior; it is not the
        # per-opening hardware run timer used by this project.
        auto_close_water_shortage = ZCLAttributeDef(
            id=0x5011,
            type=t.uint16_t,
        )

    @property
    def _is_manuf_specific(self):
        """Treat this cluster like the tested SWV implementation."""
        return False


class TimedOnOffCluster(NoReplyMixin, CustomCluster, OnOff):
    """Force ON through On With Timed Off and make TOGGLE fail closed."""

    cluster_id = OnOff.cluster_id
    cmd_values = OnOff.commands_by_name.values()

    async def command(
        self,
        command_id: foundation.GeneralCommand | int | t.uint8_t,
        *args,
        manufacturer: int | t.uint16_t | None = None,
        expect_reply: bool = True,
        tsn: int | t.uint8_t | None = None,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Apply the timed-off policy to outgoing On/Off cluster commands."""
        command_id = int(command_id)

        if command_id in (0x00, 0x02):
            # A TOGGLE command is deliberately converted to OFF. A water valve
            # must never be opened by an ambiguous state-changing command.
            if hasattr(self, "_turn_off_task") and self._turn_off_task:
                self._turn_off_task.cancel()
                self._turn_off_task = None

            command = self.server_commands[0x00]
            try:
                result = await self.request(
                    False,
                    command.id,
                    command.schema,
                    *args,
                    manufacturer=manufacturer,
                    expect_reply=expect_reply,
                    tsn=tsn,
                    **kwargs,
                )
            finally:
                # The device does not reliably report physical closure. Always
                # replace the old timer refresh with a fresh read after OFF.
                self._turn_off_task = self.create_catching_task(self._refresh_after_off())
            return result

        if command_id not in (0x01, 0x42):
            raise ValueError(f"Unsupported SWV OnOff command: 0x{command_id:02x}")

        # A normal ON command carries no requested duration and therefore uses
        # the mandatory 30-minute fallback. An explicit On With Timed Off
        # command may request a shorter duration for this individual opening.
        requested_on_time = kwargs.pop("on_time", None) if command_id == 0x42 else None
        on_time = normalize_on_time(requested_on_time)

        command = self.server_commands[0x42]
        kwargs["on_off_control"] = 0x00
        kwargs["on_time"] = on_time
        kwargs["off_wait_time"] = 10

        if hasattr(self, "_turn_off_task") and self._turn_off_task:
            self._turn_off_task.cancel()
        self._turn_off_task = self.create_catching_task(self._refresh_after_timeout(on_time))

        return await self.request(
            False,
            command.id,
            command.schema,
            *args,
            manufacturer=manufacturer,
            expect_reply=expect_reply,
            tsn=tsn,
            **kwargs,
        )

    async def _refresh_after_timeout(self, delay: int) -> None:
        """Refresh state because the tested valve does not report hardware OFF."""
        try:
            await asyncio.sleep(delay + 1)
            await self.endpoint.on_off.read_attributes(["on_off"], allow_cache=False)
        except asyncio.CancelledError:
            return

    async def _refresh_after_off(self) -> None:
        """Force a non-cached state reconciliation after every OFF command."""
        try:
            await asyncio.sleep(1)
            await self.endpoint.on_off.read_attributes(["on_off"], allow_cache=False)
        except asyncio.CancelledError:
            return


def is_water_shortage(valve_state: ValveState) -> bool:
    """Return whether the device reports a water-shortage condition."""
    return bool(valve_state & ValveState.Water_Shortage)


def is_water_leakage(valve_state: ValveState) -> bool:
    """Return whether the device reports a water-leakage condition."""
    return bool(valve_state & ValveState.Water_Leakage)


(
    QuirkBuilder("SONOFF", "SWV")
    .replaces(CustomSonoffCluster)
    .replaces(TimedOnOffCluster)
    .binary_sensor(
        CustomSonoffCluster.AttributeDefs.water_valve_state.name,
        CustomSonoffCluster.cluster_id,
        translation_key="water_supply",
        fallback_name="Water supply",
        unique_id_suffix="water_supply_status",
        attribute_converter=is_water_shortage,
    )
    .binary_sensor(
        CustomSonoffCluster.AttributeDefs.water_valve_state.name,
        CustomSonoffCluster.cluster_id,
        translation_key="water_leak",
        fallback_name="Water leak",
        unique_id_suffix="water_leak_status",
        attribute_converter=is_water_leakage,
    )
    .add_to_registry()
)
