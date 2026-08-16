# WiFi Module — Troubleshooting Guide

## Overview

The wifi module provides the vehicle's connection to home/office wireless
networks and mobile hotspots, primarily used for large data transfers
(map updates, software updates) where cellular backhaul is too slow or
metered.

## Normal event sequence

A healthy connection emits: `connect_attempt` → `dhcp_request` →
`authenticated` → (session) → `disconnect`.

## Error codes

### E-WIFI-301 — DHCP IP acquisition failure

**Cause:** The access point accepted the association but the DHCP server
did not return a lease within the timeout window. Common causes: DHCP
pool exhaustion on the access point, or the access point being configured
for static IP assignment only.

**Diagnosis:** Check whether `dhcp_request` appears in the session at all.
If it's missing entirely, the failure occurred at the association layer,
not DHCP — this points instead toward an E-WIFI-315 style rejection that
was misclassified.

**Resolution:** No automatic remediation beyond retry. If E-WIFI-301
recurs at the same physical location (e.g. a specific home garage),
recommend the user check their router's DHCP pool size.

### E-WIFI-315 — Access point authentication rejected

**Cause:** Incorrect stored credentials, or the access point has enabled
MAC address filtering that excludes the vehicle's WiFi module.

**Diagnosis:** This error occurs immediately after `connect_attempt`,
before any `dhcp_request` event — the rejection happens at the
association/auth layer.

**Resolution:** Prompt the user to re-enter WiFi credentials via the My
Porsche app or head unit settings. Not automatically retried, since
repeated failed auth attempts against some access points trigger
temporary lockouts.

## Related subsystems

cloud_sync prefers wifi over cellular when both are available due to lower
per-byte cost; a wifi failure mid-sync causes cloud_sync to fall back to
cellular rather than retry wifi immediately.
