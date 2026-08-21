# Installation

## Preconditions

- Home Assistant using the ZHA integration.
- A device whose Zigbee manufacturer and model are exactly `SONOFF` / `SWV`.
- File access to the Home Assistant configuration directory.
- A current backup and a physically safe place to test water discharge.

Do not install this quirk only from a phone while nobody is near the valve.

## 1. Back up and identify the current state

1. Create a Home Assistant backup or a hypervisor-level snapshot.
2. Copy the existing custom quirks directory to a safe rollback location.
3. Export or record the device's Zigbee signature, firmware version, and current
   entities.
4. Search the existing custom quirks path for another quirk matching
   `QuirkBuilder("SONOFF", "SWV")`. Two matching custom files must not coexist.

## 2. Configure the custom quirk path

Copy `examples/configuration.yaml` into the relevant part of your own
`configuration.yaml`, adapting the path if needed:

```yaml
zha:
  custom_quirks_path: /config/custom_zha_quirks
```

If a `zha:` section already exists, merge the key; do not add a duplicate YAML
key.

## 3. Install the quirk

Copy this file:

```text
custom_zha_quirks/sonoff_swv_timed_off.py
```

to the configured directory, normally:

```text
/config/custom_zha_quirks/sonoff_swv_timed_off.py
```

Remove or move any older custom SWV quirk out of the active directory. Do not
modify Home Assistant `.storage` files.

## 4. Validate and restart

1. Run Home Assistant's configuration check.
2. Restart Home Assistant Core.
3. Inspect the startup log for the custom-quirks-loaded message and Python
   exceptions.
4. Open the ZHA device page and verify the expected switch and diagnostic
   entities remain available.

An existing device normally receives the custom quirk after a full Core
restart. If it does not, collect diagnostics before considering a remove/rejoin;
rejoining can affect entity mappings and automations.

## 5. Add the Home Assistant helper

Merge the scripts from `examples/scripts.yaml` into your `scripts.yaml`, or
recreate them in the UI. Reload scripts or restart Home Assistant.

The first helper converts a selected ZHA switch entity into its IEEE address and
sends cluster command `0x42`. The second helper retains a software delay, OFF
confirmation, retry, and persistent failure notification.

## 6. Controlled first test

Follow `TESTING.md`. The minimum acceptance test is:

1. Route water to a safe drain.
2. Have a person at the physical valve.
3. Call `script.swv_hardware_timed_on` with the target valve and `10` seconds.
4. Confirm the valve opens and physically stops water after approximately 10
   seconds without a software OFF action.
5. Confirm Home Assistant later reports the switch `off`.

Do not proceed if the valve remains open, closes at a materially different
time, the wrong valve opens, or the state cannot be reconciled.

## 7. Production integration

Use one authoritative duration per automation and pass it to both the hardware
helper and the software delay. Keep the independent software safeguards listed
in `SAFETY.md`.

Start with short, supervised runs and extend only after successful observation.
