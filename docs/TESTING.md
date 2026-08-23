# Testing

## Automated tests

Create a Python environment and run:

```bash
python -m pip install -r requirements-dev.txt
pytest
ruff check .
```

The automated suite verifies duration validation, outgoing command rewriting,
replacement of stale refresh tasks, and non-cached state reconciliation with
mocked cluster transport. It does not prove physical valve behavior.

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

## Hardware/software OFF boundary test

This verifies that redundant OFF mechanisms do not leave the valve open or
cause it to reopen.

1. Use a safely drained outlet and an immediately accessible upstream shutoff.
2. Send a short timed ON, such as 15 seconds.
3. Send a normal software OFF at approximately the hardware deadline.
4. Physically confirm complete water shutoff.
5. Continue observing beyond the deadline and confirm the valve does not reopen.
6. Confirm Home Assistant reports `off` and the flow sensor, if present, later
   reports zero.

## Physical-button OFF test

1. Send a supervised timed ON long enough to operate the physical control.
2. Confirm real flow, then press the valve's physical button exactly once.
3. Confirm water stops and remains stopped.
4. Confirm Home Assistant eventually reports `off`.
5. Do not press the button a second time; an ambiguous toggle could reopen an
   unmodified device.

## Upstream water-interruption reconciliation test

This test applies only when the optional flow-reconciliation example has been
adapted and enabled.

1. Send a supervised timed ON with enough hardware time for the reconciliation
   delay to complete.
2. After real flow is confirmed, close only the upstream water supply. Do not
   touch the valve button.
3. Keep the upstream supply closed until Home Assistant confirms the valve is
   `off`.
4. Confirm the flow sensor remains below the configured threshold for the full
   reconciliation delay.
5. Confirm the automation sends OFF, verifies it, and creates the expected
   notification.
6. Reopen the upstream supply slowly and confirm water does not resume.

If state reconciliation or OFF confirmation fails, close the upstream supply,
stop the test, and restore the previous known-good configuration.

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
an entity changing to `off`. Before publishing evidence, remove valve names,
entity IDs, IEEE addresses, user or device names, network details, location
information, notification targets, and local filesystem paths.
