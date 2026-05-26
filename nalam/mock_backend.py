"""
Nalam — Backend
Contract-compliant Flask API. Rule-based safety decisions; Gemma (via Google
AI Studio API) generates the warm Tamil + English text. Templates are kept as
an automatic fallback when the API is unavailable, rate-limited, or returns
malformed JSON, so the service stays clinically safe under failure.

Env vars:
    GEMINI_API_KEY   — Google AI Studio key. If absent, falls back to templates.
    GEMMA_MODEL      — model id, default "gemma-3-12b-it".
    FRONTEND_ORIGIN  — CORS origin, default "*".
    PORT             — server port (Render injects this), default 5000.
"""

import json
import os
import re
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS

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
            contents=prompt + "\n\nRespond with strict JSON only. No prose.",
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


# ----- Flask app -------------------------------------------------------------

app = Flask(__name__)
_frontend_origin = os.environ.get("FRONTEND_ORIGIN", "*")
CORS(app, resources={r"/*": {"origins": _frontend_origin}})


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
        is_safe = len(danger_signs_found) == 0

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
                f"(no bullets, no markdown). Maximum 3 sentences each. "
                f"Return JSON with keys: tamil_message, english_message."
            )
            gemma = _gemma_json(prompt, ["tamil_message", "english_message"])
            if gemma:
                tamil = gemma["tamil_message"]
                english = gemma["english_message"]
            else:
                tamil = _VISIT_TAMIL[day]
                english = _VISIT_ENGLISH[day]
        else:
            signs_t = _join_tamil([_DANGER_SIGN_TAMIL.get(s, s) for s in danger_signs_found])
            signs_e = ", ".join([_DANGER_SIGN_ENGLISH.get(s, s) for s in danger_signs_found])
            prompt = (
                f"You are a Tamil HBNC assistant. A newborn on day {age_days} has these danger signs: "
                f"{signs_e}. Generate a calm but urgent message in BOTH Tamil and English telling the "
                f"mother what was found and that the baby must be taken to the PHC immediately. "
                f"Mention calling 108 if needed. Tamil: simple, calm, no panic. English: plain prose, "
                f"no markdown. Maximum 3 sentences each. "
                f"Return JSON with keys: tamil_message, english_message."
            )
            gemma = _gemma_json(prompt, ["tamil_message", "english_message"])
            if gemma:
                tamil = gemma["tamil_message"]
                english = gemma["english_message"]
            else:
                tamil = (
                    f"{signs_t}. இது அபாய அறிகுறி. குழந்தையை உடனே PHC-க்கு கொண்டு செல்லுங்கள் — "
                    "தாமதம் வேண்டாம். தேவைப்பட்டால் 108 ஆம்புலன்ஸை அழைக்கவும்."
                )
                english = (
                    f"Danger signs detected ({signs_e}). Refer the baby to the PHC immediately — "
                    "do not delay. Call 108 if needed."
                )

        return jsonify({
            "is_safe": is_safe,
            "tamil_message": tamil,
            "english_message": english,
            "danger_signs": danger_signs_found,
        })
    except Exception as e:
        print(f"/assess fatal: {e}", file=sys.stderr)
        return jsonify({
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
        is_safe = len(danger_signs_found) == 0

        if is_safe:
            tamil = (
                "தாய்க்கு இப்போது எந்த அபாய அறிகுறியும் இல்லை. ஓய்வு எடுக்கவும், "
                "சத்தான உணவு உண்ணவும், அதிக நீர் குடிக்கவும்."
            )
            english = "No maternal danger signs detected. Encourage rest, nourishing food, and plenty of fluids."
        else:
            signs_e = ", ".join([_MOTHER_DANGER_ENGLISH.get(s, s) for s in danger_signs_found])
            prompt = (
                f"You are a Tamil HBNC assistant. The mother (postpartum) shows these danger signs: "
                f"{signs_e}. Generate a calm but urgent message in BOTH Tamil and English telling the "
                f"family that she needs immediate care at the PHC. Mention calling 108 if needed. "
                f"Tamil: simple, calm. English: plain prose, no markdown. Max 3 sentences each. "
                f"Return JSON with keys: tamil_message, english_message."
            )
            gemma = _gemma_json(prompt, ["tamil_message", "english_message"])
            if gemma:
                tamil = gemma["tamil_message"]
                english = gemma["english_message"]
            else:
                signs_t = _join_tamil([_MOTHER_DANGER_TAMIL.get(s, s) for s in danger_signs_found])
                tamil = (
                    f"தாய்க்கு {signs_t} உள்ளது. இது அவசர நிலை. உடனே PHC-க்கு "
                    "அழைத்து செல்லவும். தேவைப்பட்டால் 108 அழைக்கவும்."
                )
                english = (
                    f"Maternal danger signs present ({signs_e}). This is urgent. "
                    "Refer the mother to the PHC immediately. Call 108 if needed."
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
        text = (data.get('text') or '').strip()
        ctx = data.get('baby_context') or {}
        visit_day = ctx.get('visit_day', 3)
        birth_weight = ctx.get('birth_weight', 'unknown')

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

        signs_e = ", ".join([_DANGER_SIGN_ENGLISH.get(s, s) for s in danger_signs]) if danger_signs else "none"
        mother_state = "safe" if mother_is_safe else "has danger signs"

        prompt = (
            f"You are a Tamil HBNC assistant. Generate a counselling script in BOTH Tamil and English. "
            f"Context: day-{age_days} postnatal visit, baby weight {weight_kg} kg, "
            f"premature={premature}, baby danger signs: {signs_e}, mother is {mother_state}. "
            f"The clinical action taken is: {action}. "
            f"Tailor the message to the action: HOME_CARE → reassuring care advice; "
            f"REFER_PHC → calm urgent referral; REFER_108 → emergency, call ambulance. "
            f"Tamil: simple, village-friendly. English: plain prose, no bullets or markdown. "
            f"Max 4 sentences each. "
            f"Return JSON with keys: tamil_counselling_text, english_counselling_text."
        )
        gemma = _gemma_json(prompt, ["tamil_counselling_text", "english_counselling_text"])

        if gemma:
            return jsonify({
                "tamil_counselling_text": gemma["tamil_counselling_text"],
                "english_counselling_text": gemma["english_counselling_text"],
                "action": action,
            })

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

        return jsonify({
            "tamil_counselling_text": tamil,
            "english_counselling_text": english,
            "action": action,
        })
    except Exception as e:
        print(f"/counselling fatal: {e}", file=sys.stderr)
        return jsonify({
            "tamil_counselling_text": "ஆலோசனை உருவாக்க முடியவில்லை. பாதுகாப்புக்காக உடனே 108 அழைக்கவும்.",
            "english_counselling_text": "Counselling generation failed. For safety, call 108 now.",
            "action": "REFER_108",
        })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Nalam backend running on {port}...", flush=True)
    app.run(host="0.0.0.0", port=port)
