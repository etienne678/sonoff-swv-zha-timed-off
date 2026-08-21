# Publishing checklist

This folder is designed to become the root of a separate GitHub repository.
Do not publish the parent Home Assistant configuration repository with it.

## Suggested repository metadata

- Name: `sonoff-swv-zha-timed-off`
- Description: `Experimental ZHA quirk for SONOFF SWV valves with mandatory and per-command hardware timed-off behavior.`
- Visibility for the first review: private or public draft, according to the
  maintainer's preference.
- Topics: `home-assistant`, `zha`, `zigbee`, `sonoff`, `swv`, `zha-quirks`,
  `irrigation`, `water-valve`, `home-automation`
- License: Apache-2.0

## Before creating the repository

1. Decide which public name should appear in copyright and release metadata.
2. Record the tested SWV firmware and coordinator in `COMPATIBILITY.md`.
3. Repeat the controlled 10-second test using the exact distributable quirk
   file in this folder, not a different deployed copy.
4. Run `ruff check .` and `pytest` with Python 3.12 and, if available, 3.13.
5. Review every file for private entity IDs, IEEE addresses, credentials,
   locations, screenshots, and logs.
6. Confirm `LICENSE`, `NOTICE`, and the upstream link are present.
7. Replace the changelog's `Unreleased` marker with the actual release date only
   when the release is made.

## Recommended GitHub settings

- Keep GitHub Actions enabled with read-only default permissions.
- Enable private vulnerability reporting.
- Require the CI workflow before merging to the default branch.
- Enable Dependabot alerts; review automatic dependency changes rather than
  merging them blindly because quirk APIs can change behavior.
- Disable force-pushes to the default branch after the first public release.
- Add a prominent repository description pointing to `SAFETY.md`.

## First release

Use a prerelease such as `v0.1.0-alpha.1`. Release notes should state:

- Exactly which hardware and software combination was tested.
- That the physical 10-second timer test succeeded on one installation.
- That normal ON is rewritten to a 1,800-second maximum.
- That invalid explicit values also fall back to 1,800 seconds.
- That `0x5011` is water-shortage auto-close, is unrelated to per-opening
  `on_time`, and is deliberately not exposed by this custom quirk.
- That software OFF commands and independent physical safeguards remain
  required.

Do not use phrases such as "flood-safe", "guaranteed shutoff", or "prevents
water damage".

## Upstream option

Before committing to a permanent fork, consider opening a design discussion in
`zigpy/zha-device-handlers`. The mandatory 30-minute rewrite is opinionated and
may need an opt-in mechanism before it is suitable upstream. A discussion can
also establish whether explicit `0x42` support belongs in the official SWV
handler.

Creating a remote repository, pushing files, or opening an upstream discussion
are external actions and should be performed only after explicit approval.
