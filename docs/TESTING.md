# Testing

## Automated tests

Create a Python environment and run:

```bash
python -m pip install -r requirements-dev.txt
pytest
ruff check .
```

The automated suite verifies duration validation and outgoing command rewriting
with mocked cluster transport. It does not prove physical valve behavior.

## Controlled hardware acceptance test

Only test where unexpected water discharge cannot cause damage.

1. Back up the current installation and keep the previous quirk available.
2. Route the valve outlet to a safe drain.
3. Station a person at a manual upstream shutoff.
4. Ensure no other water automation can start during the test.
5. Send a 10-second timed ON through `script.swv_hardware_timed_on`.
6. Do not send a software OFF during this first proof.
7. Measure physical opening and closure, not only the Home Assistant state.
8. Confirm state refresh to `off` after closure.
9. Repeat once before increasing the duration.

Stop immediately if the wrong valve opens or physical closure does not occur at
the expected time.

## Normal-ON fallback test

The default 1,800-second test consumes water and is long. Use a dry or safely
drained setup and supervision. A shorter temporary development constant can
prove command rewriting, but the final 1,800-second build still requires its own
acceptance decision before unattended use.

## Availability-loss test

This test intentionally removes infrastructure and can create an open-valve
hazard. Perform it only with safe drainage and an immediately accessible manual
shutoff.

1. Deliver a short hardware timed command and confirm the valve opened.
2. Remove only the test infrastructure necessary to simulate the intended
   failure; do not improvise with mains wiring.
3. Confirm physical closure occurs without Home Assistant sending OFF.
4. Restore infrastructure and reconcile the reported state.

Never conduct this test where a failure could flood a building or landscape.

## Release evidence

Record the compatibility fields in `COMPATIBILITY.md`, the exact commit, timer
value, measured duration, and outcome. Do not claim compatibility based only on
an entity changing to `off`.
