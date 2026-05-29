import json
import requests


BASE_URL = "http://127.0.0.1:5000"


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def run_test(name, method, path, payload, check_fn):
    url = f"{BASE_URL}{path}"
    print(f"\n=== {name} ===")
    print("SENT_JSON:", dump(payload) if payload is not None else None)

    resp = requests.request(method, url, json=payload, timeout=30)
    # Show raw received JSON exactly as Flask serializes (response.text).
    print("RECEIVED_RAW:", resp.text)
    try:
        received = resp.json()
    except Exception:
        received = None

    ok, reason = check_fn(received)
    print("PASS" if ok else "FAIL", "-", reason)


def main():
    # Test 3 — /assess danger
    run_test(
        "Test 3 — /assess danger",
        "POST",
        "/assess",
        {
            "baby": {"name": "Baby Priya", "weight": "2.8", "age_days": 3, "premature": False},
            "answers": {"feeding": False, "activity": True, "warmth": False, "breathing": True},
        },
        lambda received: (
            received is not None
            and received.get("is_safe") is False
            and "feeding" in received.get("danger_signs", [])
            and "warmth" in received.get("danger_signs", []),
            "Expected is_safe:false and danger_signs contain feeding + warmth"
            if received is not None
            else "Response was not valid JSON",
        ),
    )

    # Test 5 — /mother-health danger
    run_test(
        "Test 5 — /mother-health danger",
        "POST",
        "/mother-health",
        {"answers": {"bleeding": True, "fever": False, "depressed": True}},
        lambda received: (
            received is not None
            and received.get("is_safe") is False
            and "bleeding" in received.get("danger_signs", [])
            and "depressed" in received.get("danger_signs", []),
            "Expected is_safe:false and danger_signs contain bleeding + depressed"
            if received is not None
            else "Response was not valid JSON",
        ),
    )

    # Test 6 — /audio-text with keywords
    run_test(
        "Test 6 — /audio-text keywords",
        "POST",
        "/audio-text",
        {
            "text": "Baby has feeding problem and seems warm",
            "baby_context": {"visit_day": 3, "birth_weight": "2.8"},
        },
        lambda received: (
            received is not None
            and received.get("feeding_concern") is True
            and received.get("warmth_concern") is True
            and "day-3" in (received.get("reasoning") or "")
            and "2.8" in (received.get("reasoning") or ""),
            "Expected feeding_concern:true, warmth_concern:true, reasoning contains day-3 and 2.8"
            if received is not None
            else "Response was not valid JSON",
        ),
    )

    # Test 7 — /audio-text no keywords
    run_test(
        "Test 7 — /audio-text no keywords",
        "POST",
        "/audio-text",
        {
            "text": "Baby seems okay now",
            "baby_context": {"visit_day": 7, "birth_weight": "2.4"},
        },
        lambda received: (
            received is not None
            and received.get("feeding_concern") is False
            and received.get("activity_concern") is False
            and received.get("warmth_concern") is False
            and received.get("breathing_concern") is False
            and "day-7" in (received.get("reasoning") or "")
            and "2.4" in (received.get("reasoning") or ""),
            "Expected all concerns false and reasoning contains day-7 and 2.4"
            if received is not None
            else "Response was not valid JSON",
        ),
    )

    # Test 8 — /counselling HOME_CARE
    run_test(
        "Test 8 — /counselling HOME_CARE",
        "POST",
        "/counselling",
        {
            "baby": {"weight": "2.8", "age_days": 3, "premature": False},
            "danger_signs": [],
            "is_safe": True,
            "mother_result": {"is_safe": True, "danger_signs": [], "tamil_message": "ok", "english_message": "ok"},
        },
        lambda received: (
            received is not None and received.get("action") == "HOME_CARE",
            'Expected action="HOME_CARE"' if received is not None else "Response was not valid JSON",
        ),
    )


if __name__ == "__main__":
    main()

