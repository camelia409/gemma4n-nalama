"""
Nalam — Backend
Contract-compliant Flask API. Rule-based safety decisions; Gemma (via Google
AI Studio API) generates the warm Tamil + English text. Templates are kept as
an automatic fallback when the API is unavailable, rate-limited, or returns
malformed JSON, so the service stays clinically safe under failure.

Env vars:
    GEMINI_API_KEY    — Google AI Studio key. If absent, falls back to templates.
    GEMMA_MODEL       — model id, default "gemma-3-12b-it".
    FLASK_ENV         — set to "development" to also allow localhost CORS origins.
    EXTRA_CORS_ORIGIN — optional single extra allowed origin (e.g. custom domain).
    PORT              — server port (Render injects this), default 5000.
"""

import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS

# ----- Interaction logging ---------------------------------------------------
# Every /assess and /counselling call is appended to logs/interactions.jsonl
# (one JSON object per line), following the schema in docs/logging_schema.md.
# Salient fields (visit_day, weight, danger_flags, extra_concerns) are promoted
# to the top level for easy querying (Phase 4 trend tracking); the full
# request_payload is also retained so the eval set (Phase 1.4) can replay exact
# inputs. Logging must never break a request, so it is fully guarded.

LOG_SCHEMA_VERSION = "1.0"
APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")
LOG_DIR = os.environ.get("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "interactions.jsonl")

# Standard newborn checklist keys (everything else in danger_signs is free text)
STANDARD_BABY_FLAGS = {"feeding", "activity", "warmth", "breathing"}


def _coerce_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _coerce_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _extract_context(request_payload):
    """
    Pull the query-relevant fields out of an /assess or /counselling request.
    Returns (visit_day, baby_weight_kg, danger_flags, extra_concerns).
    Handles both payload shapes: /assess has `answers` (False = danger) and a
    top-level `extra_concerns`; /counselling has `danger_signs` (standard keys
    plus free-text extras mixed together).
    """
    baby = request_payload.get("baby") or {}
    visit_day = _coerce_int(baby.get("age_days"))
    baby_weight_kg = _coerce_float(baby.get("weight"))

    answers = request_payload.get("answers")
    if isinstance(answers, dict):
        danger_flags = [k for k, v in answers.items() if v is False]
    elif isinstance(request_payload.get("danger_signs"), list):
        danger_flags = [s for s in request_payload["danger_signs"] if s in STANDARD_BABY_FLAGS]
    else:
        danger_flags = []

    extra = request_payload.get("extra_concerns")
    if not isinstance(extra, list):
        ds = request_payload.get("danger_signs")
        extra = [s for s in ds if s not in STANDARD_BABY_FLAGS] if isinstance(ds, list) else None
    extra_concerns = extra if extra else None  # nullable

    return visit_day, baby_weight_kg, danger_flags, extra_concerns


def log_interaction(endpoint, request_payload, response_payload, gemma_prompt=None):
    """Append one schema-v1.0 interaction record (see docs/logging_schema.md)."""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        if not isinstance(request_payload, dict):
            request_payload = {}
        visit_day, baby_weight_kg, danger_flags, extra_concerns = _extract_context(request_payload)
        entry = {
            "schema_version": LOG_SCHEMA_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": str(uuid.uuid4()),
            "endpoint": endpoint,
            "visit_day": visit_day,
            "baby_weight_kg": baby_weight_kg,
            "danger_flags": danger_flags,
            "extra_concerns": extra_concerns,
            "consent_given": bool(request_payload.get("consent_given", False)),
            "gemma_prompt": gemma_prompt,
            "request_payload": request_payload,
            "response_payload": response_payload,
            "meta": {
                "app_version": APP_VERSION,
                "model": GEMMA_MODEL,
            },
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:  # never let logging break the response
        print(f"log_interaction failed: {e}", file=sys.stderr)


def _logged_response(endpoint, request_payload, response_payload, gemma_prompt=None):
    """
    Log the interaction ONLY if the caller gave explicit consent
    (consent_given: true in the request body), then return the JSON response.
    Without consent, nothing is written to disk.
    """
    if isinstance(request_payload, dict) and request_payload.get("consent_given") is True:
        log_interaction(endpoint, request_payload, response_payload, gemma_prompt)
    return jsonify(response_payload)

# ----- Google AI Studio client (lazy, optional) ------------------------------

_genai_client = None
_genai_unavailable = False
GEMMA_MODEL = os.environ.get("GEMMA_MODEL", "gemma-3-12b-it")


def _get_client():
    global _genai_client, _genai_unavailable
    if _genai_client is not None or _genai_unavailable:
        return _genai_client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        _genai_unavailable = True
        print("GEMINI_API_KEY not set — falling back to templates", file=sys.stderr)
        return None
    try:
        from google import genai
        _genai_client = genai.Client(api_key=api_key)
        print(f"Gemma client ready (model={GEMMA_MODEL})", file=sys.stderr)
        return _genai_client
    except Exception as e:
        _genai_unavailable = True
        print(f"Gemma client init failed: {e}", file=sys.stderr)
        return None


def _gemma_json(prompt: str, expect_keys: list[str]) -> dict | None:
    """
    Call Gemma asking for a strict JSON response. Returns dict on success,
    None on any failure — caller must have a template fallback.
    """
    client = _get_client()
    if client is None:
        return None
    try:
        resp = client.models.generate_content(
            model=GEMMA_MODEL,
            contents=prompt + "\n\nReturn ONLY the JSON object specified above. No prose, no markdown fences.",
            config={"temperature": 0.2},
        )
        text = (resp.text or "").strip()
        # Strip ```json fences if Gemma wrapped them
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            return None
        parsed = json.loads(m.group(0))
        if not all(k in parsed for k in expect_keys):
            return None
        return parsed
    except Exception as e:
        print(f"Gemma call failed: {e}", file=sys.stderr)
        return None


# ----- Input sanitisation ----------------------------------------------------
# Free-text fields flow straight into the LLM prompt, so they are stripped and
# length-capped before interpolation — this blunts prompt-injection and oversized
# payloads. Policy: TRUNCATE over-long values (don't reject); a wrong TYPE is a
# 400. Truncations are logged to stderr so injection attempts show up in Render.

MAX_EXTRA_CONCERNS_CHARS = 300
MAX_AUDIO_TEXT_CHARS = 500
MAX_WEIGHT_CHARS = 16  # birth_weight is a short numeric string like "2.8"


def _truncate_text(value, max_chars, endpoint, field):
    """Strip and cap a single string. Logs a warning if truncated. Non-str -> ''."""
    if not isinstance(value, str):
        return ""
    s = value.strip()
    if len(s) > max_chars:
        print(f"[truncate] endpoint={endpoint} field={field} "
              f"dropped={len(s) - max_chars} chars (cap={max_chars})", file=sys.stderr)
        s = s[:max_chars]
    return s


def _clean_concern_list(value, endpoint, field="extra_concerns",
                        cap=MAX_EXTRA_CONCERNS_CHARS):
    """Strip + cap each item of an already-list value; drop empties/non-strings."""
    if not value:
        return []
    return [s for s in (_truncate_text(i, cap, endpoint, field) for i in value) if s]


# ----- Prompt building blocks ------------------------------------------------
# Shared schema + few-shot fragments appended to every text-generation prompt to
# make output STRUCTURE and Tamil phrasing deterministic. The LLM only produces
# the bilingual TEXT; safety decisions (is_safe / danger_signs / action) are
# computed by rules and are NOT asked of the model — so the schema lists only
# the text keys the model must return.

_ASSESS_SCHEMA = (
    "\n\nOUTPUT SCHEMA — return EXACTLY this JSON object and nothing else "
    "(both keys required, both values plain strings, no extra keys, no markdown):\n"
    '{"tamil_message": "<Tamil text>", "english_message": "<English text>"}'
)

_ASSESS_FEWSHOT_REFER = (
    "\n\nEXAMPLE (a day-3 baby that is not feeding — a REFER_PHC danger case):\n"
    '{"tamil_message": "குழந்தை சரியாக பால் குடிக்கவில்லை. இது ஒரு அபாய அறிகுறி. '
    'உடனே குழந்தையை அருகிலுள்ள PHC-க்கு அழைத்துச் செல்லுங்கள் — தாமதிக்க வேண்டாம்.", '
    '"english_message": "The baby is not feeding well. This is a danger sign. '
    'Take the baby to the nearest PHC immediately — do not delay."}'
)

_COUNSELLING_SCHEMA = (
    "\n\nOUTPUT SCHEMA — return EXACTLY this JSON object and nothing else "
    "(both keys required, both values plain strings, no extra keys, no markdown):\n"
    '{"tamil_counselling_text": "<Tamil text>", "english_counselling_text": "<English text>"}'
)

_COUNSELLING_FEWSHOT_HOMECARE = (
    "\n\nEXAMPLE (a day-3 healthy baby with a safe mother — a HOME_CARE case):\n"
    '{"tamil_counselling_text": "குழந்தை நன்றாக இருக்கிறது. ஒவ்வொரு 2 மணி நேரத்திற்கும் '
    'தாய்ப்பால் மட்டும் கொடுங்கள். தொப்புள் கொடியை சுத்தமாகவும் உலர்வாகவும் வைத்திருங்கள். '
    'குழந்தையை நன்கு போர்த்தி வெதுவெதுப்பாக வைத்திருங்கள்.", '
    '"english_counselling_text": "The baby is doing well. Give only breast milk every '
    'two hours. Keep the umbilical cord clean and dry. Keep the baby well wrapped and warm."}'
)


# ----- Referral safety guardrail ---------------------------------------------
# For danger cases, the counselling text MUST tell the worker to seek care.
# If the generated English text contains none of these markers, it is rejected
# and replaced with a hardcoded safe-fallback referral. Server-side, never
# trusting the model or the frontend for this.

REFERRAL_MARKERS = ["PHC", "108", "refer", "hospital", "doctor", "emergency"]

# Hardcoded clinically-safe fallback used when generated text fails the check.
# Contains "PHC" and "108" so the replacement itself passes the marker check.
GUARDRAIL_FALLBACK_TAMIL = (
    "இந்த நிலைக்கு மருத்துவ கவனிப்பு தேவை. தாயையும் குழந்தையையும் உடனே "
    "அருகிலுள்ள PHC (ஆரம்ப சுகாதார நிலையம்) க்கு அழைத்துச் செல்லுங்கள். தாமதிக்க வேண்டாம். "
    "தேவைப்பட்டால் 108 ஆம்புலன்ஸை அழைக்கவும்."
)
GUARDRAIL_FALLBACK_ENGLISH = (
    "This case needs medical attention. Take the mother and baby to the nearest "
    "PHC (Primary Health Centre) now. Do not delay. Call 108 for an ambulance if needed."
)


def _referral_guardrail(response_payload, danger_flags, endpoint="counselling"):
    """
    Danger-case safety net: ensure the counselling text actually instructs the
    worker to seek care. If english_counselling_text contains no referral marker,
    log a [GUARDRAIL] warning and replace BOTH the Tamil and English text with the
    hardcoded safe-fallback referral. Returns the (possibly modified) payload.
    Call this ONLY for danger cases (action != HOME_CARE).
    """
    english = (response_payload.get("english_counselling_text") or "")
    english_lc = english.lower()
    if any(marker.lower() in english_lc for marker in REFERRAL_MARKERS):
        return response_payload  # at least one referral marker present -> OK

    print(
        f"[GUARDRAIL] endpoint={endpoint} danger_flags={danger_flags} "
        f"missing_referral_marker offending_text={english[:80]!r}",
        file=sys.stderr,
    )
    response_payload["tamil_counselling_text"] = GUARDRAIL_FALLBACK_TAMIL
    response_payload["english_counselling_text"] = GUARDRAIL_FALLBACK_ENGLISH
    return response_payload


# ----- Flask app -------------------------------------------------------------

app = Flask(__name__)

# CORS: explicit allowlist (no wildcard). The production Vercel frontend is
# always allowed; localhost dev origins are added ONLY when FLASK_ENV is set to
# "development". An optional EXTRA_CORS_ORIGIN env var allows one additional
# origin (e.g. a custom domain or preview deploy) without a code change.
PROD_ORIGIN = "https://gemma4n-nalama.vercel.app"
DEV_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]

_is_dev = os.environ.get("FLASK_ENV", "").lower() == "development"
ALLOWED_ORIGINS = [PROD_ORIGIN]
if _is_dev:
    ALLOWED_ORIGINS += DEV_ORIGINS
_extra_origin = os.environ.get("EXTRA_CORS_ORIGIN", "").strip()
if _extra_origin and _extra_origin != "*":
    ALLOWED_ORIGINS.append(_extra_origin)

CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})
print(f"CORS allowed origins ({'development' if _is_dev else 'production'}): {ALLOWED_ORIGINS}", file=sys.stderr)


# ----- Tamil/English copy banks (fallback when Gemma unavailable) -----------

_VISIT_TAMIL = {
    1:  "தாய்ப்பால் ஆரம்பித்து கொடுக்கவும். தாய்-குழந்தை தோல் தொடர்பு (skin-to-skin) வைத்துக்கொள்ளவும். குழந்தைக்கு குளியல் இன்னும் வேண்டாம். கொலொஸ்ட்ரம் (மஞ்சள் பால்) கட்டாயம் கொடுக்கவும்.",
    3:  "ஒவ்வொரு 2 மணி நேரத்திற்கும் தாய்ப்பால் மட்டும் கொடுங்கள். கொடியில் வீக்கம், சீழ், அல்லது நாற்றம் உள்ளதா என பாருங்கள். குழந்தையை நன்கு போர்த்தி வைத்திருங்கள்.",
    7:  "மஞ்சள் காமாலை அறிகுறி உள்ளதா என கண் மற்றும் தோலை பாருங்கள். குழந்தை நாளுக்கு 8 முறையாவது பால் குடிக்க வேண்டும். கொடி இப்போது விழுந்திருக்க வேண்டும்.",
    14: "BCG, OPV தடுப்பூசி போடப்பட்டதா என உறுதிசெய்யவும். குழந்தையின் எடை சரிபார்க்கவும். தாய் தனது மன நிலையை கவனிக்கவும்.",
    21: "தாய்ப்பால் மட்டும் தொடரவும். குழந்தை இப்போது சிரிக்க தொடங்கும். தாய் சத்தான உணவு உண்ணவும்.",
    28: "ஒரு மாத தடுப்பூசி நேரம் — PHC-க்கு செல்லுங்கள். குழந்தையின் எடை சரிபார்க்கவும். 6 மாதம் வரை தாய்ப்பால் மட்டும்தான்.",
    42: "இது கடைசி HBNC வருகை. அனைத்து தடுப்பூசிகளும் முடிந்துவிட்டதா என உறுதிசெய்யவும். தாய்க்கு குடும்ப கட்டுப்பாடு ஆலோசனை அளிக்கவும்.",
}
_VISIT_ENGLISH = {
    1:  "Initiate breastfeeding now. Keep mother and baby in skin-to-skin contact. No bath yet. Colostrum (yellow milk) is essential.",
    3:  "Exclusive breastfeeding every 2 hours. Check the cord for swelling, pus, or smell. Keep baby well wrapped.",
    7:  "Check eyes and skin for jaundice. Baby should be feeding at least 8 times a day. The cord should have fallen off by now.",
    14: "Confirm BCG and OPV are done. Check baby's weight. Watch the mother's mood — flag fatigue or tearfulness.",
    21: "Continue exclusive breastfeeding. Baby starts social smiling now. Mother needs nourishing food.",
    28: "One-month immunization is due at the PHC. Check baby's weight. Exclusive breastfeeding until 6 months.",
    42: "Final HBNC visit. Confirm all immunizations are complete. Counsel the mother on family planning.",
}
_DANGER_SIGN_TAMIL = {
    "feeding":   "குழந்தை சரியாக பால் குடிக்கவில்லை",
    "activity":  "குழந்தை சுறுசுறுப்பாக இல்லை",
    "warmth":    "குழந்தையின் உடல் குளிர்ச்சியாக உள்ளது",
    "breathing": "குழந்தை சரியாக மூச்சு விடவில்லை",
}
_DANGER_SIGN_ENGLISH = {
    "feeding":   "baby is not feeding properly",
    "activity":  "baby is not active",
    "warmth":    "baby's body is cold",
    "breathing": "baby is not breathing well",
}
_MOTHER_DANGER_TAMIL = {
    "bleeding":  "அதிக ரத்தப்போக்கு",
    "fever":     "காய்ச்சல்",
    "depressed": "தாயின் மன நிலை சரியில்லை",
}
_MOTHER_DANGER_ENGLISH = {
    "bleeding":  "heavy bleeding",
    "fever":     "fever",
    "depressed": "low mood / postpartum depression signs",
}


def _closest_visit_day(visit_day):
    days = list(_VISIT_TAMIL.keys())
    try:
        d = int(visit_day)
    except (TypeError, ValueError):
        d = 3
    return min(days, key=lambda x: abs(x - d))


def _join_tamil(items):
    return " மற்றும் ".join(items) if len(items) > 1 else (items[0] if items else "")


# ----- /health ---------------------------------------------------------------

@app.route('/health', methods=['GET'])
def health():
    using_gemma = _get_client() is not None
    return jsonify({
        "status": "Nalam API running",
        "model": (GEMMA_MODEL if using_gemma else "rules-only-fallback"),
    })


# ----- /assess ---------------------------------------------------------------

@app.route('/assess', methods=['POST'])
def assess():
    try:
        data = request.get_json(silent=True) or {}
        baby = data.get('baby') or {}
        answers = data.get('answers') or {}

        try:
            weight_kg = float(baby.get('weight') or 3.0)
        except (TypeError, ValueError):
            weight_kg = 3.0
        try:
            age_days = int(baby.get('age_days') or 3)
        except (TypeError, ValueError):
            age_days = 3
        premature = bool(baby.get('premature') or False)

        # Rule: True = normal, False = danger sign
        danger_signs_found = [k for k, v in answers.items() if v is False]
        # Free-text concerns the ASHA added beyond the 4 standard items
        raw_extra = data.get('extra_concerns')
        if raw_extra is not None and not isinstance(raw_extra, list):
            return jsonify({"error": "extra_concerns must be a list of strings"}), 400
        extra_concerns = _clean_concern_list(raw_extra, 'assess')
        # Any extra concern is treated as unsafe (conservative default)
        is_safe = (len(danger_signs_found) == 0) and (len(extra_concerns) == 0)
        # Surface extras in danger_signs so result + counselling see them
        danger_signs_found = danger_signs_found + extra_concerns

        gemma = None
        if is_safe:
            day = _closest_visit_day(age_days)
            risk = []
            if weight_kg < 2.0:
                risk.append("low birth weight")
            if premature:
                risk.append("premature baby")
            risk_text = ", ".join(risk) if risk else "no extra risk factors"
            prompt = (
                f"You are a Tamil HBNC assistant for ASHA workers in rural Tamil Nadu. "
                f"This is a day-{age_days} postnatal home visit. Baby weight is {weight_kg} kg. "
                f"Risk factors: {risk_text}. "
                f"Generate a short, warm counselling message in BOTH Tamil and English for the mother. "
                f"Focus on the right HBNC priorities for this visit day. "
                f"Tamil must be simple, informal, village-friendly. English must be plain prose "
                f"(no bullets, no markdown). Maximum 3 sentences each."
                f"{_ASSESS_SCHEMA}"
            )
            gemma = _gemma_json(prompt, ["tamil_message", "english_message"])
            if gemma:
                tamil = gemma["tamil_message"]
                english = gemma["english_message"]
            else:
                tamil = _VISIT_TAMIL[day]
                english = _VISIT_ENGLISH[day]
        else:
            std_signs = [s for s in danger_signs_found if s in _DANGER_SIGN_TAMIL]
            signs_t = _join_tamil([_DANGER_SIGN_TAMIL[s] for s in std_signs])
            signs_e = ", ".join([_DANGER_SIGN_ENGLISH[s] for s in std_signs]) if std_signs else "none from the standard checklist"
            extras_e = "; ".join(extra_concerns) if extra_concerns else ""
            extras_clause = (
                f" The ASHA also observed: {extras_e}. Incorporate these into the message." if extras_e else ""
            )
            prompt = (
                f"You are a Tamil HBNC assistant. A newborn on day {age_days} has these danger signs from "
                f"the standard checklist: {signs_e}.{extras_clause} "
                f"Generate a calm but urgent message in BOTH Tamil and English telling the mother what was "
                f"found and that the baby must be taken to the PHC immediately. Mention calling 108 if needed. "
                f"Tamil: simple, calm, no panic. English: plain prose, no markdown. Maximum 3 sentences each."
                f"{_ASSESS_SCHEMA}{_ASSESS_FEWSHOT_REFER}"
            )
            gemma = _gemma_json(prompt, ["tamil_message", "english_message"])
            if gemma:
                tamil = gemma["tamil_message"]
                english = gemma["english_message"]
            else:
                extras_t = (" மற்றும் ASHA கூறியது: " + "; ".join(extra_concerns) + ".") if extra_concerns else ""
                extras_eng = (f" Additional observations: {extras_e}." if extras_e else "")
                tamil = (
                    f"{signs_t or 'குழந்தையில் கவலை'}.{extras_t} இது அபாய அறிகுறி. "
                    "குழந்தையை உடனே PHC-க்கு கொண்டு செல்லுங்கள் — தாமதம் வேண்டாம். "
                    "தேவைப்பட்டால் 108 ஆம்புலன்ஸை அழைக்கவும்."
                )
                english = (
                    f"Danger signs detected ({signs_e}).{extras_eng} Refer the baby to the PHC "
                    "immediately — do not delay. Call 108 if needed."
                )

        return _logged_response('assess', data, {
            "is_safe": is_safe,
            "tamil_message": tamil,
            "english_message": english,
            "danger_signs": danger_signs_found,
        })
    except Exception as e:
        print(f"/assess fatal: {e}", file=sys.stderr)
        return _logged_response('assess', request.get_json(silent=True) or {}, {
            "is_safe": False,
            "tamil_message": "மதிப்பீடு தோல்வியடைந்தது. பாதுகாப்புக்காக குழந்தையை உடனே PHC-க்கு அனுப்பவும்.",
            "english_message": "Assessment failed. For safety, refer the baby to PHC immediately.",
            "danger_signs": ["unknown_risk_fallback"],
        })


# ----- /mother-health --------------------------------------------------------

@app.route('/mother-health', methods=['POST'])
def mother_health():
    try:
        data = request.get_json(silent=True) or {}
        answers = data.get('answers') or {}
        danger_signs_found = [k for k, v in answers.items() if v is True]
        raw_extra = data.get('extra_concerns')
        if raw_extra is not None and not isinstance(raw_extra, list):
            return jsonify({"error": "extra_concerns must be a list of strings"}), 400
        extra_concerns = _clean_concern_list(raw_extra, 'mother-health')
        is_safe = (len(danger_signs_found) == 0) and (len(extra_concerns) == 0)
        danger_signs_found = danger_signs_found + extra_concerns

        if is_safe:
            tamil = (
                "தாய்க்கு இப்போது எந்த அபாய அறிகுறியும் இல்லை. ஓய்வு எடுக்கவும், "
                "சத்தான உணவு உண்ணவும், அதிக நீர் குடிக்கவும்."
            )
            english = "No maternal danger signs detected. Encourage rest, nourishing food, and plenty of fluids."
        else:
            std_signs = [s for s in danger_signs_found if s in _MOTHER_DANGER_TAMIL]
            signs_e = ", ".join([_MOTHER_DANGER_ENGLISH[s] for s in std_signs]) if std_signs else "none from the standard checklist"
            extras_e = "; ".join(extra_concerns) if extra_concerns else ""
            extras_clause = (
                f" The ASHA also observed about the mother: {extras_e}. Incorporate these." if extras_e else ""
            )
            prompt = (
                f"You are a Tamil HBNC assistant. The mother (postpartum) shows these danger signs: "
                f"{signs_e}.{extras_clause} Generate a calm but urgent message in BOTH Tamil and English "
                f"telling the family that she needs immediate care at the PHC. Mention calling 108 if needed. "
                f"Tamil: simple, calm. English: plain prose, no markdown. Max 3 sentences each."
                f"{_ASSESS_SCHEMA}{_ASSESS_FEWSHOT_REFER}"
            )
            gemma = _gemma_json(prompt, ["tamil_message", "english_message"])
            if gemma:
                tamil = gemma["tamil_message"]
                english = gemma["english_message"]
            else:
                signs_t = _join_tamil([_MOTHER_DANGER_TAMIL[s] for s in std_signs]) or "கவலை அறிகுறிகள்"
                extras_t = (" ASHA கூறியது: " + "; ".join(extra_concerns) + ".") if extra_concerns else ""
                tamil = (
                    f"தாய்க்கு {signs_t} உள்ளது.{extras_t} இது அவசர நிலை. உடனே PHC-க்கு "
                    "அழைத்து செல்லவும். தேவைப்பட்டால் 108 அழைக்கவும்."
                )
                english = (
                    f"Maternal danger signs present ({signs_e}).{(' ' + extras_e + '.') if extras_e else ''} "
                    "This is urgent. Refer the mother to the PHC immediately. Call 108 if needed."
                )

        return jsonify({
            "is_safe": is_safe,
            "tamil_message": tamil,
            "english_message": english,
            "danger_signs": danger_signs_found,
        })
    except Exception as e:
        print(f"/mother-health fatal: {e}", file=sys.stderr)
        return jsonify({
            "is_safe": False,
            "tamil_message": "தாய் மதிப்பீடு தோல்வியடைந்தது. பாதுகாப்புக்காக PHC-க்கு அனுப்பவும்.",
            "english_message": "Mother-health assessment failed. For safety, refer to PHC.",
            "danger_signs": ["unknown_maternal_risk_fallback"],
        })


# ----- /audio-text -----------------------------------------------------------

@app.route('/audio-text', methods=['POST'])
def audio_text():
    """
    Frontend does Tamil STT in the browser; backend extracts which checklist
    items the mother's concern implies.
    """
    try:
        data = request.get_json(silent=True) or {}
        raw_text = data.get('text')
        if raw_text is not None and not isinstance(raw_text, str):
            return jsonify({"error": "text must be a string"}), 400
        text = _truncate_text(raw_text or "", MAX_AUDIO_TEXT_CHARS, 'audio-text', 'text')
        ctx = data.get('baby_context') or {}
        _vd = _coerce_int(ctx.get('visit_day'))
        visit_day = _vd if _vd is not None else 3
        birth_weight = _truncate_text(
            str(ctx.get('birth_weight', 'unknown')), MAX_WEIGHT_CHARS, 'audio-text', 'birth_weight')

        if not text:
            return jsonify({
                "transcription": "",
                "feeding_concern": False, "activity_concern": False,
                "warmth_concern": False, "breathing_concern": False,
                "urgency": "low", "confidence": "low",
                "reasoning": "No concern transcript provided.",
            })

        prompt = (
            f"You are a Tamil HBNC assistant. An ASHA worker captured the mother's concern about a "
            f"day-{visit_day}, {birth_weight} kg newborn:\n\n\"{text}\"\n\n"
            "Return JSON with keys feeding_concern, activity_concern, warmth_concern, "
            "breathing_concern (booleans), urgency ('low'|'high'), confidence ('low'|'medium'|'high'), "
            "reasoning (one short English sentence). Flag a concern only if the text clearly implies it."
        )
        parsed = _gemma_json(prompt, [
            "feeding_concern", "activity_concern", "warmth_concern", "breathing_concern",
            "urgency", "confidence", "reasoning"
        ])

        if parsed:
            return jsonify({
                "transcription": text,
                "feeding_concern":   bool(parsed.get("feeding_concern", False)),
                "activity_concern":  bool(parsed.get("activity_concern", False)),
                "warmth_concern":    bool(parsed.get("warmth_concern", False)),
                "breathing_concern": bool(parsed.get("breathing_concern", False)),
                "urgency":    parsed.get("urgency", "low"),
                "confidence": parsed.get("confidence", "medium"),
                "reasoning":  parsed.get("reasoning", ""),
            })

        # Keyword fallback
        tl = text.lower()
        feeding = any(k in tl for k in ['பால்', 'குடிக்க', 'feed', 'feeding', 'milk'])
        warmth = any(k in tl for k in ['குளிர்', 'ஜில்', 'cold', 'warm', 'shiver'])
        activity = any(k in tl for k in ['சோம்பேறி', 'தூக்க', 'அசையவில்லை', 'lethargic', 'sleepy', 'limp'])
        breathing = any(k in tl for k in ['மூச்சு', 'breath', 'choke', 'wheez'])
        any_concern = feeding or activity or warmth or breathing
        return jsonify({
            "transcription": text,
            "feeding_concern": feeding,
            "activity_concern": activity,
            "warmth_concern": warmth,
            "breathing_concern": breathing,
            "urgency": "high" if any_concern else "low",
            "confidence": "low",  # rule-based fallback, signal lower confidence
            "reasoning": "Keyword fallback used because Gemma was unavailable.",
        })
    except Exception as e:
        print(f"/audio-text fatal: {e}", file=sys.stderr)
        return jsonify({
            "transcription": "",
            "feeding_concern": True, "activity_concern": True,
            "warmth_concern": False, "breathing_concern": False,
            "urgency": "high", "confidence": "low",
            "reasoning": "Audio-text processing failed; conservative concern fallback applied.",
        })


# ----- /counselling ----------------------------------------------------------

@app.route('/counselling', methods=['POST'])
def counselling():
    try:
        data = request.get_json(silent=True) or {}
        baby = data.get('baby')
        danger_signs = data.get('danger_signs')
        is_safe = data.get('is_safe')
        mother_result = data.get('mother_result')

        if not isinstance(baby, dict) or not isinstance(danger_signs, list) \
                or not isinstance(is_safe, bool) or not isinstance(mother_result, dict):
            raise ValueError("invalid body")

        try:
            weight_kg = float(baby.get('weight') or 3.0)
        except (TypeError, ValueError):
            weight_kg = 3.0
        age_days = baby.get('age_days') if isinstance(baby.get('age_days'), int) else 3
        premature = bool(baby.get('premature') or False)
        mother_is_safe = bool(mother_result.get('is_safe'))

        if not is_safe and danger_signs:
            action = "REFER_PHC" if mother_is_safe else "REFER_108"
        elif not mother_is_safe:
            action = "REFER_PHC"
        else:
            action = "HOME_CARE"

        # Split standard danger signs from free-text extras in danger_signs.
        # Free-text extras flow into the prompt, so strip + cap them.
        std_baby_signs = [s for s in danger_signs if s in _DANGER_SIGN_ENGLISH]
        extra_baby = _clean_concern_list(
            [s for s in danger_signs if s not in _DANGER_SIGN_ENGLISH], 'counselling', 'danger_signs')
        signs_e = ", ".join([_DANGER_SIGN_ENGLISH[s] for s in std_baby_signs]) if std_baby_signs else "none"

        mother_danger_list = mother_result.get('danger_signs') or []
        mother_extras = _clean_concern_list(
            [s for s in mother_danger_list if s not in _MOTHER_DANGER_ENGLISH],
            'counselling', 'mother_danger_signs') if isinstance(mother_danger_list, list) else []
        mother_state = "safe" if mother_is_safe else "has danger signs"

        extras_clause = ""
        if extra_baby:
            extras_clause += f" The ASHA additionally observed about the baby: {'; '.join(extra_baby)}."
        if mother_extras:
            extras_clause += f" The ASHA additionally observed about the mother: {'; '.join(mother_extras)}."

        prompt = (
            f"You are a Tamil HBNC assistant. Generate a counselling script in BOTH Tamil and English. "
            f"Context: day-{age_days} postnatal visit, baby weight {weight_kg} kg, "
            f"premature={premature}, baby standard danger signs: {signs_e}, mother is {mother_state}."
            f"{extras_clause} "
            f"The clinical action already decided for this case is: {action} "
            f"(HOME_CARE=SAFE, REFER_PHC=refer to clinic, REFER_108=emergency ambulance). "
            f"Tailor the message to that action: HOME_CARE → reassuring care advice; "
            f"REFER_PHC → calm urgent referral to the PHC; REFER_108 → emergency, tell them to call 108. "
            f"If extras were observed, weave them into the counselling so the mother knows what to watch. "
            f"Do NOT contradict the decided action. "
            f"Tamil: simple, village-friendly. English: plain prose, no bullets or markdown. "
            f"Max 4 sentences each."
            f"{_COUNSELLING_SCHEMA}{_COUNSELLING_FEWSHOT_HOMECARE}"
        )
        gemma = _gemma_json(prompt, ["tamil_counselling_text", "english_counselling_text"])

        if gemma:
            result = {
                "tamil_counselling_text": gemma["tamil_counselling_text"],
                "english_counselling_text": gemma["english_counselling_text"],
                "action": action,
            }
        else:
            # Template fallback
            day = _closest_visit_day(age_days)
            if action == "HOME_CARE":
                tamil = f"{_VISIT_TAMIL[day]} அடுத்த வருகை வரை இதே போல் தொடரவும். தாய்க்கு ஓய்வு தேவை."
                english = f"{_VISIT_ENGLISH[day]} Continue this routine until the next visit. Mother needs rest."
            elif action == "REFER_PHC":
                signs_t = _join_tamil([_DANGER_SIGN_TAMIL.get(s, s) for s in danger_signs]) \
                    if danger_signs else "தாயின் நிலையில் சில அபாய அறிகுறிகள்"
                tamil = (
                    f"{signs_t} கண்டறியப்பட்டது. குழந்தையை"
                    f"{' மற்றும் தாயை' if not mother_is_safe else ''} உடனே PHC-க்கு கொண்டு செல்லுங்கள். "
                    "தாமதம் வேண்டாம். வழியில் தாய்ப்பால் தொடரவும்."
                )
                english = (
                    f"Found: {signs_e}. Refer the baby"
                    f"{' and mother' if not mother_is_safe else ''} to the PHC immediately. "
                    "Do not delay. Continue breastfeeding on the way."
                )
            else:  # REFER_108
                tamil = (
                    "இது அவசர நிலை. உடனே 108 ஆம்புலன்ஸை அழைக்கவும். தாயையும் குழந்தையையும் ஒன்றாக "
                    "ஆம்புலன்ஸில் கொண்டு செல்லவும். காத்திருக்கும் போது குழந்தையை வெதுவெதுப்பாக வைத்திருங்கள்."
                )
                english = (
                    "This is an emergency. Call 108 immediately. Transport mother and baby together. "
                    "While waiting, keep the baby warm and against the mother's chest."
                )
            result = {
                "tamil_counselling_text": tamil,
                "english_counselling_text": english,
                "action": action,
            }

        # SAFETY GUARDRAIL: a danger case (any non-HOME_CARE action) MUST contain
        # a referral instruction. This covers every is_safe=false case and also
        # the mother-only danger case (baby is_safe=true but mother unsafe), which
        # a literal is_safe check would miss. Replaces unsafe text in place.
        if action != "HOME_CARE":
            result = _referral_guardrail(result, danger_signs, endpoint='counselling')

        return _logged_response('counselling', data, result)
    except Exception as e:
        print(f"/counselling fatal: {e}", file=sys.stderr)
        return _logged_response('counselling', request.get_json(silent=True) or {}, {
            "tamil_counselling_text": "ஆலோசனை உருவாக்க முடியவில்லை. பாதுகாப்புக்காக உடனே 108 அழைக்கவும்.",
            "english_counselling_text": "Counselling generation failed. For safety, call 108 now.",
            "action": "REFER_108",
        })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Nalam backend running on {port}...", flush=True)
    app.run(host="0.0.0.0", port=port)
