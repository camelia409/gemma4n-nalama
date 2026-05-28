#!/usr/bin/env python3
"""
Run the Nalam eval set against the live API and score each case Y/N.

Usage:
    python run_eval.py                 # run against the default live API
    python run_eval.py --base-url URL  # run against a different backend
    python run_eval.py --dry-run       # validate eval_set.json structure only
    python run_eval.py --delay 4.5     # seconds between calls (Gemini free tier
                                        # is ~15 req/min, so keep >= 4s)

Outputs:
    results.json         per-case detail
    results_summary.md   human-readable summary

Scoring per case (all case-insensitive substring matching):
    action_match          expected normalized action == mapped API action
    must_contain_pass     every must_contain keyword present in the text
    must_not_contain_pass no must_not_contain keyword present
    overall               Y only if all three pass

Action mapping (normalized vocab = SAFE / REFER_PHC / REFER_EMERGENCY):
    /counselling : HOME_CARE->SAFE, REFER_PHC->REFER_PHC, REFER_108->REFER_EMERGENCY
    /assess, /mother-health : is_safe True->SAFE, False->REFER_PHC
        (these endpoints expose only is_safe; they CANNOT express emergency
         severity, so any case expecting REFER_EMERGENCY here will mismatch.
         That is a documented architectural limitation, not a script bug.)
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
EVAL_FILE = HERE / "eval_set.json"
RESULTS_JSON = HERE / "results.json"
RESULTS_MD = HERE / "results_summary.md"
DEFAULT_BASE_URL = "https://nalam-api-h62b.onrender.com"

# Cases the eval set documents as intentional clinical-vs-backend gaps.
KNOWN_INTENTIONAL = {
    "E1_vlbw_safe_signs", "E2_vlbw_premature", "E3_vlbw_cold",
    "B4_single_breathing", "J2_counselling_breathing_emergency",
}

VALID_ACTIONS = {"SAFE", "REFER_PHC", "REFER_EMERGENCY"}
VALID_ENDPOINTS = {"assess", "mother-health", "counselling"}

BUCKET_NAMES = {
    "A": "(a) all-clear safe", "B": "(b) single danger sign",
    "C": "(c) multiple danger signs", "D": "(d) premature baby",
    "E": "(e) very low weight <1.8kg", "F": "(f) late visit day",
    "G": "(g) extra_concerns free text", "H": "(h) mother danger / safe",
    "I": "(i) both mother+baby", "J": "(j) is_safe=false counselling",
    "K": "(k) counselling home-care safe",
}


def map_action(endpoint, response):
    """Map a live API response to the normalized action vocabulary."""
    if endpoint == "counselling":
        return {
            "HOME_CARE": "SAFE",
            "REFER_PHC": "REFER_PHC",
            "REFER_108": "REFER_EMERGENCY",
        }.get(response.get("action"), response.get("action"))
    is_safe = response.get("is_safe")
    if is_safe is True:
        return "SAFE"
    if is_safe is False:
        return "REFER_PHC"  # cannot express emergency severity at this endpoint
    return None


def text_blob(endpoint, response):
    """Concatenate the response's text fields for keyword scoring."""
    if endpoint == "counselling":
        keys = ("tamil_counselling_text", "english_counselling_text")
    else:
        keys = ("tamil_message", "english_message")
    return " ".join(str(response.get(k, "")) for k in keys)


def score_case(case, response):
    exp = case["expected"]
    blob_lc = text_blob(case["endpoint"], response).lower()

    action_got = map_action(case["endpoint"], response)
    action_match = action_got == exp["action"]

    mc_missing = [k for k in exp["must_contain"] if k.lower() not in blob_lc]
    must_contain_pass = not mc_missing

    mnc_present = [k for k in exp["must_not_contain"] if k.lower() in blob_lc]
    must_not_contain_pass = not mnc_present

    overall = action_match and must_contain_pass and must_not_contain_pass
    return {
        "action_expected": exp["action"],
        "action_got": action_got,
        "action_match": action_match,
        "must_contain_pass": must_contain_pass,
        "must_contain_missing": mc_missing,
        "must_not_contain_pass": must_not_contain_pass,
        "must_not_contain_present": mnc_present,
        "overall": overall,
    }


def call_api(base_url, case, timeout):
    """POST the case's request_payload; return (response_dict, error_or_None)."""
    url = base_url.rstrip("/") + "/" + case["endpoint"]
    body = json.dumps(case["request_payload"]).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "ngrok-skip-browser-warning": "true"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def validate_structure(cases):
    """Validate the eval set without hitting the API. Returns list of problems."""
    problems = []
    seen = set()
    for i, c in enumerate(cases):
        cid = c.get("case_id", f"<index {i}>")
        if cid in seen:
            problems.append(f"{cid}: duplicate case_id")
        seen.add(cid)
        for key in ("case_id", "description", "endpoint", "request_payload", "expected"):
            if key not in c:
                problems.append(f"{cid}: missing top-level key '{key}'")
        if c.get("endpoint") not in VALID_ENDPOINTS:
            problems.append(f"{cid}: invalid endpoint '{c.get('endpoint')}'")
        exp = c.get("expected", {})
        for key in ("action", "must_contain", "must_not_contain", "notes"):
            if key not in exp:
                problems.append(f"{cid}: expected missing '{key}'")
        if exp.get("action") not in VALID_ACTIONS:
            problems.append(f"{cid}: invalid action '{exp.get('action')}'")
        if not isinstance(exp.get("must_contain"), list):
            problems.append(f"{cid}: must_contain must be a list")
        if not isinstance(exp.get("must_not_contain"), list):
            problems.append(f"{cid}: must_not_contain must be a list")
    return problems


def wake_backend(base_url, timeout):
    """Ping /health to wake a sleeping free-tier instance before timing runs."""
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/health", timeout=timeout) as r:
            r.read()
        return True
    except Exception:
        return False


def write_summary(meta, results):
    by_bucket = defaultdict(list)
    for r in results:
        by_bucket[r["case_id"][0]].append(r)

    total = len(results)
    passed = sum(1 for r in results if r["score"]["overall"])
    known = [r for r in results if r["case_id"] in KNOWN_INTENTIONAL]
    real = [r for r in results if r["case_id"] not in KNOWN_INTENTIONAL]
    real_pass = sum(1 for r in real if r["score"]["overall"])

    lines = []
    lines.append("# Nalam Eval Results\n")
    lines.append(f"- Run at: {meta['run_at']}")
    lines.append(f"- Base URL: {meta['base_url']}")
    lines.append(f"- Total cases: {total}\n")

    lines.append("## Pass rates\n")
    lines.append(f"- **Raw overall:** {passed}/{total} = {passed/total*100:.1f}%")
    lines.append(
        f"- **Adjusted (excluding {len(known)} known intentional failures):** "
        f"{real_pass}/{len(real)} = {real_pass/len(real)*100:.1f}%\n"
    )

    lines.append("## Pass rate by scenario bucket\n")
    lines.append("| Bucket | Pass / Total |")
    lines.append("|---|---|")
    for b in sorted(by_bucket):
        rs = by_bucket[b]
        p = sum(1 for r in rs if r["score"]["overall"])
        lines.append(f"| {BUCKET_NAMES.get(b, b)} | {p}/{len(rs)} |")
    lines.append("")

    def fmt_fail(r):
        s = r["score"]
        checks = []
        if not s["action_match"]:
            checks.append(f"action (expected {s['action_expected']}, got {s['action_got']})")
        if not s["must_contain_pass"]:
            checks.append(f"must_contain missing {s['must_contain_missing']}")
        if not s["must_not_contain_pass"]:
            checks.append(f"must_not_contain present {s['must_not_contain_present']}")
        if r.get("error"):
            checks.append(f"API error: {r['error']}")
        txt = (r.get("response_text") or "").replace("\n", " ")[:200]
        return (f"- **{r['case_id']}** — failed: {'; '.join(checks)}\n"
                f"  - response: _{txt}_")

    known_fails = [r for r in known if not r["score"]["overall"]]
    lines.append(f"## Known intentional failures ({len(known_fails)}/{len(known)} failed as expected)\n")
    lines.append("These encode documented clinical-vs-backend gaps; excluded from the adjusted rate.\n")
    for r in known:
        status = "FAILED (expected)" if not r["score"]["overall"] else "PASSED (gap not triggered)"
        lines.append(f"- {r['case_id']}: {status}")
    lines.append("")

    real_fails = [r for r in real if not r["score"]["overall"]]
    lines.append(f"## Unexpected failures ({len(real_fails)}) — need attention\n")
    if not real_fails:
        lines.append("_None._\n")
    else:
        for r in real_fails:
            lines.append(fmt_fail(r))
    lines.append("")

    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Run the Nalam eval set against the API.")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--dry-run", action="store_true", help="validate structure only")
    ap.add_argument("--delay", type=float, default=4.5, help="seconds between calls")
    ap.add_argument("--timeout", type=float, default=90.0, help="per-request timeout")
    args = ap.parse_args()

    cases = json.loads(EVAL_FILE.read_text(encoding="utf-8"))

    problems = validate_structure(cases)
    if args.dry_run:
        print(f"Validated {len(cases)} cases.")
        if problems:
            print(f"{len(problems)} structural problem(s):")
            for p in problems:
                print("  -", p)
            sys.exit(1)
        print("Structure OK. No problems found.")
        return
    if problems:
        print("Refusing to run — structural problems:", file=sys.stderr)
        for p in problems:
            print("  -", p, file=sys.stderr)
        sys.exit(1)

    print(f"Waking backend at {args.base_url} ...", file=sys.stderr)
    wake_backend(args.base_url, args.timeout)

    results = []
    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] {case['case_id']} ...", file=sys.stderr)
        response, error = call_api(args.base_url, case, args.timeout)
        if error:
            score = {
                "action_expected": case["expected"]["action"], "action_got": None,
                "action_match": False, "must_contain_pass": False,
                "must_contain_missing": case["expected"]["must_contain"],
                "must_not_contain_pass": False, "must_not_contain_present": [],
                "overall": False,
            }
            resp_text = ""
        else:
            score = score_case(case, response)
            resp_text = text_blob(case["endpoint"], response)
        results.append({
            "case_id": case["case_id"], "endpoint": case["endpoint"],
            "description": case["description"], "response": response,
            "response_text": resp_text, "error": error, "score": score,
        })
        if i < len(cases):
            time.sleep(args.delay)

    meta = {"run_at": datetime.now(timezone.utc).isoformat(), "base_url": args.base_url}
    RESULTS_JSON.write_text(json.dumps({"meta": meta, "results": results},
                                       ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary(meta, results)

    total = len(results)
    passed = sum(1 for r in results if r["score"]["overall"])
    real = [r for r in results if r["case_id"] not in KNOWN_INTENTIONAL]
    real_pass = sum(1 for r in real if r["score"]["overall"])
    print(f"\nRaw: {passed}/{total} ({passed/total*100:.1f}%) | "
          f"Adjusted: {real_pass}/{len(real)} ({real_pass/len(real)*100:.1f}%)", file=sys.stderr)
    print(f"Wrote {RESULTS_JSON.name} and {RESULTS_MD.name}", file=sys.stderr)


if __name__ == "__main__":
    main()
