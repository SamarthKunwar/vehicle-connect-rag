# Voice Assistant Module — Troubleshooting Guide

## Overview

Provides wake-word detection locally and routes recognized commands to a
cloud-based natural language understanding (NLU) service for processing.

## Normal event sequence

`wake_word_detected` → `cloud_request_sent` → `response_received`.

## Error codes

### E-VA-201 — Cloud NLU endpoint unreachable

**Cause:** The voice assistant successfully detected a wake word locally
but could not reach the backend NLU service — either due to no network
connectivity at all, or the NLU endpoint itself being degraded.

**Diagnosis:** Cross-reference against cloud_sync and wifi/cellular
connectivity events in the same session window. If wifi/cellular also
show connection failures at the same timestamp, this is a connectivity
issue, not an NLU service issue. If connectivity is healthy but E-VA-201
still occurs, escalate to the NLU service team.

**Resolution:** The assistant falls back to a small set of offline
commands (climate control, media playback) that don't require cloud NLU.
Full command support resumes once connectivity/service is restored.

## Related subsystems

Voice assistant's offline fallback command set is intentionally limited —
it does not attempt navigation or cloud_sync-dependent actions while in
fallback mode.
