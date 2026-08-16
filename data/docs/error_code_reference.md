# Connect Platform — Error Code Reference

This document is the canonical index of error codes emitted by the Connect
Platform modules. Each code links to the detailed troubleshooting guide for
its owning module.

| Error Code | Module | Severity | Summary | Guide |
|---|---|---|---|---|
| E-BT-104 | bluetooth | ERROR | Pairing handshake timeout | [Bluetooth Troubleshooting](bluetooth_troubleshooting.md) |
| E-BT-207 | bluetooth | ERROR | Signal lost during active session | [Bluetooth Troubleshooting](bluetooth_troubleshooting.md) |
| E-WIFI-301 | wifi | ERROR | DHCP IP acquisition failure | [WiFi Troubleshooting](wifi_troubleshooting.md) |
| E-WIFI-315 | wifi | ERROR | Access point authentication rejected | [WiFi Troubleshooting](wifi_troubleshooting.md) |
| E-BOOT-050 | infotainment_boot | ERROR | Boot watchdog timeout | [Infotainment Boot Troubleshooting](infotainment_boot_troubleshooting.md) |
| E-BOOT-092 | infotainment_boot | ERROR | Display controller self-test failure | [Infotainment Boot Troubleshooting](infotainment_boot_troubleshooting.md) |
| E-CLOUD-410 | cloud_sync | ERROR | Auth token expired | [Cloud Sync Troubleshooting](cloud_sync_troubleshooting.md) |
| E-CLOUD-423 | cloud_sync | ERROR | Backend returned 503 | [Cloud Sync Troubleshooting](cloud_sync_troubleshooting.md) |
| E-NAV-118 | navigation | ERROR | GPS fix lost | [Navigation Troubleshooting](navigation_troubleshooting.md) |
| E-VA-201 | voice_assistant | ERROR | Cloud NLU endpoint unreachable | [Voice Assistant Troubleshooting](voice_assistant_troubleshooting.md) |

## Severity levels

- **INFO** — normal operational event, no action required.
- **WARN** — recoverable condition, typically followed by an automatic
  reconnect attempt. Worth monitoring if frequency increases.
- **ERROR** — the module failed to complete its current operation. Always
  paired with a specific error code from the table above.

## Reading a Connect Platform session trace

Every connect/reconnect attempt is grouped under a `session_id`. A healthy
session shows a linear sequence of INFO events ending in a completed state
(e.g. `paired`, `ui_ready`, `sync_complete`). A failing session shows the
same sequence truncated by an ERROR event, optionally followed by a WARN
`reconnect` event if the module's retry logic engaged.
