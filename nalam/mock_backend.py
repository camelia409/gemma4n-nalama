from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "Mock Nalam API running", "model": "mock-nalam-v2"})

@app.route('/assess', methods=['POST'])
def assess():
    try:
        data = request.get_json(silent=True) or {}
        answers = data.get('answers', {})
        danger_signs_found = [k for k, v in answers.items() if v is False]
        is_safe = len(danger_signs_found) == 0

        if is_safe:
            return jsonify({
                "is_safe": True,
                "tamil_message": "தாய்ப்பால் தொடர்ந்து கொடுங்கள். குழந்தையை சுத்தமாக வைத்துக்கொள்ளுங்கள்.",
                "english_message": "Continue breastfeeding and keep the baby clean.",
                "danger_signs": []
            })

        return jsonify({
            "is_safe": False,
            "tamil_message": "குழந்தைக்கு அபாய அறிகுறிகள் தெரிகின்றன. 108 ஐ அழைத்து மருத்துவமனைக்கு செல்லவும்.",
            "english_message": "Danger signs detected. Call 108 and refer to PHC immediately.",
            "danger_signs": danger_signs_found
        })
    except Exception:
        # Clinically safe fallback per contract.
        return jsonify({
            "is_safe": False,
            "tamil_message": "மதிப்பீடு தோல்வியடைந்தது. உடனே பரிந்துரை செய்யவும்.",
            "english_message": "Assessment failed. Treat as danger and refer immediately.",
            "danger_signs": ["unknown_risk_fallback"]
        })

@app.route('/counselling', methods=['POST'])
def counselling():
    data = request.get_json(silent=True) or {}
    baby = data.get('baby')
    danger_signs = data.get('danger_signs')
    is_safe = data.get('is_safe')
    mother_result = data.get('mother_result')

    if not isinstance(baby, dict) or not isinstance(danger_signs, list) or not isinstance(is_safe, bool) or not isinstance(mother_result, dict):
        return jsonify({
            "tamil_counselling_text": "ஆலோசனை உருவாக்க முடியவில்லை. பாதுகாப்புக்காக உடனே 108 அழைக்கவும்.",
            "english_counselling_text": "Counselling generation failed. For safety, call 108 now.",
            "action": "REFER_108"
        })

    weight = baby.get('weight')
    age_days = baby.get('age_days')
    premature = baby.get('premature')
    mother_is_safe = mother_result.get('is_safe')

    required_ok = isinstance(weight, str) and isinstance(age_days, int) and isinstance(premature, bool) and isinstance(mother_is_safe, bool)
    if not required_ok:
        return jsonify({
            "tamil_counselling_text": "ஆலோசனை உருவாக்க முடியவில்லை. பாதுகாப்புக்காக உடனே 108 அழைக்கவும்.",
            "english_counselling_text": "Counselling generation failed. For safety, call 108 now.",
            "action": "REFER_108"
        })

    action = "REFER_108" if (not is_safe or not mother_is_safe) else "HOME_CARE"
    danger_text = ", ".join(danger_signs) if danger_signs else "none"

    tamil_text = (
        f"குழந்தை வயது {age_days} நாள், எடை {weight} கிலோ. "
        f"குறைப்பிரசவம்: {'ஆம்' if premature else 'இல்லை'}. "
        f"கண்டறியப்பட்ட அபாய அறிகுறிகள்: {danger_text}. "
        f"தாய் நிலை பாதுகாப்பு: {'பாதுகாப்பானது' if mother_is_safe else 'அபாயம்'}."
    )
    english_text = (
        f"Baby is {age_days} days old, weight {weight} kg, premature={premature}. "
        f"Danger signs: {danger_text}. Mother safe: {mother_is_safe}."
    )

    return jsonify({
        "tamil_counselling_text": tamil_text,
        "english_counselling_text": english_text,
        "action": action
    })

@app.route('/mother-health', methods=['POST'])
def mother_health():
    data = request.get_json(silent=True) or {}
    answers = data.get('answers', {})
    danger_signs_found = [k for k, v in answers.items() if v is True]
    is_safe = len(danger_signs_found) == 0

    if is_safe:
        return jsonify({
            "is_safe": True,
            "tamil_message": "(Mock) தாய்க்கு எந்த அபாய அறிகுறியும் இல்லை. நன்றாக கவனித்துக்கொள்ளவும்.",
            "english_message": "(Mock) No maternal danger signs detected. Continue routine care.",
            "danger_signs": []
        })

    return jsonify({
        "is_safe": False,
        "danger_signs": danger_signs_found,
        "tamil_message": "(Mock) தாய்க்கு உடனடியாக மருத்துவ உதவி தேவை. PHC-க்கு செல்லவும்.",
        "english_message": "(Mock) Maternal danger signs detected. Refer to PHC immediately."
    })

@app.route('/audio-text', methods=['POST'])
def audio_text():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    baby_context = data.get('baby_context', {})
    visit_day = baby_context.get('visit_day')
    birth_weight = baby_context.get('birth_weight')

    feeding = 'பால்' in text or 'குடிக்க' in text or 'feeding' in text
    warmth = 'ஜில்' in text or 'குளிர்' in text or 'warm' in text or 'தண்ணி' in text
    activity = 'சோம்பேறி' in text or 'தூக்க' in text or 'active' in text

    concern_labels = []
    if feeding:
        concern_labels.append("feeding")
    if activity:
        concern_labels.append("activity")
    if warmth:
        concern_labels.append("warmth")

    if concern_labels:
        label_text = ", ".join(concern_labels)
        reasoning = f"{label_text.capitalize()} concern detected in day-{visit_day}, {birth_weight}kg newborn."
    else:
        reasoning = f"No explicit concern keywords detected in day-{visit_day}, {birth_weight}kg newborn."

    return jsonify({
        "transcription": text,
        "feeding_concern": feeding,
        "activity_concern": activity,
        "warmth_concern": warmth,
        "breathing_concern": False,
        "urgency": "high" if (feeding or warmth or activity) else "low",
        "confidence": "high",
        "reasoning": reasoning
    })

if __name__ == '__main__':
    print("Mock Backend running on 5000...")
    app.run(port=5000)
