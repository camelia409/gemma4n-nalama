# Nalam — Interaction Logging Schema

**Schema version:** `1.0`
**Producer:** `nalam/mock_backend.py` → `log_interaction()`
**Sink:** `logs/interactions.jsonl` (one JSON object per line; UTF-8)
**Endpoints logged:** `/assess`, `/counselling`

This schema is the single source of truth consumed by:
- **Phase 1.4** — eval set construction (replays `request_payload`, scores `response_payload`)
- **Phase 4.1** — trend tracking (queries `visit_day`, `baby_weight_kg`, `danger_flags` over time)
- any future fine-tuning pipeline

If the structure changes in a backward-incompatible way, bump `schema_version`
and document the change at the bottom of this file.

---

## Field definitions

| Field | Type | Nullable | Description |
|---|---|---|---|
| `schema_version` | string | no | Schema version that produced this record. Currently `"1.0"`. Consumers should branch on this. |
| `timestamp` | string (ISO 8601, UTC) | no | When the response was produced, e.g. `"2026-05-28T17:16:07.515707+00:00"`. |
| `session_id` | string (UUID v4) | no | Unique per request. Generated server-side. Not yet tied to a user/visit across calls — see Limitations. |
| `endpoint` | string enum | no | Which handler produced this record: `"assess"` or `"counselling"`. |
| `visit_day` | integer | yes | Baby's age in days at this visit (from `baby.age_days`). Scheduled HBNC visits are **1, 3, 7, 14, 28**, but this field stores the **actual** recorded day (may differ for catch-up/delayed visits). `null` if the request omitted/garbled it. |
| `baby_weight_kg` | float | yes | Birth/visit weight in kg (from `baby.weight`, coerced to float). `null` if missing or unparseable. |
| `danger_flags` | array of string | no (may be `[]`) | Active standard checklist keys. For `/assess`: keys in `answers` whose value is `false`. For `/counselling`: the standard keys present in `danger_signs`. Allowed keys: `feeding`, `activity`, `warmth`, `breathing`. Empty array = no standard danger signs. |
| `extra_concerns` | array of string | yes | Free-text concerns the ASHA added beyond the 4 standard items. For `/assess`: the request's `extra_concerns`. For `/counselling`: the non-standard entries found in `danger_signs`. `null` when there are none. |
| `consent_given` | boolean | no | Whether the caller asserted data-capture consent (`request.consent_given`). **Currently always `false`** — the app has no consent UI yet (see Limitations). |
| `gemma_prompt` | string | yes | The exact prompt string sent to the LLM. **Currently always `null`** — will be populated in Phase 1.4 when the prompt is threaded into the logger. |
| `request_payload` | object | no | The full, verbatim request body. Retained for loss-less replay in the eval set. May contain PII (mother/baby identifiers) → `logs/` is git-ignored. |
| `response_payload` | object | no | The full JSON body returned to the client (the LLM- or template-generated result). Shape depends on `endpoint` and follows `API_CONTRACT.md`. |
| `meta` | object | no | Interpretation context so old logs stay readable after upgrades. See below. |
| `meta.app_version` | string | no | App version that produced the record (`APP_VERSION` env, default `"0.1.0"`). |
| `meta.model` | string | no | Configured model id (`GEMMA_MODEL` env), e.g. `"gemini-2.5-flash"`. NOTE: reflects the *configured* model, not whether this specific response came from the model or the template fallback — see Limitations. |

---

## Example record

```json
{
  "schema_version": "1.0",
  "timestamp": "2026-05-28T17:16:07.515707+00:00",
  "session_id": "9b81e881-597e-4b29-a9d1-5d9d920f5e19",
  "endpoint": "assess",
  "visit_day": 3,
  "baby_weight_kg": 2.8,
  "danger_flags": ["feeding"],
  "extra_concerns": ["red rash on left arm"],
  "consent_given": false,
  "gemma_prompt": null,
  "request_payload": {
    "baby": { "name": "Baby Priya", "weight": "2.8", "age_days": 3, "premature": false },
    "answers": { "feeding": false, "activity": true, "warmth": true, "breathing": true },
    "extra_concerns": ["red rash on left arm"]
  },
  "response_payload": {
    "is_safe": false,
    "tamil_message": "குழந்தை சரியாக பால் குடிக்கவில்லை. இது அபாய அறிகுறி...",
    "english_message": "Danger signs detected (baby is not feeding properly). Refer the baby to the PHC immediately...",
    "danger_signs": ["feeding", "red rash on left arm"]
  },
  "meta": {
    "app_version": "0.1.0",
    "model": "gemini-2.5-flash"
  }
}
```

---

## Forward-compatibility notes (Phase 4 trend tracking)

To reconstruct a baby's trajectory across visits without re-querying the app,
trend tracking needs `visit_day` + `baby_weight_kg` + `danger_flags` per record.
All three are promoted to the top level so a consumer can do a single pass over
`interactions.jsonl` and group by baby.

**Open gap:** records are not yet linked to a stable baby identity. `session_id`
is per-request, so two visits for the same baby cannot currently be joined. When
Phase 4 starts, add a `baby_id` (hashed/pseudonymous) field — bump to schema
`1.1`. This was deliberately deferred because the current backend is stateless
and does not receive a baby id; wiring it requires a small frontend change.

---

## Limitations (fields that cannot be fully populated today)

| Field | Status | Why |
|---|---|---|
| `gemma_prompt` | always `null` | The prompt string is built inside each endpoint and not yet passed to the logger. Planned for Phase 1.4. The logger already accepts a `gemma_prompt` argument, so wiring it is a one-line change per call site. |
| `consent_given` | always `false` | No consent-capture UI exists in the app. The field reads `request.consent_given`, which the frontend never sends. Becomes meaningful once a consent screen is added. |
| `meta.model` | configured, not actual | Records the configured `GEMMA_MODEL`. It does **not** indicate whether this particular response came from the LLM or the safe template fallback. Recommend adding a `generated_by` enum (`"model"` \| `"template"`) — deferred to keep 1.2 scoped. |
| `baby_id` | absent | See forward-compatibility note above. Needed before trend tracking can join visits. |

---

## Changelog

- **1.0** (2026-05-28) — initial schema. Promotes `visit_day`, `baby_weight_kg`,
  `danger_flags`, `extra_concerns` to top level; adds `schema_version`,
  `consent_given`, `gemma_prompt`, and `meta`. Retains full `request_payload`
  for replay.
