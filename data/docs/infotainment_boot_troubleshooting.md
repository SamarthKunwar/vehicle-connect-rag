# Infotainment Boot — Troubleshooting Guide

## Overview

Covers the head unit's boot sequence from power-on to UI ready state. This
is the foundational module — bluetooth audio, navigation rendering, and
voice assistant UI all block on `ui_ready`.

## Normal event sequence

`power_on` → `kernel_init` → `services_started` → `ui_ready`.

## Error codes

### E-BOOT-050 — Boot watchdog timeout

**Cause:** The boot sequence exceeded the watchdog's maximum allowed
duration (default 30s). Usually caused by a hung service during
`kernel_init` or `services_started`, most often the map data indexing
service after a large map update was applied.

**Diagnosis:** Check the timestamp gap between `power_on` and the `error`
event — if it's close to exactly 30s, the watchdog fired as designed
rather than the system hanging indefinitely. Compare against recent
software/map update events if available.

**Resolution:** Automatic reboot is triggered. If E-BOOT-050 recurs across
consecutive boots, escalate — this indicates a genuinely hung service
rather than a one-off slow boot.

### E-BOOT-092 — Display controller self-test failure

**Cause:** The display controller's power-on self-test (POST) failed,
typically due to a display panel connection fault or a controller
firmware crash from the previous session.

**Diagnosis:** This error occurs very early in the sequence, often right
after `power_on` with no `kernel_init` event logged — self-test happens
before the main kernel initializes.

**Resolution:** A single occurrence is usually transient (cold-start
firmware hiccup). Recurring E-BOOT-092 across multiple power cycles
indicates a hardware fault requiring service center inspection of the
display panel connector.

## Related subsystems

No module can reach a fully "connected" user-visible state until
infotainment_boot reaches `ui_ready` — bluetooth, wifi, and cloud_sync can
all connect at the radio/network level before this, but their status will
not render until boot completes.
