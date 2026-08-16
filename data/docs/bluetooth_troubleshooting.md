# Bluetooth Module — Troubleshooting Guide

## Overview

The bluetooth module manages device pairing, hands-free calling, and audio
streaming between the head unit and paired smartphones. It is one of the
first modules initialized after cabin wake-up.

## Normal event sequence

A healthy pairing session emits, in order: `connect_attempt` → `handshake`
→ `paired`. Disconnection at end of drive emits `disconnect`.

## Error codes

### E-BT-104 — Pairing handshake timeout

**Cause:** The paired device did not respond to the handshake request
within the configured timeout window (default 15s, configurable up to 30s
in fleet settings). Most commonly caused by the phone's Bluetooth radio
being asleep, out of range, or already connected to a different accessory.

**Diagnosis:** Check whether the `error` event's preceding `handshake`
event has an unusually large time gap (>10s) from `connect_attempt`. A gap
under 1s followed immediately by timeout suggests a radio-level issue
rather than a protocol handshake issue.

**Resolution:** The module automatically retries via a `reconnect` event.
If repeated E-BT-104 occurs across many sessions for the same device, the
device's Bluetooth cache should be cleared and re-paired from scratch.

### E-BT-207 — Signal lost during active session

**Cause:** RF interference or the paired device moving out of effective
range mid-session. Distinct from E-BT-104 because it occurs after a
successful `handshake`, not during connection setup.

**Diagnosis:** If E-BT-207 co-occurs with other modules also reporting
signal issues in the same time window, suspect cabin-wide RF interference
(e.g. aftermarket electronics) rather than a bluetooth-specific fault.

**Resolution:** Automatic reconnect via the `reconnect` event is usually
sufficient. Persistent E-BT-207 in a stationary vehicle indicates a
hardware antenna fault requiring service inspection.

## Related subsystems

Bluetooth audio routing depends on the infotainment_boot module completing
`ui_ready` before audio streams can be established — a bluetooth pairing
that succeeds before boot completes will queue audio until boot finishes.
