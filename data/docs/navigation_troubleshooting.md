# Navigation Module — Troubleshooting Guide

## Overview

Provides GPS positioning and route calculation. Depends on a clear
satellite view; performance is heavily affected by physical environment
(tunnels, parking garages, dense urban canyons).

## Normal event sequence

`gps_search` → `gps_fix_acquired` → `route_calculated`.

## Error codes

### E-NAV-118 — GPS fix lost

**Cause:** Satellite signal was lost for longer than the module's grace
period (default 8s) before a fix could be re-acquired. Common in tunnels,
parking structures, and dense urban environments with tall buildings.

**Diagnosis:** Check the vehicle's last known location context if
available — GPS loss immediately after a `route_calculated` event in a
known tunnel/garage location is expected behavior, not a fault. Loss in
open terrain warrants antenna inspection.

**Resolution:** The module automatically resumes dead-reckoning using
wheel speed and gyroscope data until a fix is reacquired. No user action
needed for transient loss under ~60s.

## Related subsystems

Navigation does not depend on infotainment_boot reaching `ui_ready` to
begin acquiring GPS fix internally, but route rendering on-screen is
blocked until boot completes.
