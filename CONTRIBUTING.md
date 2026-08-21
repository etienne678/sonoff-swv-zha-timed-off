# Contributing

Contributions are welcome, but water-control changes require unusually careful
evidence and review.

## Before opening a change

- Read `SAFETY.md` and `docs/PROTOCOL.md`.
- Search existing issues and upstream `zigpy/zha-device-handlers` changes.
- Do not include private IEEE addresses, Zigbee network keys, access tokens,
  credentials, exact home addresses, or unsanitized diagnostics.
- Do not claim compatibility without a measured physical test.

## Development checks

```bash
python -m pip install -r requirements-dev.txt
ruff check .
pytest
```

Changes to command rewriting, duration limits, fallback behavior, retry logic,
or device matching must include tests and an entry in `CHANGELOG.md`.

## Hardware reports

Use the fields in `docs/COMPATIBILITY.md`. Clearly distinguish:

- Home Assistant state from observed physical water flow.
- `on_time` command behavior from attribute `0x5011`.
- A software OFF result from autonomous hardware closure.

Describe the test drainage and manual shutoff precautions without publishing
sensitive location information.

## Upstream relationship

This repository derives from `zigpy/zha-device-handlers`. Review the current
upstream SONOFF SWV quirk before changing entity declarations or imports. Mark
modified files prominently and retain Apache-2.0 attribution.

An upstream contribution may be preferable to a permanent fork if maintainers
accept an opt-in or otherwise safe timed-off design.
