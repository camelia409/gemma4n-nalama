from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "Mock Nalam API running", "model": "Dummy"})

@app.route('/assess', methods=['POST'])
def assess():
    data = request.json
    answers = data.get('answers', {})
    danger_signs_found = [k for k, v in answers.items() if v == False]
    is_safe = len(danger_signs_found) == 0
    
    if is_safe:
        return jsonify({
            "decision": "MONITOR",
            "decision_tamil": "வீட்டில் கவனிக்கவும்",
            "danger_signs": [],
            "tamil_message": "தாய்ப்பால் தொடர்ந்து கொடுங்கள். குழந்தையை சுத்தமாக வைத்துக்கொள்ளுங்கள்.",
            "is_safe": True
        })
    else:
        return jsonify({
            "decision": "REFER",
            "decision_tamil": "உடனே PHC-க்கு அனுப்பவும்",
            "danger_signs": danger_signs_found,
            "tamil_message": "குழந்தைக்கு அபாய அறிகுறிகள் தெரிகின்றன. 108 ஐ அழைத்து மருத்துவமனைக்கு செல்லவும்.",
            "is_safe": False
        })

@app.route('/counselling', methods=['POST'])
def counselling():
    return jsonify({
        "tamil_counselling_text": "குழந்தைக்கு தொடர்ந்து தாய்ப்பால் கொடுங்கள். 6 மாதம் வரை வேறு உணவு வேண்டாம். குழந்தை நன்றாக வளர்கிறது."
    })

@app.route('/mother-health', methods=['POST'])
def mother_health():
    data = request.json
    answers = data.get('answers', {})
    danger_signs_found = [k for k, v in answers.items() if v == True]
    is_safe = len(danger_signs_found) == 0
    
    if is_safe:
        return jsonify({
            "is_safe": True,
            "tamil_message": "(Mock) தாய்க்கு எந்த அபாய அறிகுறியும் இல்லை. நன்றாக கவனித்துக்கொள்ளவும்."
        })
    else:
        return jsonify({
            "is_safe": False,
            "danger_signs": danger_signs_found,
            "tamil_message": "(Mock) தாய்க்கு உடனடியாக மருத்துவ உதவி தேவை. PHC-க்கு செல்லவும்."
        })

@app.route('/audio', methods=['POST'])
def process_audio():
    # Mocking audio interpretation
    return jsonify({
        "transcription": "(MOCK) குழந்தை சரியாக பால் குடிக்கவில்லை என்று அம்மா சொல்கிறார்.",
        "feeding_concern": True,
        "activity_concern": False,
        "warmth_concern": False,
        "breathing_concern": False,
        "urgency": "high",
        "tamil_followup_question": ""
    })

@app.route('/audio-text', methods=['POST'])
def audio_text():
    data = request.json
    text = data.get('text', '')
    
    # Mocking Gemma 4 reasoning logic
    feeding = 'பால்' in text or 'குடிக்க' in text or 'feeding' in text
    warmth = 'ஜில்' in text or 'குளிர்' in text or 'warm' in text or 'தண்ணி' in text
    activity = 'சோம்பேறி' in text or 'தூக்க' in text or 'active' in text
    
    return jsonify({
        "transcription": text,
        "feeding_concern": feeding,
        "activity_concern": activity,
        "warmth_concern": warmth,
        "breathing_concern": False,
        "urgency": "high" if (feeding or warmth or activity) else "low",
        "confidence": "high",
        "reasoning": "Detected clinical vocabulary in transcription."
    })

if __name__ == '__main__':
    print("Mock Backend running on 5000...")
    app.run(port=5000)
