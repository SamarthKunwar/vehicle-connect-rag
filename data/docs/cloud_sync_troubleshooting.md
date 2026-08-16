# Cloud Sync Module — Troubleshooting Guide

## Overview

Handles synchronization of vehicle telemetry, user preferences, and My
Porsche app state with backend cloud services. Runs opportunistically
whenever wifi or cellular connectivity is available.

## Normal event sequence

`connect_attempt` → `auth_handshake` → `sync_started` → `sync_complete`.

## Error codes

### E-CLOUD-410 — Auth token expired

**Cause:** The OAuth token used for backend authentication expired before
a scheduled refresh occurred. Usually happens after the vehicle has been
powered off for an extended period (multi-week parking) exceeding the
token refresh cycle.

**Diagnosis:** Occurs at the `auth_handshake` stage, before `sync_started`
— no partial sync data is at risk since the failure is pre-sync.

**Resolution:** Automatic token refresh is attempted via the backup
refresh token; if that also fails, the user must re-authenticate via the
My Porsche app.

### E-CLOUD-423 — Backend returned 503

**Cause:** The cloud backend service was temporarily unavailable —
typically during backend deployments or regional outages, not a
vehicle-side fault.

**Diagnosis:** If E-CLOUD-423 appears across many vehicles in the same
time window, this confirms a backend-side incident rather than a
per-vehicle issue. A single vehicle showing this once is not actionable.

**Resolution:** Exponential backoff retry is standard; no user action
required. Sustained failures beyond 30 minutes should be escalated to the
backend on-call team.

## Related subsystems

cloud_sync prefers wifi (see [WiFi Troubleshooting](wifi_troubleshooting.md))
over cellular for cost reasons, and defers non-urgent syncs entirely if
neither connection type is available rather than queuing indefinitely.
