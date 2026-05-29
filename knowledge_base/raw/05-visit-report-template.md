# HBNC Visit Report Template and Structure

## Purpose of the HBNC Visit Report

The HBNC Visit Report is a structured written summary of every ASHA home visit to a newborn and mother. It serves multiple purposes:

**Who uses it:**
- **ASHA Worker:** Documents the visit for her own records, tracks progress over visits, shows what was assessed and taught
- **ANM/Health Worker:** Reviews reports from ASHA to monitor newborns in her area, identifies high-risk cases, plans PHC/community health center follow-up
- **PHC Doctor:** If baby is referred, receives report with baseline findings and reason for referral
- **Mother's Copy:** Printed simple version given to mother showing: baby's condition, what to do, when to come back, what danger signs to watch for

**What makes a good report:**
- Clear and specific (not vague)
- Written in plain language (no medical jargon)
- Complete (all required fields filled, nothing omitted)
- Bilingual (Tamil and English for accessibility)
- Actionable (mother knows exactly what to do)
- Accurate (findings documented clearly so next visitor can see trends)

---

## Complete HBNC Visit Report Schema

Every report contains the following fields in this order. Fields marked **[REQUIRED]** must always be completed.

### **A. VISIT METADATA (Identifying Information)**

| Field Name | Tamil Name | Data Type | Required | Example |
|------------|-----------|-----------|----------|---------|
| Visit Date | ஆய்வு நாள் | Date (DD/MM/YYYY) | **[R]** | 15/05/2026 |
| Day of Life | பிறப்பிற்கு நாட்கள் | Number | **[R]** | 3 |
| ASHA Worker Name | ASHA பெயர் | Text | **[R]** | Lakshmi Devi |
| Baby Name | குழந்தையின் பெயர் | Text | **[R]** | Arjun |
| Mother's Name | தாயின் பெயர் | Text | **[R]** | Priya |
| Location/Village | இடம்/கிராமம் | Text | **[R]** | Mudalur Village |
| Mother's Phone | தாயின் தொலைபேசி | Phone | Optional | 9876543210 |
| Baby's Birth Date | குழந்தையின் பிறந்த நாள் | Date | **[R]** | 12/05/2026 |
| Birth Weight | பிறப்பு எடை | Number (kg) | **[R]** | 2.8 |
| Delivery Location | பிரസவ இடம் | Text (Home/Hospital) | **[R]** | Hospital |

---

### **B. BABY ASSESSMENT FINDINGS**

| Field Name | Tamil Name | Data Type | Required | Example |
|------------|-----------|-----------|----------|---------|
| Current Weight | தற்போதைய எடை | Number (kg) | **[R]** | 2.7 |
| Weight Change Since Birth | பிறப்பிற்குப் பிறகு எடை மாற்றம் | Text with % | **[R]** | Lost 0.1 kg (3.6% loss) |
| Temperature | வெப்பநிலை | Number (°C) | **[R]** | 37.2°C |
| Breathing Rate (at rest) | சுவாசக் கணக்கு | Number/min | **[R]** | 48 breaths/min |
| General Appearance | பொதுவான தோற்றம் | Text | **[R]** | Alert, responsive, normal color |
| Feeding Status | பாலூட்டுதல் நிலை | Text | **[R]** | Feeding 8-10 times/day, good latch, both breasts |
| Wet Diapers (24h) | ஈரமான விரிப்பு (24 மணி) | Number | **[R]** | 6 wet diapers |
| Stools (24h) | மலம் (24 மணி) | Number | **[R]** | 3 stools, yellow, seedy |
| Skin Color/Condition | தோல் நிறம்/நிலை | Text | **[R]** | Pink, no jaundice visible |
| Jaundice Assessment | மஞ்சள் நோய் மதிப்பீடு | Text (None/Mild/Moderate/Severe) | **[R]** | Mild on face, not on limbs |
| Cord Status | தொப்புளி நிலை | Text | **[R]** | Dry, no redness, healing well |
| Activity Level | செயல்பாடு நிலை | Text | **[R]** | Active, cries strongly, responsive to stimulation |

---

### **C. MOTHER ASSESSMENT FINDINGS**

| Field Name | Tamil Name | Data Type | Required | Example |
|------------|-----------|-----------|----------|---------|
| Vaginal Bleeding | யோனி இரத்தப்போக்கு | Text | **[R]** | Lochia normal, minimal, no odor |
| Perineal Wound Status | பிரसவ காயம் | Text (if applicable) | Optional | If C-section: Incision clean, healing, no discharge |
| Breast Status | மார்பக நிலை | Text | **[R]** | Soft, engorged but manageable, no pain or redness |
| Breastfeeding Confidence | தாய் நம்பிக்கை | Text | **[R]** | Confident, baby latches well, satisfied with milk |
| Temperature | வெப்பநிலை | Number (°C) | **[R]** | 37.0°C |
| Mood/Mental Status | மனநிலை | Text | **[R]** | Alert, coping well, confident in baby care |
| Rest and Recovery | ஆறுதல் | Text | **[R]** | Resting adequately, family support present |
| Danger Signs Present? | ஆபத்து அறிகுறிகள் | Yes/No | **[R]** | No |

---

### **D. DANGER SIGNS IDENTIFIED (Complete Only if Danger Signs Present)**

| Field Name | Tamil Name | Data Type | Required if danger present | Example |
|------------|-----------|-----------|----------|---------|
| Danger Sign 1 | ஆபத்து அறிகுறி 1 | Text | **[R]** | Mild cord redness |
| Severity Level | ஆபத்து நிலை | Dropdown (Mild/Moderate/Severe/Critical) | **[R]** | Mild |
| Danger Sign 2 | ஆபத்து அறிகுறி 2 | Text | Optional | None |
| Severity Level | ஆபத்து நிலை | Dropdown | Optional | - |
| Danger Sign 3 | ஆபத்து அறிகுறி 3 | Text | Optional | None |
| Any mother danger signs? | தாய் ஆபத்து அறிகுறிகள் | Yes/No | **[R]** | No |
| If yes, describe | விவரம் | Text | Optional | - |

---

### **E. COUNSELLING PROVIDED**

| Field Name | Tamil Name | Data Type | Required | Example |
|------------|-----------|-----------|----------|---------|
| Breastfeeding Counselling Given | தாய்ப்பால் ஆலோசனை | Text | **[R]** | Taught correct latch position, explained colostrum benefits, demonstrated side-lying position |
| Cord Care Counselling Given | தொப்புளி கவனம் | Text | **[R]** | Keep dry, expose to air, no oils, wash hands before touching |
| Temperature Maintenance Counselling | வெப்பநிலை பராமரிப்பு | Text | **[R]** | Appropriate blankets, skin-to-skin contact, avoid cold drafts |
| Hygiene Counselling Given | சுத்தமாக வாழும் முறை | Text | **[R]** | Hand washing before baby care, clean environment, separate cloths |
| Danger Signs Teaching Given | ஆபத்து அறிகுறிகள் கற்பிப்பு | Text | **[R]** | Explained fever, poor feeding, jaundice, breathing difficulty, what to do if present |
| Mother's Recovery Support | தாயின் ஆறுதல் ஆதரவு | Text | **[R]** | Discussed rest, family support, nutrition, emotional adjustment |
| Other Counselling | பிற ஆலோசனை | Text | Optional | Discussed exclusive breastfeeding until 6 months |

---

### **F. DIET AND NUTRITION ADVICE GIVEN**

| Field Name | Tamil Name | Data Type | Required | Example |
|------------|-----------|-----------|----------|---------|
| Mother Diet Advice | தாயின் உணவு ஆலோசனை | Text | **[R]** | Eat warm rice with ghee, lentils, drumstick leaves, drink 3-4 liters water daily, avoid cold foods |
| Milk Supply Support | பால் உற்பத்தி ஆதரவு | Text | **[R]** | Frequent breastfeeding builds supply, offered galactagogue options (sesame, fenugreek) |
| Feeding Frequency | பாலூட்டும் அதிர்வெண் | Text | **[R]** | 8-12 times daily, day and night, on demand |
| Feeding Duration | பாலூட்டல் காலம் | Text | **[R]** | Let baby finish each breast, usually 20-40 minutes total |
| Dietary Supplements | உணவு கூட்டுப்பொருள் | Text | Optional | If needed: Iron tablets, multivitamin discussed |

---

### **G. FOLLOWUP SCHEDULE**

| Field Name | Tamil Name | Data Type | Required | Example |
|------------|-----------|-----------|----------|---------|
| Next Visit Date | அடுத்த வரவு நாள் | Date | **[R]** | 18/05/2026 (Day 6) |
| Next Visit Day | நாள் | Number | **[R]** | Day 6 of life |
| Reason for Next Visit | அடுத்த வரவின் காரணம் | Text | **[R]** | Check feeding progress, weight, jaundice status |
| What Mother Should Watch For | தாய் கவனிக்க வேண்டியவை | Text | **[R]** | Fever, baby stops feeding, breathing difficulty, yellow color worse |
| When to Come to PHC Immediately | உடனடி PHC நேரம் | Text | **[R]** | If baby has fever, cannot feed, breathing problems, or yellow everywhere |
| Contact Number for Emergencies | அவசர தொலைபேசி | Text | **[R]** | Call 108 ambulance or come to Mudalur PHC |
| Special Monitoring Notes | சிறப்பு கவனிப்பு குறிப்புகள் | Text | Optional | LBW baby—monitor weight closely at each visit |

---

### **H. REFERRAL DECISION (Complete Only if Referral Made)**

| Field Name | Tamil Name | Data Type | Required if referred | Example |
|------------|-----------|-----------|----------|---------|
| Referral Needed? | மாற்றுதல் தேவையா? | Yes/No | **[R]** | Yes |
| Referral Type | மாற்றுதல் வகை | Dropdown (PHC Walk-in / PHC Urgent Same Day / 108 Ambulance) | **[R]** | PHC Same Day |
| Reason for Referral | மாற்றுதல் காரணம் | Text | **[R]** | Cord redness with discharge, needs assessment and possible antibiotics |
| Referred To Facility | வசதி | Text | **[R]** | Mudalur Primary Health Center |
| Facility Address | வசதி முகவரி | Text | **[R]** | Mudalur PHC, Main Road |
| Facility Phone | வசதி தொலைபேசி | Phone | **[R]** | 04656-234567 |
| What Mother Should Bring | தாய் எடுத்துச் செல்ல வேண்டியவை | Text | Optional | HBNC card, baby's feeding history, this report |
| Expected Outcome | எதிர்பார்க்கப்படும் விளைவு | Text | **[R]** | Assessment, cord care teaching, possible topical/oral antibiotics if infection confirmed |
| Follow-up After Referral | மாற்றுதலுக்குப் பிறகு | Text | **[R]** | ASHA to confirm baby reached facility next day. Plan recheck in 2-3 days if discharged same day. |

---

### **I. ASHA NOTES AND OBSERVATIONS**

| Field Name | Tamil Name | Data Type | Required | Example |
|------------|-----------|-----------|----------|---------|
| Family Cooperation | குடும்பம் ஒத்துழைப்பு | Text | **[R]** | Good, mother receptive to counselling, family supportive |
| Challenges Identified | சிக்கலுக்கு | Text | Optional | Isolated family, limited access to PHC, poor nutrition at home |
| Strengths to Build On | வலிமை | Text | Optional | Mother motivated to breastfeed, good family support |
| Continuity Notes | தொடர்பு குறிப்புகள் | Text | Optional | Mother mentioned concern about milk supply—address at next visit |

---

### **J. MOTHER'S ACKNOWLEDGMENT**

| Field Name | Tamil Name | Data Type | Required | Example |
|------------|-----------|-----------|----------|---------|
| Mother Understands Counselling | தாய் புரிந்துகொண்டாரா | Yes/No (thumbprint if illiterate) | **[R]** | Yes / Thumbprint |
| Questions Asked by Mother | தாயின் கேள்விகள் | Text | Optional | Asked about exclusive breastfeeding and water |
| Questions Answered | பதிலளித்த கேள்விகள் | Text | Optional | Explained breast milk is 88% water, no supplemental water needed |
| Mother's Signature/Mark | தாய் கையெழுத்து | Signature/Thumbprint | Optional | [Mother's signature] |
| Date Report Given to Mother | அறிக்கை வழங்கிய நாள் | Date | **[R]** | 15/05/2026 |

---

## Report Sections in Presentation Order

A complete HBNC report is organized as follows for clarity:

### **Report Header** (一ページの上部)
```
HBNC VISIT REPORT
ASHA Worker: [Name] | Date: [Date] | Day of Life: [Day]
Baby: [Name] | Mother: [Name] | Location: [Village]
```

### **1. BABY'S STATUS SUMMARY** (1-2 sentences)
State overall baby condition, weight status, feeding status clearly.

Example: "Arjun is a 3-day-old boy weighing 2.7 kg (3.6% weight loss from 2.8 kg birth weight). He is alert and responsive, feeding 8-10 times daily with good latch on both breasts."

### **2. TODAY'S BABY ASSESSMENT** (Vital signs and specific findings)
Temperature, breathing rate, weight, feeding, wet diapers, stools, skin color, cord, activity level.

### **3. MOTHER'S STATUS SUMMARY** (1 sentence)
State overall mother condition.

Example: "Mother is recovering well, breastfeeding confidently, and coping with newborn care."

### **4. TODAY'S MOTHER ASSESSMENT** (Specific findings)
Bleeding, perineal status, breasts, mood, temperature, rest.

### **5. DANGER SIGNS ASSESSMENT** (If no signs: "None identified" | If present: list each)
Only complete if danger signs found.

### **6. COUNSELLING PROVIDED** (Summary of teaching)
Breastfeeding, cord care, temperature, hygiene, danger signs, mother's recovery.

### **7. NUTRITION ADVICE GIVEN** (Summary of diet counselling)
What mother should eat, milk supply support, feeding frequency.

### **8. FOLLOWUP SCHEDULE** (Clear and specific)
Next visit date, what to watch for, when to come immediately.

### **9. REFERRAL DECISION** (Only if needed)
Is referral needed? To where? Why? What will happen?

### **10. MOTHER'S COPY MESSAGE** (Simple language, large print if printed)
"Come back on [date]. Watch for: fever, stops feeding, yellow everywhere. Call 108 if emergency."

---

## Language Rules for Report Writing

### **Principle 1: Write in Plain Language**

❌ **NOT:** "Patient exhibits physiological jaundice with mild icterus on cephalic region."
✅ **YES:** "Baby has mild yellow color on face, not on limbs. This is normal and should improve with frequent breastfeeding."

❌ **NOT:** "Infant demonstrates adequate milk transfer with bilateral breast engagement."
✅ **YES:** "Baby is feeding well on both breasts, taking about 20-30 minutes per feed, waking naturally for feeds."

### **Principle 2: Be Specific, Not Vague**

❌ **NOT:** "Baby is doing okay."
✅ **YES:** "Baby is alert, breathing normally (48 breaths/min), feeding 8 times in 24 hours, passing 6 wet diapers daily."

❌ **NOT:** "Cord looks fine."
✅ **YES:** "Cord is dry with no redness, no discharge, no foul smell, healing normally."

### **Principle 3: Use Active Voice and Clear Attribution**

❌ **NOT:** "Feeding difficulty was noted."
✅ **YES:** "Baby struggled to latch on first breast but feeds well on second breast with positioning help."

❌ **NOT:** "Counselling was provided."
✅ **YES:** "ASHA taught mother correct breastfeeding position and demonstrated side-lying position for night feeds."

### **Principle 4: Include Specificity in Numbers**

❌ **NOT:** "Baby is wetting diapers adequately."
✅ **YES:** "Baby passed 6 wet diapers in last 24 hours (expected for Day 3)."

❌ **NOT:** "Baby has some weight loss."
✅ **YES:** "Baby lost 0.1 kg since birth (3.6% loss), which is normal for Day 3."

### **Principle 5: Use Bilingual Terms Consistently**

Always use the Tamil term alongside English in parentheses first use, then English abbreviation after.

✅ **YES:** "Baby has நாபிப் தொற்று (cord infection) with redness extending 2 cm around umbilicus."

### **Principle 6: Be Objective About Danger Signs**

Do not minimize or exaggerate. State facts clearly.

✅ **YES:** "Breathing rate is 65 breaths/min at rest, which is faster than normal (30-60). Baby is not in respiratory distress but needs monitoring."

❌ **NOT:** "Baby is fine" (when breathing is actually fast).
❌ **NOT:** "Baby is dying" (when breathing fast but stable).

---

## Report Variations by Outcome

Reports differ based on outcome. Use these templates:

### **VARIATION 1: SAFE VISIT REPORT (No Danger Signs, Healthy Baby)**

**Referral Needed?** No
**Next Visit:** Standard schedule
**Length:** Shorter, focused on positive findings and routine counselling

**Key sections to emphasize:**
- Weight status and trajectory
- Feeding adequacy and mother's confidence
- Mother's recovery and support
- Routine counselling given
- Standard followup date

**Tone:** Reassuring, supportive
**Example in report:** "All findings are normal. Continue current feeding and care practices. Come back on [date] for routine check."

---

### **VARIATION 2: DANGER SIGN REPORT (Concern Found, No Referral Yet)**

**Referral Needed?** No, but close monitoring needed
**Next Visit:** Sooner than standard (2-3 days instead of standard interval)
**Length:** Longer, focused on danger sign assessment and management plan

**Key sections to emphasize:**
- Specific danger sign identified and severity
- Why it is concerning
- What is being done at home (counselling, support)
- What mother should watch for
- Recheck visit date sooner than standard
- When to escalate to referral

**Tone:** Serious but not alarming; action-oriented
**Example in report:** "Baby has mild cord redness. This is not an emergency but needs close monitoring. Keep cord dry and clean. I will check again on [2-3 days]. If redness spreads, baby develops fever, or discharge appears, come to PHC immediately."

---

### **VARIATION 3: REFERRAL REPORT (Danger Sign Requires PHC)**

**Referral Needed?** Yes
**Next Visit:** Determined by PHC plan
**Length:** Longer, detailed, includes rationale for referral and continuity plan

**Key sections to emphasize:**
- Specific danger sign(s) identified
- Severity level and justification for referral
- PHC facility details (address, phone, what to bring)
- What family should expect at PHC
- Instructions for getting to facility
- Follow-up plan after referral
- ASHA continuity after referral

**Tone:** Clear, calm, action-oriented
**Example in report:** "Baby has signs of cord infection: redness extending around umbilicus, yellow discharge, possible mild fever. This requires PHC assessment and treatment. Mother should go to Mudalur PHC today [date] with this report. Baby may need antibiotics and cord care training. I will follow up tomorrow to confirm baby was seen and plan next steps."

---

## Sample Complete Report: Safe Visit (Day 3, Healthy Baby, No Flags)

```
════════════════════════════════════════════════════════════
            HOME BASED NEWBORN CARE (HBNC) VISIT REPORT
════════════════════════════════════════════════════════════

VISIT INFORMATION
─────────────────
Visit Date: 15/05/2026
Day of Life: 3
ASHA Worker: Lakshmi Devi
Baby Name: Arjun
Mother Name: Priya
Location: Mudalur Village, Block Postal, District
Mother's Phone: 9876543210


BABY'S STATUS SUMMARY
─────────────────────
Arjun is a healthy 3-day-old boy weighing 2.7 kg (3.6% weight loss from birth weight of 2.8 kg). He is alert, responsive, and feeding well on both breasts 8-10 times daily. All vital signs are normal. No danger signs identified.


BABY'S DETAILED ASSESSMENT
──────────────────────────
Current Weight: 2.7 kg
Weight Change: Lost 0.1 kg (3.6% loss from birth) — Normal for Day 3
Temperature: 37.2°C — Normal
Breathing Rate: 48 breaths/minute at rest — Normal (30-60 expected)
General Appearance: Alert and responsive, cries strongly, interacts with mother
Feeding Status: Feeding 8 times in last 24 hours, latches well on both breasts, takes about 25 minutes per feed, baby appears satisfied after feeds
Wet Diapers: 6 wet diapers in last 24 hours — Adequate for Day 3
Stools: 3 stools, yellow color, seedy texture — Normal
Skin Color: Pink, no jaundice visible — Normal for Day 3
Cord Status: Cord is dry with no redness, no discharge, no foul smell, healing normally
Activity Level: Active, responsive to voice and touch, sleeps between feeds


MOTHER'S STATUS SUMMARY
───────────────────────
Priya is recovering well from hospital delivery. She is breastfeeding confidently, managing newborn care with family support, and her mood is positive.


MOTHER'S DETAILED ASSESSMENT
────────────────────────────
Vaginal Bleeding/Lochia: Normal amount, no offensive odor — Normal for Day 3
C-Section Wound (if applicable): N/A (vaginal delivery)
Breast Status: Breasts are firm with milk coming in, no pain, no redness — Normal engorgement for Day 3
Breastfeeding Confidence: Mother is confident, says baby is latching well, feels letdown reflex
Temperature: 37.0°C — Normal
Mood: Alert, happy, excited about baby, managing well
Rest and Recovery: Resting at home with family support, mother-in-law helping with household work
Danger Signs in Mother: None


DANGER SIGNS ASSESSMENT
───────────────────────
No danger signs identified in baby or mother.
Baby: All vital signs normal, feeding adequate, no fever, no breathing difficulty, no jaundice concern, cord healing normally
Mother: No excessive bleeding, no fever, no breast problems, mood positive, recovering well


COUNSELLING PROVIDED TODAY
───────────────────────────
1. BREASTFEEDING: Reviewed correct latch position (mouth covering areola, chin touching breast). Explained that colostrum is all baby needs on Day 1-3. Discussed frequency (8-12 times per day is normal). Taught side-lying position for comfortable night feeding. Mother demonstrates good understanding.

2. CORD CARE: Instructed to keep cord dry and exposed to air. Explained normal cord changes (progressively drier, will separate Day 7-10). Advised no oils, ash, or pastes. Emphasized hand washing before touching cord or baby. Mother understands.

3. TEMPERATURE MAINTENANCE: Discussed appropriate blankets (currently using 2 blankets, which is appropriate). Encouraged skin-to-skin contact for bonding and warmth. Advised against excessive wrapping.

4. HYGIENE: Explained importance of hand washing before baby care. Discussed clean environment and separate cloths for baby. Family understands.

5. DANGER SIGNS: Taught mother to watch for: fever (temp ≥38.5°C), baby stops feeding, baby very sleepy, yellow color on baby, cord with redness or pus, baby breathing very fast. Explained when to come to PHC immediately.

6. MOTHER'S RECOVERY: Discussed importance of rest, good nutrition, and staying hydrated while breastfeeding. Encouraged family support. Addressed any concerns about recovery.


NUTRITION AND DIET ADVICE GIVEN
────────────────────────────────
MOTHER'S DIET: Advised warm, nourishing foods to support recovery and milk production:
- Rice with ghee and salt (easy to digest)
- Lentil soup (protein)
- Warm milk with jaggery in evening
- Plenty of water and warm herbal drinks (cumin water, fennel water)
- Encouraged traditional postpartum foods: sesame seeds, drumstick leaves, jaggery
- Explained these foods support milk supply and healing, not luxuries
- Advised against raw/cold foods, excessive spices

FEEDING FREQUENCY: Explained that baby should feed 8-12 times per 24 hours, including at night. This is normal and helps mother's milk supply.

BREASTFEEDING SUPPORT: Frequent breastfeeding is the best way to maintain and increase milk supply. Mother's nutrition and hydration directly affect milk.


FOLLOWUP SCHEDULE
─────────────────
Next Visit Date: 18/05/2026 (Tuesday)
Next Visit Day: Day 6 of life
Purpose of Next Visit: Check baby's continued feeding progress, weight regain, assess for jaundice, check cord healing, mother's recovery

WHAT MOTHER SHOULD WATCH FOR BEFORE NEXT VISIT:
- Baby's temperature (feel warm but not hot)
- Baby feeding 8+ times daily
- 6 or more wet diapers daily
- Yellow color on baby (mild yellow on face on Day 3-5 is normal, but watch if spreading)

WHEN TO COME TO PHC IMMEDIATELY (Do Not Wait for Next Scheduled Visit):
- Baby develops fever (≥38.5°C)
- Baby stops feeding or very weak feeding
- Baby very difficult to wake or seems limp
- Baby breathing very fast (≥60 breaths/minute) or with difficulty
- Yellow color spreading to arms, legs, or everywhere
- Cord becomes red, warm, or has discharge
- Baby has seizure or unusual movements
- CALL 108 AMBULANCE IF VERY SERIOUS

Emergency Contact: Call Mudalur PHC: 04656-234567 or 108 ambulance


MOTHER'S ACKNOWLEDGMENT
──────────────────────
Does mother understand today's counselling? YES ✓

Questions Asked by Mother:
- "Is the yellow color on baby normal?"
- "Do I need to give baby water in this heat?"

Questions Answered:
- Explained that mild yellow on face on Day 3 is physiological jaundice, not an emergency, improves with frequent breastfeeding
- Explained breast milk is 88% water, plenty for baby's hydration, NO supplemental water needed

Mother's Signature: [Priya's signature] / Thumbprint

Date Report Given to Mother: 15/05/2026
Mother Received: Copy of this report (simple language version)


ASHA NOTES
──────────
Family Cooperation: Excellent — Mother is motivated, receptive to counselling, family is supportive and participating in baby care
Strengths: Mother's confidence in breastfeeding, family presence and help, good living conditions, water availability
Any Challenges: None identified
Follow-up Notes: Baby and mother are doing very well. Standard HBNC follow-up schedule appropriate.


═══════════════════════════════════════════════════════════
Report Completed By: Lakshmi Devi, ASHA Worker
Signature: [ASHA signature]  Date: 15/05/2026
═══════════════════════════════════════════════════════════
```

---

## Sample Complete Report: Danger Sign Visit (Day 3, Cord Infection, PHC Referral)

```
════════════════════════════════════════════════════════════
            HOME BASED NEWBORN CARE (HBNC) VISIT REPORT
                    ⚠️ REFERRAL REPORT ⚠️
════════════════════════════════════════════════════════════

VISIT INFORMATION
─────────────────
Visit Date: 15/05/2026
Day of Life: 3
ASHA Worker: Lakshmi Devi
Baby Name: Arjun
Mother Name: Priya
Location: Mudalur Village, Block Postal, District
Mother's Phone: 9876543210


BABY'S STATUS SUMMARY
─────────────────────
Arjun is a 3-day-old boy weighing 2.7 kg. While most vital signs are stable, he has signs of தொப்புளி வழியான தொற்று (cord infection) that require PHC evaluation and treatment today.


BABY'S DETAILED ASSESSMENT
──────────────────────────
Current Weight: 2.7 kg
Weight Change: Lost 0.1 kg (3.6%) — Acceptable for Day 3
Temperature: 37.5°C — Slightly elevated but not fever
Breathing Rate: 48 breaths/minute — Normal
General Appearance: Alert and responsive, active
Feeding Status: Feeding 7 times in last 24 hours, reasonable latch, consuming breast milk
Wet Diapers: 5 in last 24 hours — Slightly less than ideal but acceptable
Stools: 2 stools, yellow — Acceptable
Skin Color: Pink, no jaundice — Good
CORD STATUS: ⚠️ CONCERN IDENTIFIED — Redness visible around umbilicus extending approximately 1.5-2 cm. Mild warmth on palpation. Small amount of yellowish discharge from cord stump. No foul odor yet.
Activity Level: Active and responsive


MOTHER'S STATUS SUMMARY
───────────────────────
Priya is recovering from hospital delivery. She is breastfeeding with some confidence, and mood is good. No danger signs identified in mother.


MOTHER'S DETAILED ASSESSMENT
────────────────────────────
Vaginal Bleeding: Normal amount — Normal
Breast Status: Engorged but manageable, no pain or redness — Normal
Breastfeeding Confidence: Good, baby latching well
Temperature: 36.9°C — Normal
Mood: Positive, managing well
Rest: Adequate with family support
Danger Signs in Mother: None


DANGER SIGNS IDENTIFIED
───────────────────────
BABY DANGER SIGN PRESENT: YES

Specific Danger Sign: தொப்புளி வழியான தொற்று (Cord Infection) — Moderate Stage

Details:
- Redness around umbilicus: Visible erythema extending 1.5-2 cm beyond cord base
- Warmth: Mild warmth on palpation of cord area
- Discharge: Small amount of yellowish discharge from cord stump
- Temperature: Slightly elevated at 37.5°C (normal is 37°C, not yet fever)
- Baby's feeding: Slightly reduced (7 times vs expected 8-12)
- Baby's general condition: Otherwise alert and responsive, no fever, no lethargy

Severity Assessment: MODERATE — Not immediately life-threatening but requires same-day PHC evaluation and treatment. Risk of progression to cellulitis or sepsis if untreated.

Why This is Concerning:
- Cord is the most common entry point for infection in first weeks of life
- Even mild infection can spread rapidly in newborns with immature immune systems
- Early treatment with antibiotics prevents progression
- Infection can become life-threatening (sepsis) within 24-48 hours if untreated

MOTHER DANGER SIGNS: None


COUNSELLING PROVIDED TODAY
──────────────────────────
1. CORD INFECTION EXPLANATION: Explained to mother that baby has signs of cord infection (redness, discharge, warmth). Clarified this is NOT mother's fault — common in newborns and easily treated. Emphasized importance of PHC evaluation TODAY.

2. HOME CARE WHILE WAITING: Instructed mother to keep cord dry and clean before going to PHC. No oils or pastes. If discharge increases, gently wipe with clean water.

3. BREASTFEEDING CONTINUATION: Emphasized mother should continue breastfeeding — very important for baby's immune function even during infection treatment.

4. DANGER SIGNS: Taught mother to watch for worsening signs: cord redness spreading, pus increasing, fever, baby becoming lethargic, baby stops feeding. If these occur, go to PHC immediately.

5. MOTHER'S ROLE: Encouraged mother to ask PHC doctor about cord care and treatment plan. Explained PHC will likely prescribe topical or oral antibiotics.


NUTRITION AND DIET ADVICE GIVEN
────────────────────────────────
MOTHER'S DIET: Same as healthy baby visit — warm nourishing foods, good hydration, galactagogues to support immune function through breast milk.

FEEDING: Continue breastfeeding as normal. Frequent breastfeeding supports baby's immune system during infection. At least 8-10 times daily.


REFERRAL DECISION
─────────────────
⚠️ REFERRAL NEEDED: YES

Referral Type: PHC Walk-In, URGENT — SAME DAY

Reason for Referral:
Baby has moderate stage cord infection with redness, warmth, and discharge. This requires PHC evaluation and treatment today. While not currently life-threatening, infection can progress rapidly in newborns. Early treatment with antibiotics prevents serious complications.

Referred To Facility: Mudalur Primary Health Center (PHC)
Facility Address: Main Road, Mudalur Village
Facility Phone: 04656-234567

What Mother Should Bring to PHC:
- This HBNC report
- HBNC card
- Baby (for breastfeeding at facility)
- Any questions about cord care

What to Expect at PHC:
- Doctor will examine baby's cord carefully
- May take a culture or rapid test
- Will likely prescribe antibiotic ointment (for topical application) or oral antibiotics
- Will teach mother proper cord care
- May recommend washings or specific cleaning steps
- Will give instructions on when to return for follow-up

Expected Timeline:
- Baby may be evaluated and sent home today OR
- If doctor wants to observe, may keep for few hours or longer
- Plan for recheck visit with PHC or ASHA in 2-3 days if discharged same day


FOLLOWUP AFTER REFERRAL
───────────────────────
ASHA will follow up tomorrow (16/05) to confirm:
1. Did family reach PHC?
2. What was the diagnosis?
3. What treatment was prescribed?
4. Are there special care instructions?

If baby is discharged same day:
- ASHA will do recheck home visit on 18/05 (Day 5) to assess cord healing
- If cord improving: recheck again on Day 7
- If cord not improving or worsening: refer back to PHC

If baby is kept at PHC:
- Followup depends on PHC decision
- ASHA will connect with mother to plan home care after discharge


MOTHER'S ACKNOWLEDGMENT
──────────────────────
Does mother understand the referral and why baby needs to go to PHC today? YES ✓

Mother's Questions:
- "Will my baby be okay?"
- "Is this my fault?"

Answers Provided:
- Reassured mother that cord infection is common, easily treated, not mother's fault
- Explained that with PHC treatment, baby will be fine
- Emphasized early treatment prevents serious problems

Mother's Agreement: Mother agrees to take baby to PHC today
Mother's Signature: [Priya's signature] / Thumbprint
Date Report Given: 15/05/2026


ASHA NOTES
──────────
Family Cooperation: Very good — Mother cooperative, agreed to PHC referral, will go immediately
Strengths: Mother receptive to advice, willing to follow up, good family support
Challenges: Limited prior knowledge about infection signs, some anxiety about PHC visit
Special Notes: Reassured mother extensively that this is not an emergency (no fever, baby alert) but important same-day visit. Will follow up tomorrow to confirm PHC visit.


═══════════════════════════════════════════════════════════
Report Completed By: Lakshmi Devi, ASHA Worker
Signature: [ASHA signature]  Date: 15/05/2026

⚠️ URGENT REFERRAL — Mother to take baby to PHC TODAY
═══════════════════════════════════════════════════════════
```

---

## Tamil Field Labels for Bilingual Report (Printable)

**Use these exact Tamil labels when creating printed bilingual reports:**

| English Field | Tamil Label |
|---------------|------------|
| VISIT REPORT | ஆய்வு அறிக்கை |
| Visit Date | ஆய்வு நாள் |
| Day of Life | பிறப்பிற்கு நாட்கள் |
| ASHA Worker | ASHA பணியாளர் |
| Baby Name | குழந்தையின் பெயர் |
| Mother Name | தாயின் பெயர் |
| Location | இடம் |
| Birth Weight | பிறப்பு எடை |
| Current Weight | தற்போதைய எடை |
| Temperature | வெப்பநிலை |
| Breathing Rate | சுவாசக் கணக்கு |
| General Appearance | பொதுவான தோற்றம் |
| Feeding Status | பாலூட்டுதல் நிலை |
| Wet Diapers | ஈரமான விரிப்பு |
| Stools | மலம் |
| Skin Color | தோல் நிறம் |
| Jaundice | மஞ்சள் நோய் |
| Cord Status | தொப்புளி நிலை |
| Activity Level | செயல்பாடு நிலை |
| Vaginal Bleeding | யோனி இரத்தப்போக்கு |
| Breast Status | மார்பக நிலை |
| Mood | மனநிலை |
| Danger Signs | ஆபத்து அறிகுறிகள் |
| Counselling Given | கொடுக்கப்பட்ட ஆலோசனை |
| Breastfeeding Advice | தாய்ப்பால் ஆலோசனை |
| Cord Care | தொப்புளி பராமரிப்பு |
| Danger Signs Taught | ஆபத்து அறிகுறிகள் கற்பிப்பு |
| Next Visit Date | அடுத்த வரவு நாள் |
| What to Watch For | கவனிக்க வேண்டியவை |
| When to Come to PHC | PHC வரும் நேரம் |
| Referral Needed | மாற்றுதல் தேவையா |
| Referral Type | மாற்றுதல் வகை |
| Reason for Referral | மாற்றுதல் காரணம் |
| Referral Facility | மாற்றுதல் வசதி |
| Mother Understands | தாய் புரிந்துகொண்டாரா |
| Mother's Signature | தாயின் கையெழுத்து |

---

## Critical Fields That Must NEVER Be Omitted From Any Report

**Regardless of whether the visit is safe, has danger signs, or requires referral, the following fields are MANDATORY in EVERY report:**

1. **Visit Date** — Every report must have a date
2. **Day of Life** — Critical for interpreting findings
3. **Baby's Current Weight** — Essential for tracking growth
4. **Weight Change from Birth** — Shows trend
5. **Temperature** — Always assessed, always documented
6. **Breathing Rate** — Always assessed, always documented
7. **Feeding Status** — Core assessment for every visit
8. **Wet Diapers (24h)** — Best indicator of adequate feeding
9. **Cord Status** — Common infection site, always checked
10. **Danger Signs Assessment** — Explicitly state "None" or list them
11. **Breastfeeding Counselling Provided** — Essential every visit
12. **Next Visit Date** — Mother must know when to return
13. **When to Come to PHC Immediately** — Safety critical
14. **Mother's Acknowledgment** — Document that mother was informed
15. **ASHA Signature and Date** — Accountability and traceability

**Why these fields are critical:**
- They create continuity across visits (next ASHA can see trends)
- They protect baby (danger signs are tracked across visits)
- They protect mother (clear instructions prevent confusion)
- They protect ASHA (documentation shows appropriate care)
- They enable PHC oversight (reports go to health system)

**Never write:** "Will follow up as needed" without a specific date
**Never omit:** Cord status just because it looks normal
**Never forget:** Feeding and weight — these are the foundations of healthy baby growth

---

## Report Generation Rules for the RAG System

When the counselling system generates a visit report, it must:

1. **Always include mandatory fields** — No exceptions
2. **Match tone to outcome** — Reassuring for safe visits, clear and action-oriented for danger signs
3. **Use Tamil terminology consistently** — Every core concept in both languages
4. **Include specific numbers** — Not "baby is good," but "baby has 6 wet diapers and is feeding 8 times daily"
5. **Explain the why** — Not just "go to PHC," but "why baby needs to go"
6. **Provide clear instructions** — What mother should do before visiting PHC, what to bring, what to expect
7. **Document mother's understanding** — Confirm she understands counselling and next steps
8. **Create continuity** — Next ASHA can see previous findings and follow up appropriately

---

## Summary: The Report as the Deliverable

The HBNC Visit Report is more than documentation — it is the primary deliverable to the family and health system. It must be:

- **Complete:** All required fields filled
- **Accurate:** Specific findings, not vague impressions
- **Clear:** Plain language, bilingual, mother understands
- **Actionable:** Mother knows exactly what to do
- **Safe:** No critical danger signs missed
- **Continuous:** Next visit builds on previous findings

The report is the ASHA worker's professional responsibility and the mother's right to know about her baby's health.
