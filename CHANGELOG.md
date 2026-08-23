# Changelog

All notable changes will be documented here.

## 0.1.0-alpha.1 - Unreleased

- Replace a cancelled timer refresh with a forced, non-cached state read after
  every explicit or fail-closed OFF command.
- Force the post-hardware-timeout state read to bypass the Zigbee attribute
  cache.
- Prevent example scripts from retrying ON when a start is not confirmed.
- Refuse an example timed start unless the selected valve is confirmed OFF.
- Add an optional, disabled flow-stopped reconciliation automation example.
- Add automated coverage for OFF refresh replacement and non-cached reads.
- Document supervised hardware/software boundary, physical-button, and upstream
  water-interruption acceptance tests.
- Force normal ON commands to use a 1,800-second hardware timed-off fallback.
- Permit explicit per-command durations from 1 through 1,800 seconds.
- Convert TOGGLE to OFF.
- Refresh the ZHA state after the hardware timeout.
- Keep attribute `0x5011` internal and document its water-shortage meaning.
- Preserve the current upstream unique-ID suffixes for water-status sensors.
- Add Home Assistant scripts, examples, safety documentation, tests, and CI.

The dynamic timer and state reconciliation have been physically verified on one
anonymized SONOFF SWV installation. Testing included a short hardware-only
timeout, simultaneous hardware/software OFF, physical-button OFF, and an
upstream water interruption. Broader device and firmware validation is pending.
