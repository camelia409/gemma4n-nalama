"""
Patch nalama-gemma4-tamil-fixed-hosted.ipynb so its Flask endpoints match
API_CONTRACT.md exactly. Run this once before uploading the notebook to Kaggle.

Idempotent: re-running it just rewrites the same cells.
"""
import json
from pathlib import Path

NB_PATH = Path(__file__).parent / "nalama-gemma4-tamil-fixed-hosted.ipynb"

NEW_FLASK_CELL = r'''# Cell 14 — Flask API (contract-compliant)
# Endpoints, request bodies, and response shapes match API_CONTRACT.md.
# All decision-making is RULE-BASED; Gemma generates Tamil + English text only.

!pip install -q flask flask-cors pyngrok

import os
import base64
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

FRONTEND_DIST = '/kaggle/working/dist'   # optional: serve frontend from same origin
app = Flask(__name__, static_folder=FRONTEND_DIST if os.path.isdir(FRONTEND_DIST) else None,
            static_url_path='/')
CORS(app)


# ---- helpers ----------------------------------------------------------------

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


def _gemma_english_from_tamil(tamil_text):
    """Quick English rendering. Uses Gemma if available, falls back to a short label."""
    try:
        messages = [{"role": "user", "content": [{"type": "text",
            "text": f"Translate this Tamil message to short, plain English for an ASHA worker. "
                    f"Only the translation, no preamble.\n\n{tamil_text}"}]}]
        return run_inference(messages, max_new_tokens=200).strip()
    except Exception:
        return "See Tamil message for guidance."


# ---- /health ----------------------------------------------------------------

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "Nalam API running", "model": "Gemma 4 E2B"})


# ---- /assess ----------------------------------------------------------------

@app.route('/assess', methods=['POST'])
def assess():
    try:
        data = request.get_json(silent=True) or {}
        baby = data.get('baby') or {}
        answers = data.get('answers') or {}

        weight_kg = float(baby.get('weight') or 3.0)
        age_days = int(baby.get('age_days') or 3)
        premature = bool(baby.get('premature') or False)

        # Rule-based decision per contract (True = normal, False = danger)
        danger_signs_found = [k for k, v in answers.items() if v is False]
        is_safe = len(danger_signs_found) == 0

        if is_safe:
            tamil_message = generate_tamil_counselling(
                visit_day=age_days, baby_weight_kg=weight_kg,
                is_premature=premature, home_delivery=False
            )
        else:
            tamil_message = generate_referral_explanation(danger_signs_found)

        english_message = _gemma_english_from_tamil(tamil_message)

        return jsonify({
            "is_safe": is_safe,
            "tamil_message": tamil_message,
            "english_message": english_message,
            "danger_signs": danger_signs_found,
        })
    except Exception as e:
        signs_t = " மற்றும் ".join(_DANGER_SIGN_TAMIL.values())
        return jsonify({
            "is_safe": False,
            "tamil_message": "மதிப்பீடு தோல்வியடைந்தது. பாதுகாப்புக்காக குழந்தையை உடனே PHC-க்கு அனுப்பவும்.",
            "english_message": "Assessment failed. For safety, refer the baby to PHC immediately.",
            "danger_signs": ["unknown_risk_fallback"],
        })


# ---- /mother-health ---------------------------------------------------------

@app.route('/mother-health', methods=['POST'])
def mother_health():
    try:
        data = request.get_json(silent=True) or {}
        answers = data.get('answers') or {}
        danger_signs_found = [k for k, v in answers.items() if v is True]
        is_safe = len(danger_signs_found) == 0

        if is_safe:
            tamil_message = (
                "தாய்க்கு இப்போது எந்த அபாய அறிகுறியும் இல்லை. ஓய்வு எடுக்கவும், "
                "சத்தான உணவு உண்ணவும், அதிக நீர் குடிக்கவும்."
            )
        else:
            signs_t = " மற்றும் ".join(
                [_MOTHER_DANGER_TAMIL.get(s, s) for s in danger_signs_found]
            )
            tamil_message = (
                f"தாய்க்கு {signs_t} உள்ளது. இது அவசர நிலை. உடனே PHC-க்கு "
                "அழைத்து செல்லவும். தேவைப்பட்டால் 108 அழைக்கவும்."
            )

        english_message = _gemma_english_from_tamil(tamil_message)

        return jsonify({
            "is_safe": is_safe,
            "tamil_message": tamil_message,
            "english_message": english_message,
            "danger_signs": danger_signs_found,
        })
    except Exception:
        return jsonify({
            "is_safe": False,
            "tamil_message": "தாய் மதிப்பீடு தோல்வியடைந்தது. பாதுகாப்புக்காக PHC-க்கு அனுப்பவும்.",
            "english_message": "Mother-health assessment failed. For safety, refer to PHC.",
            "danger_signs": ["unknown_maternal_risk_fallback"],
        })


# ---- /audio-text ------------------------------------------------------------

@app.route('/audio-text', methods=['POST'])
def audio_text():
    """
    Browser already did Tamil STT; backend extracts concern flags from the text.
    Uses Gemma to read the transcript and decide which checklist items to flag.
    """
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get('text') or '').strip()
        baby_context = data.get('baby_context') or {}
        visit_day = baby_context.get('visit_day', 3)
        birth_weight = baby_context.get('birth_weight', 'unknown')

        prompt = (
            f"You are a Tamil HBNC assistant. The ASHA worker reports the mother's concern about a "
            f"day-{visit_day}, {birth_weight} kg newborn:\n\n"
            f"\"{text}\"\n\n"
            "Return a strict JSON object (no prose) with keys: "
            "feeding_concern, activity_concern, warmth_concern, breathing_concern (booleans), "
            "urgency ('low' or 'high'), confidence ('low'|'medium'|'high'), reasoning (one sentence). "
            "Flag a concern only if the text clearly implies it."
        )
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        raw = run_inference(messages, max_new_tokens=250).strip()

        # Strip code fences if Gemma added them
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()
        parsed = json.loads(raw)

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
    except Exception as e:
        return jsonify({
            "transcription": (data.get('text') if isinstance(data, dict) else '') or "",
            "feeding_concern": True, "activity_concern": True,
            "warmth_concern": False, "breathing_concern": False,
            "urgency": "high", "confidence": "low",
            "reasoning": "Audio-text processing failed; conservative concern fallback applied."
        })


# ---- /counselling -----------------------------------------------------------

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

        weight_kg = float(baby.get('weight') or 3.0)
        age_days = baby.get('age_days') if isinstance(baby.get('age_days'), int) else 3
        premature = bool(baby.get('premature') or False)
        mother_is_safe = bool(mother_result.get('is_safe'))

        if not is_safe and danger_signs:
            action = "REFER_PHC" if mother_is_safe else "REFER_108"
            tamil = generate_referral_explanation(danger_signs)
        elif not mother_is_safe:
            action = "REFER_PHC"
            tamil = (
                "தாய்க்கு அபாய அறிகுறிகள் உள்ளன. தாயை உடனே PHC-க்கு கொண்டு செல்லவும். "
                "குழந்தைக்கு தாய்ப்பால் வழியில் தொடரவும்."
            )
        else:
            action = "HOME_CARE"
            tamil = generate_tamil_counselling(
                visit_day=age_days, baby_weight_kg=weight_kg,
                is_premature=premature, home_delivery=False
            )

        english = _gemma_english_from_tamil(tamil)

        return jsonify({
            "tamil_counselling_text": tamil,
            "english_counselling_text": english,
            "action": action,
        })
    except Exception:
        return jsonify({
            "tamil_counselling_text": "ஆலோசனை உருவாக்க முடியவில்லை. பாதுகாப்புக்காக உடனே 108 அழைக்கவும்.",
            "english_counselling_text": "Counselling generation failed. For safety, call 108 now.",
            "action": "REFER_108",
        })


# ---- frontend passthrough (optional) ----------------------------------------

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if not app.static_folder:
        return jsonify({"status": "Nalam API running", "model": "Gemma 4 E2B"})
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# ---- start ngrok + Flask ----------------------------------------------------

print("Flask app defined. Starting ngrok tunnel...")
from pyngrok import ngrok
ngrok.kill()
http_tunnel = ngrok.connect(5000)
print(f"\nPublic URL: {http_tunnel.public_url}")
print("Set VITE_API_URL=<that URL> in Vercel, then redeploy the frontend.")
print("\nStarting Flask server (this blocks — keep the notebook running)...")
app.run(port=5000, debug=False, use_reloader=False)
'''

NEW_DOC_CELL = """## API Endpoints (matches API_CONTRACT.md)

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service health |
| `/assess` | POST | Newborn checklist assessment |
| `/mother-health` | POST | Maternal danger-sign assessment |
| `/audio-text` | POST | Extract concerns from Tamil transcript |
| `/counselling` | POST | Generate Tamil + English counselling script |

All endpoints follow the canonical request/response shapes in `API_CONTRACT.md`.
Rule-based decision-making lives in the Flask layer; Gemma is used **only** for
generating warm Tamil text (and the English mirror via translation).

### Quick test
```bash
curl -X POST $PUBLIC_URL/assess -H 'Content-Type: application/json' -d '{
  "baby": {"name": "Baby Priya", "weight": "2.8", "age_days": 3, "premature": false},
  "answers": {"feeding": true, "activity": true, "warmth": true, "breathing": true}
}'
```
"""


def main():
    nb = json.loads(NB_PATH.read_text())
    cells = nb["cells"]

    # Find and replace the Flask cell and the doc cell after it.
    flask_idx = None
    for i, c in enumerate(cells):
        src = "".join(c.get("source", []))
        if c["cell_type"] == "code" and "Flask API" in src and "/assess" in src:
            flask_idx = i
            break
    if flask_idx is None:
        raise SystemExit("Could not locate the Flask API cell to patch.")

    cells[flask_idx] = {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": NEW_FLASK_CELL.splitlines(keepends=True),
    }
    # If the next cell is a markdown "API Endpoints" doc, replace it too.
    if flask_idx + 1 < len(cells) and cells[flask_idx + 1]["cell_type"] == "markdown":
        cells[flask_idx + 1] = {
            "cell_type": "markdown",
            "metadata": {},
            "source": NEW_DOC_CELL.splitlines(keepends=True),
        }

    NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n")
    print(f"Patched {NB_PATH.name}: Flask cell {flask_idx} rewritten.")


if __name__ == "__main__":
    main()
