# Safety and risk notice

## Read this before installation

This project controls a physical water valve. A valve that remains open can
cause flooding, mold, electrical hazards, property damage, injury, interruption
of water service, and significant financial loss.

The project is experimental, is not safety-certified, and is not a substitute
for a certified shutoff system, pressure regulator, backflow prevention,
supervised irrigation controller, leak protection system, or appropriate
insurance and maintenance.

The software is provided under the Apache License 2.0 on an **as-is** basis,
without warranties or conditions. Liability limitations are subject to
applicable law. This document is technical risk guidance, not legal advice.

## Known failure paths

- The timed command is not delivered, is corrupted, or is interpreted
  differently by another firmware version.
- The device opens but loses radio contact before a software OFF command.
- Home Assistant, ZHA, the coordinator, the network, or power fails.
- The valve mechanically sticks open or its electronics fail.
- State shown in Home Assistant differs from the physical valve.
- A retry resets the hardware timer and extends the opening.
- A configuration error passes an unintended duration. This quirk converts an
  invalid duration to 1,800 seconds; invalid does **not** mean OFF.
- Custom-quirk API or upstream SWV behavior changes after an upgrade.
- A manually operated physical control bypasses the intended automation path.

The hardware timer reduces only some of these risks.

## Minimum operational safeguards

Before use:

1. Back up Home Assistant and record the previous quirk.
2. Test with the outlet positioned over a safe drain and with someone present.
3. Start with 10 seconds and physically time the actual closure.
4. Verify a normal ON closes at the configured 1,800-second fallback before
   relying on that behavior.
5. Retest after firmware, Home Assistant, ZHA, zigpy, coordinator, or quirk
   changes.

For ongoing use:

- Retain a Home Assistant delay and explicit OFF command.
- Confirm OFF state, retry once, and notify visibly on failure.
- Add an independent maximum-runtime watchdog and startup/reconnection checks.
- Use leak sensors and a separate upstream shutoff where damage is possible.
- Keep hoses, fittings, pressure ratings, drainage, and the valve mechanically
  maintained.
- Do not use unattended where a single failure can cause unacceptable harm.
- Do not assume the Home Assistant state proves physical water flow stopped.

## No safe default for every installation

The 1,800-second fallback is an opinionated maximum chosen for one installation.
It may be far too long for another property, flow rate, hose, room, or drainage
system. Review `DEFAULT_ON_TIME_SECONDS` before use; changing it requires a new
controlled hardware test.

Do not advertise this code as flood protection or as guaranteeing closure.
