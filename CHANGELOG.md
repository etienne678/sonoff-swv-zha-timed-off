# Changelog

All notable changes will be documented here.

## 0.1.0-alpha.1 - Unreleased

- Force normal ON commands to use a 1,800-second hardware timed-off fallback.
- Permit explicit per-command durations from 1 through 1,800 seconds.
- Convert TOGGLE to OFF.
- Refresh the ZHA state after the hardware timeout.
- Keep attribute `0x5011` internal and document its water-shortage meaning.
- Preserve the current upstream unique-ID suffixes for water-status sensors.
- Add Home Assistant scripts, examples, safety documentation, tests, and CI.

The dynamic timer has been physically verified with a 10-second test on one
SONOFF SWV installation. Broader device and firmware validation is pending.
