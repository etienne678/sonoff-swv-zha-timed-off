# Compatibility

## Physically verified installation

| Component | Verified value |
| --- | --- |
| Home Assistant Core | 2026.8.3 |
| Integration | ZHA |
| Zigbee manufacturer | `SONOFF` |
| Zigbee model | `SWV` |
| Explicit timer test | Raw `on_time=10`; physical closure after about 10.4 s |
| Hardware/software boundary | 15-second hardware timeout plus software OFF at the boundary; closed without reopening |
| Physical-button OFF | Water stopped and ZHA updated to `off` |
| Upstream water interruption | Optional reconciliation detected sustained zero flow and confirmed OFF after about 30 s |
| Normal-ON fallback | 1,800 s policy used on the source installation |
| Firmware version | Not yet recorded for the public compatibility matrix |
| Coordinator / radio | Not yet recorded for the public compatibility matrix |

The timer and reconciliation core in this repository are based on the physically
tested deployed quirk. All published evidence is deliberately anonymized. The
repository packaging, compatibility import path, current-upstream
unique-ID suffixes for the two water-status sensors, CI, and generic examples are
an alpha release candidate and require a clean installation test before a
stable release.

## Not implied by this test

Testing one valve does not establish compatibility with:

- Every product sold as SONOFF SWV.
- Different SWV firmware or hardware revisions.
- Zigbee2MQTT or other coordinators; this is a ZHA quirk only.
- Future Home Assistant, ZHA, zigpy, or zha-device-handlers releases.
- Values outside the documented 1-to-1,800 range.
- Water-shortage attribute `0x5011` behavior.

## Reporting additional results

Compatibility reports should include:

- Home Assistant Core version.
- Device firmware and hardware revision.
- ZHA device signature and sanitized diagnostics.
- Coordinator model and firmware.
- Requested raw timer value and measured physical duration.
- Whether the timer survived loss of Home Assistant/coordinator availability.
- Whether Home Assistant eventually refreshed to `off`.
- Whether an explicit OFF near the hardware deadline caused any reopening.
- Whether an early physical-button OFF was reflected in Home Assistant.
- If flow reconciliation was tested, its configured delay and observed result.

Remove IEEE addresses, network keys, location data, and other sensitive values
before publishing diagnostics.
