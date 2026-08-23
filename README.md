# SONOFF SWV ZHA Timed Off

> [!CAUTION]
> Experimental software controls a physical water valve. Software, firmware,
> Zigbee, radio, power, or configuration failures can leave a valve open and
> cause flooding, property damage, injury, or financial loss. Read
> [SAFETY.md](SAFETY.md), test over a safe drain, and use independent physical
> safeguards. The software is provided **as is**, without warranty.

An experimental ZHA custom quirk for the SONOFF SWV Zigbee water valve. It
forces every normal ON command to carry a 30-minute hardware timed-off fallback
and permits a shorter timer to be selected for each individual valve opening.

The project is currently **alpha**. The timer mechanism and redundant OFF state
reconciliation have been physically verified on one anonymized installation.
They have not been validated across all SWV firmware, ZHA, zigpy, coordinator,
or Home Assistant versions.

[Deutsche Dokumentation](README.de.md)

## Why this exists

A Home Assistant software delay cannot close a valve while Home Assistant,
Zigbee, the coordinator, or the radio path is unavailable. A timer delivered to
the valve before it opens can continue running in the valve hardware.

This quirk adds two policies:

| Request | Command sent to the valve |
| --- | --- |
| Normal `switch.turn_on` / On command | `On With Timed Off` (`0x42`) with `on_time=1800` |
| Explicit `0x42` with `on_time=1..1800` | `On With Timed Off` with that individual value |
| Missing, invalid, zero, negative, or over-limit value | 1,800-second fallback |
| OFF | OFF |
| TOGGLE | OFF; an ambiguous command is never allowed to open water |

The hardware timer complements software OFF commands; it does not replace
them. The examples retain a Home Assistant delay, an explicit OFF, a retry, and
failure reporting. Every explicit OFF and hardware deadline is followed by a
forced, non-cached state read so a missed device report does not leave an old ON
state indefinitely.

## The `Auto Close Time` misunderstanding

Two unrelated mechanisms are easy to confuse:

| Mechanism | Meaning |
| --- | --- |
| On/Off command `0x42`, field `on_time` | Hardware timeout for this individual valve opening |
| SONOFF attribute `0x5011` in cluster `0xFC11` | Water-shortage auto-close configuration |

Attribute `0x5011` is **not** the general per-opening run timer. The current
upstream SWV quirk also names it `auto_close_water_shortage` and exposes it as a
`Water shortage auto-close` switch, not a freely adjustable duration:

<https://github.com/zigpy/zha-device-handlers/blob/dev/zhaquirks/sonoff/swv.py>

This custom quirk intentionally does not expose `0x5011`. Installing it over a
version that exposed either `Auto Close Time` or the upstream
`Water shortage auto-close` switch can leave that old entity marked
`unavailable`; remove only that verified stale entity through Home Assistant's
entity settings. Never edit `.storage` directly. The two water-status binary
sensors retain the current upstream unique-ID suffixes to avoid unnecessary
entity churn.

## Included files

- [`custom_zha_quirks/sonoff_swv_timed_off.py`](custom_zha_quirks/sonoff_swv_timed_off.py): the custom quirk.
- [`examples/scripts.yaml`](examples/scripts.yaml): dynamic timed-ON helper and a software-verified valve cycle.
- [`examples/automation.yaml`](examples/automation.yaml): disabled example automation.
- [`examples/flow_reconciliation_automation.yaml`](examples/flow_reconciliation_automation.yaml): optional disabled example for sustained zero flow while state remains ON.
- [`docs/INSTALLATION.md`](docs/INSTALLATION.md): backup, installation, verification, and first test.
- [`docs/PROTOCOL.md`](docs/PROTOCOL.md): command behavior and the `0x5011` distinction.
- [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md): tested and untested combinations.
- [`docs/TESTING.md`](docs/TESTING.md): automated and controlled physical tests.
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md): common failure modes.
- [`docs/UNINSTALL.md`](docs/UNINSTALL.md): complete rollback procedure.
- [`docs/PUBLISHING.md`](docs/PUBLISHING.md): GitHub metadata and release checklist.

## Quick start

Do not start with a connected indoor water line. Follow the full
[installation guide](docs/INSTALLATION.md).

1. Back up Home Assistant and the existing custom quirk directory.
2. Copy `sonoff_swv_timed_off.py` into the configured ZHA custom quirks path.
3. Configure `zha.custom_quirks_path` if it is not already configured.
4. Run a Home Assistant configuration check and restart Home Assistant.
5. Confirm the custom quirk loaded in the logs.
6. Install the helper from `examples/scripts.yaml`.
7. Perform a controlled 10-second test over a safe drain and physically confirm
   closure before using longer durations.

## Required layered safety

At minimum, production automations should retain all of these:

- Per-opening hardware timed-off command.
- Home Assistant software delay followed by explicit OFF.
- State confirmation, one OFF retry, and visible failure notification.
- A separate maximum-runtime watchdog that survives automation reloads.
- A startup/reconnection policy for valves reported open.
- Physical isolation, appropriate drainage, and leak detection where damage is
  possible.

No Zigbee quirk is a certified flood-prevention device.

## Compatibility and maintenance

The quirk matches exactly manufacturer `SONOFF` and model `SWV`. Custom quirks
replace upstream behavior and can lag improvements in `zha-device-handlers`.
Review upstream changes before each Home Assistant upgrade and repeat the short
hardware test afterwards.

New quirks use the Quirks V2 API. The source includes an import fallback for the
API paths bundled with the physically tested Home Assistant 2026.8.3 instance.

## License and attribution

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). This project is
derived from the Apache-2.0 licensed upstream SONOFF SWV device handler and is
not affiliated with SONOFF, Home Assistant, ZHA, zigpy, or their maintainers.

The license contains warranty and liability limitations, subject to applicable
law. The prominent safety warning is operational guidance, not legal advice.
