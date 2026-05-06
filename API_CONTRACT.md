# API Contract (Single Source of Truth)

This document is the canonical API contract for this project.
Frontend, mock backend, and Kaggle backend MUST match this file exactly.
If implementation code disagrees with this contract, the code is wrong.

## 1) GET `/health`

### Request Body
- No request body.

### Success Response
Fields (exact):
- `status` (string) - service health status text.
- `model` (string) - model/backend identifier.

Example:
```json
{
  "status": "Nalam API running",
  "model": "Gemma 4 E2B"
}
```

### Failure/Fallback Response (Clinically Safe)
Fields (exact):
- `status` (string)
- `model` (string)
- `warning` (string)

Required behavior:
- MUST return a valid JSON object (never blank, never non-JSON error page).

Example:
```json
{
  "status": "degraded",
  "model": "unknown",
  "warning": "health check fallback response"
}
```

---

## 2) POST `/assess`

### Request Body
Fields (exact):
- `baby` (object)
  - `name` (string) - example: `"Baby Priya"`
  - `weight` (string) - example: `"2.8"`
  - `age_days` (integer) - example: `3`
  - `premature` (boolean) - example: `false`
- `answers` (object)
  - `feeding` (boolean) - example: `true`
  - `activity` (boolean) - example: `false`
  - `warmth` (boolean) - example: `true`
  - `breathing` (boolean) - example: `true`

Example:
```json
{
  "baby": {
    "name": "Baby Priya",
    "weight": "2.8",
    "age_days": 3,
    "premature": false
  },
  "answers": {
    "feeding": true,
    "activity": false,
    "warmth": true,
    "breathing": true
  }
}
```

### Success Response
Response shape is EXACTLY:
- `is_safe` (boolean)
- `tamil_message` (string)
- `english_message` (string)
- `danger_signs` (array of strings)

Notes:
- No extra fields allowed.
- `decision` MUST NOT be returned.
- `decision_tamil` MUST NOT be returned.
- `danger_signs` is required in every response. Safe case MUST be `[]`.

Example:
```json
{
  "is_safe": false,
  "tamil_message": "<Tamil referral guidance>",
  "english_message": "Danger signs detected. Refer to PHC immediately.",
  "danger_signs": ["activity"]
}
```

### Failure/Fallback Response (Clinically Safe)
Fields (exact):
- `is_safe` (boolean) - MUST be `false`
- `tamil_message` (string)
- `english_message` (string)
- `danger_signs` (array of strings) - MUST be present (use at least one conservative marker when uncertain)

Example:
```json
{
  "is_safe": false,
  "tamil_message": "<Tamil fallback: treat as danger and refer now>",
  "english_message": "Assessment unavailable. Treat as danger and refer immediately.",
  "danger_signs": ["unknown_risk_fallback"]
}
```

---

## 3) POST `/mother-health`

### Request Body
Fields (exact):
- `answers` (object)
  - `bleeding` (boolean) - example: `false`
  - `fever` (boolean) - example: `false`
  - `depressed` (boolean) - example: `false`

Example:
```json
{
  "answers": {
    "bleeding": false,
    "fever": false,
    "depressed": false
  }
}
```

### Success Response
Fields (exact):
- `is_safe` (boolean)
- `tamil_message` (string)
- `english_message` (string)
- `danger_signs` (array of strings)

Notes:
- `danger_signs` is required in every response.
- Safe case MUST return `danger_signs: []` (never `undefined`, never absent).

Example:
```json
{
  "is_safe": true,
  "tamil_message": "<Tamil mother-safe guidance>",
  "english_message": "No maternal danger signs detected. Continue routine care.",
  "danger_signs": []
}
```

### Failure/Fallback Response (Clinically Safe)
Fields (exact):
- `is_safe` (boolean) - MUST be `false`
- `tamil_message` (string)
- `english_message` (string)
- `danger_signs` (array of strings) - MUST be present

Example:
```json
{
  "is_safe": false,
  "tamil_message": "<Tamil fallback: urgent maternal referral>",
  "english_message": "Mother-health assessment unavailable. Refer to PHC immediately.",
  "danger_signs": ["unknown_maternal_risk_fallback"]
}
```

---

## 4) POST `/audio-text`

### Request Body
Fields (exact):
- `text` (string) - free-text transcription from speech input.
- `baby_context` (object) - REQUIRED
  - `visit_day` (integer) - example: `3`
  - `birth_weight` (string) - example: `"2.8"`

Required behavior:
- Backend MUST consume `baby_context` for personalized concern detection.

Example:
```json
{
  "text": "Baby is not feeding well since last night",
  "baby_context": {
    "visit_day": 3,
    "birth_weight": "2.8"
  }
}
```

### Success Response
Fields (exact):
- `transcription` (string)
- `feeding_concern` (boolean)
- `activity_concern` (boolean)
- `warmth_concern` (boolean)
- `breathing_concern` (boolean)
- `urgency` (string; allowed values: `"low"`, `"high"`)
- `confidence` (string; example values: `"low"`, `"medium"`, `"high"`)
- `reasoning` (string)

Example:
```json
{
  "transcription": "Baby is not feeding well since last night",
  "feeding_concern": true,
  "activity_concern": false,
  "warmth_concern": false,
  "breathing_concern": false,
  "urgency": "high",
  "confidence": "high",
  "reasoning": "Feeding concern detected; risk elevated for day-3 newborn."
}
```

### Failure/Fallback Response (Clinically Safe)
Fields (exact):
- `transcription` (string)
- `feeding_concern` (boolean)
- `activity_concern` (boolean)
- `warmth_concern` (boolean)
- `breathing_concern` (boolean)
- `urgency` (string)
- `confidence` (string)
- `reasoning` (string)

Required behavior:
- On failure, concerns SHOULD default to a cautious interpretation when uncertainty is high.

Example:
```json
{
  "transcription": "",
  "feeding_concern": true,
  "activity_concern": true,
  "warmth_concern": false,
  "breathing_concern": false,
  "urgency": "high",
  "confidence": "low",
  "reasoning": "Audio-text processing failed; conservative concern fallback applied."
}
```

---

## 5) POST `/counselling`

### Request Body
Fields (exact):
- `baby` (object) - REQUIRED
  - `weight` (string) - example: `"2.8"`
  - `age_days` (integer) - example: `3`
  - `premature` (boolean) - example: `false`
- `danger_signs` (array of strings) - REQUIRED
- `is_safe` (boolean) - REQUIRED
- `mother_result` (object) - REQUIRED
  - `is_safe` (boolean) - example: `true`
  - `danger_signs` (array of strings) - example: `[]`
  - `tamil_message` (string) - example: `"<Tamil mother summary>"`
  - `english_message` (string) - example: `"No maternal danger signs detected."`

Required behavior:
- Empty request body `{}` is invalid and MUST NOT be used.

Example:
```json
{
  "baby": {
    "weight": "2.8",
    "age_days": 3,
    "premature": false
  },
  "danger_signs": ["activity"],
  "is_safe": false,
  "mother_result": {
    "is_safe": true,
    "danger_signs": [],
    "tamil_message": "<Tamil mother summary>",
    "english_message": "No maternal danger signs detected."
  }
}
```

### Success Response
Fields (exact):
- `tamil_counselling_text` (string)
- `english_counselling_text` (string)
- `action` (string; allowed values: `"HOME_CARE"`, `"REFER_PHC"`, `"REFER_108"`)

Example:
```json
{
  "tamil_counselling_text": "<Tamil counselling script>",
  "english_counselling_text": "Continue breastfeeding and seek immediate care for listed danger signs.",
  "action": "REFER_PHC"
}
```

### Failure/Fallback Response (Clinically Safe)
Fields (exact):
- `tamil_counselling_text` (string)
- `english_counselling_text` (string)
- `action` (string) - MUST be `"REFER_108"`

Example:
```json
{
  "tamil_counselling_text": "<Tamil fallback: call 108 now>",
  "english_counselling_text": "Counselling generation failed. Call 108 emergency service now.",
  "action": "REFER_108"
}
```

---

## Global Contract Rules (Mandatory)

1. Every response that includes `tamil_message` MUST also include `english_message`. Both are required.
2. `danger_signs` MUST be present in every `/assess` and `/mother-health` response. Safe responses MUST use `[]`.
3. The newborn checklist fourth key is `activity` everywhere. `lethargy` is not allowed.
4. `/audio-text` request MUST include `baby_context.visit_day` (integer) and `baby_context.birth_weight` (string); backend MUST use these values for personalization.
5. `/counselling` request MUST include `baby`, `danger_signs`, `is_safe`, and `mother_result`; empty `{}` is invalid.
6. Failure responses MUST be clinically cautious:
   - `/assess`: default `is_safe: false`
   - `/mother-health`: default `is_safe: false`
   - `/counselling`: default `action: "REFER_108"`
7. `/assess` response shape is exactly `is_safe`, `tamil_message`, `english_message`, `danger_signs` and nothing else.

---

## Field Name Master List

Alphabetical list of every field name used anywhere in this contract:

- `action`
- `activity`
- `activity_concern`
- `age_days`
- `answers`
- `baby`
- `baby_context`
- `birth_weight`
- `bleeding`
- `breathing`
- `breathing_concern`
- `confidence`
- `danger_signs`
- `depressed`
- `english_counselling_text`
- `english_message`
- `feeding`
- `feeding_concern`
- `fever`
- `is_safe`
- `model`
- `mother_result`
- `name`
- `premature`
- `reasoning`
- `status`
- `tamil_counselling_text`
- `tamil_message`
- `text`
- `transcription`
- `urgency`
- `visit_day`
- `warning`
- `warmth`
- `warmth_concern`
- `weight`

---

## What Changed From Current Code

1. `/assess` and `/mother-health` previously returned `tamil_message` without guaranteed `english_message`; fix: make `english_message` required whenever `tamil_message` exists.
2. Checklist key naming drift (`activity` vs `lethargy`) caused mismatch risk; fix: standardize the fourth checklist key as `activity` everywhere.
3. `/mother-health` safe response could omit `danger_signs`; fix: require `danger_signs: []` in safe responses and always include the field.
4. `/counselling` accepted empty `{}` from frontend; fix: require full body with `baby`, `danger_signs`, `is_safe`, and `mother_result`.
5. `/audio-text` received `baby_context` from frontend but backend ignored it; fix: require `baby_context` in request and mandate backend use for personalization.
6. `/assess` returned unused `decision` and `decision_tamil`; fix: remove both and enforce the exact 4-field response shape only.
