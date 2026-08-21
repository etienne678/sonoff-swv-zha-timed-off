# Troubleshooting

## The quirk does not load

- Confirm `zha.custom_quirks_path` points to the directory containing the file.
- Confirm the manufacturer/model pair is exactly `SONOFF` / `SWV` in the Zigbee
  signature.
- Remove duplicate custom files that register the same pair.
- Run the Home Assistant configuration check and inspect startup logs for Python
  import exceptions.
- Do not assume the filename determines matching; the QuirkBuilder identifiers
  do.

## The valve runs for 30 minutes instead of the requested shorter duration

The fallback was used. Common causes:

- A normal `switch.turn_on` was called instead of command `0x42`.
- `on_time` was missing, zero, negative, non-numeric, or greater than 1,800.
- The example helper was not loaded or called.
- Another automation retried with a normal ON and reset the timer.

Invalid input deliberately becomes 1,800 seconds. Send OFF if the request should
not run at all.

## Home Assistant remains `on` after physical closure

The tested valve does not reliably report hardware auto-off. The quirk performs
an attribute read one second after the timer. Check Zigbee reachability and logs.
Do not reopen the valve merely to correct the UI state.

## `Auto Close Time` remains visible but unavailable

That is normally a stale Entity Registry entry from an older quirk. This project
does not create it. Delete only the unavailable `number.*_auto_close_time` entity
through Home Assistant's entity settings. Do not edit `.storage`.

## `Water shortage auto-close` disappeared

This custom quirk intentionally does not expose attribute `0x5011`. The upstream
quirk exposes it with its correct water-shortage meaning. Its old switch can
remain unavailable after installing this custom version. Read `PROTOCOL.md`
before deciding whether to maintain a separate variant.

## The physical valve does not close

Use the manual upstream shutoff immediately. Treat it as a hardware or protocol
failure, stop all automations, roll back, and collect logs only after the water
hazard is controlled.

## Reporting a problem

Include the fields listed in `COMPATIBILITY.md` and a minimal reproduction.
Sanitize diagnostics; never publish Zigbee network keys, Home Assistant tokens,
credentials, exact addresses, or private topology information.
