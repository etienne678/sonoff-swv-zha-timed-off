# Uninstall and rollback

## Before removal

1. Disable every automation and script that calls the custom timed-ON helper.
2. Physically verify all valves are closed.
3. Keep a manual upstream shutoff available.
4. Back up the current configuration and logs needed for diagnosis.

## Remove the custom quirk

1. Remove `sonoff_swv_timed_off.py` from the active custom quirks directory, or
   restore the previously backed-up custom SWV quirk.
2. Ensure only one custom quirk matches `SONOFF` / `SWV`.
3. Run the Home Assistant configuration check.
4. Restart Home Assistant Core.
5. Verify which quirk now applies and test normal ON/OFF behavior safely.

Without this custom quirk, a normal ON command is no longer guaranteed by this
project to carry the 1,800-second hardware fallback. Do not leave old
automations enabled under that assumption.

## Clean stale entities

Changing quirk entity declarations can leave old entries marked `unavailable`.
Remove only verified stale entries through Home Assistant's entity settings.
Never edit `.storage` directly.

The official upstream SWV quirk may expose `Water shortage auto-close`; this is
not the same as the timed-opening feature.

## Rejoining is a last resort

Do not remove and rejoin the Zigbee device merely to clean an entity name.
Rejoining can affect entity mappings and dependent automations. First restart,
inspect the applied quirk, and clean only stale registry entities through the
supported UI/API.
