"""Generates synthetic connect/infotainment event logs.

Simulates decoded CAN-derived events (as if a DBC file already translated
raw arbitration IDs into named modules/events) for modules like bluetooth,
wifi, infotainment boot, cloud sync, navigation, and voice assistant.
"""
import csv
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

MODULES = ["bluetooth", "wifi", "infotainment_boot", "cloud_sync", "navigation", "voice_assistant"]

# error_code -> (module, message template)
ERROR_CODES = {
    "E-BT-104": ("bluetooth", "Bluetooth pairing handshake timed out after {n}s"),
    "E-BT-207": ("bluetooth", "Bluetooth signal lost during active session"),
    "E-WIFI-301": ("wifi", "WiFi module failed to acquire IP address via DHCP"),
    "E-WIFI-315": ("wifi", "WiFi authentication rejected by access point"),
    "E-BOOT-050": ("infotainment_boot", "Infotainment head unit boot exceeded {n}s watchdog limit"),
    "E-BOOT-092": ("infotainment_boot", "Display controller failed self-test on boot"),
    "E-CLOUD-410": ("cloud_sync", "Cloud sync rejected: authentication token expired"),
    "E-CLOUD-423": ("cloud_sync", "Cloud sync failed: backend returned 503"),
    "E-NAV-118": ("navigation", "Navigation module lost GPS fix for {n}s"),
    "E-VA-201": ("voice_assistant", "Voice assistant failed to reach cloud NLU endpoint"),
}

NORMAL_EVENTS = {
    "bluetooth": ["connect_attempt", "handshake", "paired", "disconnect"],
    "wifi": ["connect_attempt", "dhcp_request", "authenticated", "disconnect"],
    "infotainment_boot": ["power_on", "kernel_init", "services_started", "ui_ready"],
    "cloud_sync": ["connect_attempt", "auth_handshake", "sync_started", "sync_complete"],
    "navigation": ["gps_search", "gps_fix_acquired", "route_calculated"],
    "voice_assistant": ["wake_word_detected", "cloud_request_sent", "response_received"],
}


def make_session(start_time, module, will_error):
    session_id = str(uuid.uuid4())[:8]
    events = []
    t = start_time
    sequence = NORMAL_EVENTS[module][:]

    if will_error:
        module_error_codes = [
            (code, template) for code, (err_module, template) in ERROR_CODES.items()
            if err_module == module
        ]
        error_code, template = random.choice(module_error_codes)
        insert_at = random.randint(1, len(sequence))
        sequence = sequence[:insert_at]
    else:
        error_code = None

    for event_type in sequence:
        t += timedelta(milliseconds=random.randint(50, 800))
        events.append({
            "timestamp": t.isoformat(),
            "session_id": session_id,
            "module": module,
            "event_type": event_type,
            "severity": "INFO",
            "error_code": None,
            "message": f"{module} {event_type.replace('_', ' ')}",
        })

    if will_error:
        t += timedelta(milliseconds=random.randint(100, 1500))
        n = random.choice([5, 8, 10, 15, 30])
        events.append({
            "timestamp": t.isoformat(),
            "session_id": session_id,
            "module": module,
            "event_type": "error",
            "severity": "ERROR",
            "error_code": error_code,
            "message": template.format(n=n),
        })
        # ~60% of errors are followed by a reconnect attempt
        if random.random() < 0.6:
            t += timedelta(milliseconds=random.randint(500, 3000))
            events.append({
                "timestamp": t.isoformat(),
                "session_id": session_id,
                "module": module,
                "event_type": "reconnect",
                "severity": "WARN",
                "error_code": None,
                "message": f"{module} attempting reconnect after error {error_code}",
            })

    return events, t


def generate(num_sessions=400, error_rate=0.18, out_dir=Path("data/logs")):
    out_dir.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 8, 1, 6, 0, 0)
    all_events = []
    t = start

    for _ in range(num_sessions):
        t += timedelta(seconds=random.randint(2, 120))
        module = random.choice(MODULES)
        will_error = random.random() < error_rate
        events, t = make_session(t, module, will_error)
        all_events.extend(events)

    all_events.sort(key=lambda e: e["timestamp"])

    csv_path = out_dir / "connect_events.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_events[0].keys()))
        writer.writeheader()
        writer.writerows(all_events)

    jsonl_path = out_dir / "connect_events.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for e in all_events:
            f.write(json.dumps(e) + "\n")

    print(f"Generated {len(all_events)} events across {num_sessions} sessions")
    print(f"  -> {csv_path}")
    print(f"  -> {jsonl_path}")
    error_count = sum(1 for e in all_events if e["severity"] == "ERROR")
    print(f"  {error_count} error events ({error_count / num_sessions:.1%} of sessions)")


if __name__ == "__main__":
    generate()
