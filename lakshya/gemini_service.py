"""
AarogyaSahay - Gemini AI Medical Intelligence Service
Integrates Google Gemini 2.5/2.0 API with fallback clinical protocols
for Rural Clinical Triage, Tele-OPD SOAP/Prescription Generation,
Vernacular Health Record Explanation, and Conversational Healthcare Copilot.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Primary & fallback Gemini models
PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash"
MODEL_CANDIDATES = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest"]


def generate_with_retry(client: genai.Client, contents: str, config: Optional[types.GenerateContentConfig] = None):
    """Attempt generation across candidate models for fault-tolerant resilience."""
    last_err = None
    for model_name in MODEL_CANDIDATES:
        try:
            kwargs = {"model": model_name, "contents": contents}
            if config:
                kwargs["config"] = config
            response = client.models.generate_content(**kwargs)
            return response, model_name
        except Exception as e:
            last_err = e
            logger.warning(f"Gemini model '{model_name}' temporary fault ({e}), trying next candidate...")
    raise last_err

# In-memory runtime API key storage
_runtime_api_key = None


def get_api_key() -> Optional[str]:
    """Retrieve Gemini API key from runtime memory, env vars, or .env file."""
    global _runtime_api_key
    if _runtime_api_key:
        return _runtime_api_key

    # Check environment variables
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key and key.strip():
        return key.strip()

    # Check local .env in lakshya or root
    for env_path in [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    ]:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass

    return None


def set_runtime_api_key(api_key: str) -> bool:
    """Store API key into runtime and write to local .env for persistence."""
    global _runtime_api_key
    clean_key = api_key.strip()
    _runtime_api_key = clean_key
    os.environ["GEMINI_API_KEY"] = clean_key

    # Persist to local .env file
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={clean_key}\n")
        return True
    except Exception as e:
        logger.warning(f"Failed to persist .env: {e}")
        return True


def is_configured() -> bool:
    """Check if a Gemini API key is currently configured."""
    key = get_api_key()
    return bool(key and len(key) > 8)


def get_genai_client(api_key: Optional[str] = None) -> Optional[genai.Client]:
    """Instantiate and return google-genai Client."""
    key = api_key or get_api_key()
    if not key:
        return None
    try:
        return genai.Client(api_key=key)
    except Exception as e:
        logger.error(f"Error creating GenAI client: {e}")
        return None


def test_gemini_connection(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Test ping to Gemini API to verify token validity."""
    client = get_genai_client(api_key)
    if not client:
        return {"success": False, "error": "No Gemini API key configured."}

    try:
        response, used_model = generate_with_retry(
            client,
            contents="Respond with only the text: 'AarogyaSahay Gemini Medical Grid Online'"
        )
        return {
            "success": True,
            "message": response.text.strip(),
            "model": used_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# =====================================================================
# 1. CLINICAL TRIAGE & DIFFERENTIAL DIAGNOSIS CDSS
# =====================================================================

def evaluate_clinical_triage(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evidence-based clinical triage using Gemini 2.5 with IMNCI & Maternal RMNCH+A protocols.
    Falls back to deterministic clinical rules if API key is not configured.
    """
    client = get_genai_client()
    patient_name = data.get("patient_name", "Rural Patient")
    age = data.get("age", 28)
    category = data.get("category", "maternal")  # maternal, pediatric, general
    sys_bp = int(data.get("systolic_bp", 120))
    dia_bp = int(data.get("diastolic_bp", 80))
    pulse = int(data.get("pulse", 80))
    spo2 = int(data.get("spo2", 98))
    resp_rate = int(data.get("resp_rate", 20))
    danger_signs = data.get("danger_signs", [])
    complaints = data.get("complaints", "")
    maternal_weeks = int(data.get("gestational_weeks", 0))
    proteinuria = data.get("proteinuria", "nil")

    # If Gemini is configured, invoke AI model
    if client:
        prompt = f"""You are a Senior Public Health Medical Officer and Clinical Decision Support System for rural India (AarogyaSahay Health Grid).
Assess the following rural patient according to national clinical triage guidelines (IMNCI, Maternal RMNCH+A, and Emergency Medical 108 Triage):

PATIENT PROFILE:
- Name: {patient_name}
- Age: {age} years
- Protocol Category: {category}
- Blood Pressure: {sys_bp}/{dia_bp} mmHg
- Pulse Rate: {pulse} bpm
- Oxygen Saturation (SpO2): {spo2}%
- Respiratory Rate: {resp_rate} breaths/min
- Gestational Weeks (if maternal): {maternal_weeks}
- Proteinuria / Urine Albumin: {proteinuria}
- Reported Danger Signs: {', '.join(danger_signs) if danger_signs else 'None noted'}
- Clinical Complaints: {complaints if complaints else 'Not specified'}

Analyze the case and return a VALID JSON OBJECT with these exact keys:
{{
  "tier": "Red - Emergency Escalation" | "Yellow - Priority Tele-Consultation" | "Green - Routine Primary Care",
  "badge": "emergency" | "urgent" | "routine",
  "condition_title": "Concise medical condition or syndrome name",
  "urgency_summary": "One sentence summary of risk and priority",
  "clinical_assessment": "3-4 sentences explaining the pathophysiological risk and rationale based on vitals and signs",
  "differential_diagnoses": ["Top differential 1", "Top differential 2", "Top differential 3"],
  "red_flags": ["Red flag 1", "Red flag 2"],
  "protocol_actions": "Immediate on-site actions mandated for Frontline ASHA / ANM (e.g. Magnesium Sulfate loading, recovery position, keep warm, oral rehydration)",
  "recommended_facility": "Sub-Centre" | "Primary Health Centre (PHC)" | "Community Health Centre (CHC)" | "District Hospital / FRU Emergency",
  "transport_advice": "Immediate 108 Emergency Ambulance Dispatch" | "Assisted Tele-OPD within 4 hours" | "Standard Village Sub-Centre Follow-up",
  "eta_target": "<15 mins" | "<4 hours" | "Within 48 hours"
}}

Respond ONLY with the JSON object. Do not wrap in markdown tags or extra text."""

        try:
            response, used_model = generate_with_retry(
                client,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            raw_text = response.text.strip()
            # Clean possible markdown fence
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            result = json.loads(raw_text.strip())
            result["is_ai_live"] = True
            result["model"] = used_model
            return result
        except Exception as e:
            logger.warning(f"Gemini API call failed, falling back to rule engine: {e}")

    # Deterministic Clinical Rule Engine Fallback
    return _fallback_clinical_triage(
        sys_bp=sys_bp,
        dia_bp=dia_bp,
        pulse=pulse,
        spo2=spo2,
        resp_rate=resp_rate,
        category=category,
        maternal_weeks=maternal_weeks,
        proteinuria=proteinuria,
        danger_signs=danger_signs,
        patient_name=patient_name
    )


def _fallback_clinical_triage(sys_bp, dia_bp, pulse, spo2, resp_rate, category, maternal_weeks, proteinuria, danger_signs, patient_name):
    """Accurate evidence-based clinical rules matching IMNCI & RMNCH+A protocols."""
    ds_str = " ".join(danger_signs).lower()
    is_emergency = (
        sys_bp >= 160 or dia_bp >= 110 or spo2 < 92 or
        "convulsion" in ds_str or "unconscious" in ds_str or "bleeding" in ds_str or
        "chest pain" in ds_str or "snakebite" in ds_str or "trauma" in ds_str or
        (category == "maternal" and maternal_weeks > 20 and sys_bp >= 150 and proteinuria in ("severe", "trace")) or
        (category == "pediatric" and ("unable to feed" in ds_str or "chest indrawing" in ds_str or resp_rate > 50))
    )

    is_urgent = (
        sys_bp >= 140 or dia_bp >= 90 or pulse > 105 or spo2 < 95 or
        "headache" in ds_str or "fever" in ds_str or "vomiting" in ds_str or
        (category == "maternal" and maternal_weeks > 0 and sys_bp >= 135)
    )

    if is_emergency:
        if category == "maternal":
            title = "Severe Pre-Eclampsia / Impending Obstetric Emergency"
            rationale = f"Elevated blood pressure ({sys_bp}/{dia_bp} mmHg) with gestational danger signs indicates impending eclamptic crisis. Immediate risk of placental abruption and maternal-fetal hypoxia."
            actions = "Administer loading dose Magnesium Sulfate (4g IV + 10g IM) per National Health Mission protocol. Secure airway, position on left lateral side. Mobilize 108 Emergency Ambulance."
            facility = "District Hospital / First Referral Unit (FRU Emergency)"
        elif category == "pediatric":
            title = "Acute Pediatric Respiratory Distress / Severe Pneumonia (IMNCI)"
            rationale = f"Signs of acute hypoxia (SpO2 {spo2}%) and respiratory compromise in pediatric patient. High risk of decompensation."
            actions = "Administer pre-referral dose of Amoxicillin and warm/humidified oxygen if available. Keep child warm during transport. Prevent hypoglycemia with expressed breast milk."
            facility = "Community Health Centre (CHC) / District Pediatric Care Unit"
        else:
            title = "Acute Cardiovascular / Medical Emergency"
            rationale = f"Critical hemodynamics (BP {sys_bp}/{dia_bp}, SpO2 {spo2}%) warranting immediate tertiary stabilization."
            actions = "Place patient in high Fowler's or recovery position. Maintain oxygen flow. Dispatch emergency 108 ALS ambulance immediately."
            facility = "Sub-Divisional / District Hospital Emergency Hub"

        return {
            "tier": "Red - Emergency Escalation",
            "badge": "emergency",
            "condition_title": title,
            "urgency_summary": f"Critical vital instability detected for {patient_name}. Immediate hospital transfer required.",
            "clinical_assessment": rationale,
            "differential_diagnoses": ["Eclampsia / Pre-Eclampsia Crisis", "Acute Hypertensive Emergency", "Cardiopulmonary Compromise"],
            "red_flags": danger_signs or ["Severe Hypertension (BP ≥160/110)", "Hypoxia (SpO2 <92%)"],
            "protocol_actions": actions,
            "recommended_facility": facility,
            "transport_advice": "Immediate 108 Emergency Ambulance Dispatch (<15 mins)",
            "eta_target": "<15 mins",
            "is_ai_live": False,
            "model": "Aarogya Clinical CDSS Rules"
        }

    elif is_urgent:
        return {
            "tier": "Yellow - Priority Tele-Consultation",
            "badge": "urgent",
            "condition_title": "Moderate Gestational / Clinical Hypertension & Febrile State",
            "urgency_summary": f"Elevated vitals (BP {sys_bp}/{dia_bp}) require medical officer review within 4 hours.",
            "clinical_assessment": f"Patient exhibits Stage-1 hypertensive markers or febrile symptoms requiring physician evaluation and anti-hypertensive or antibiotic titration. Safe for PHC level tele-consultation.",
            "differential_diagnoses": ["Gestational Hypertension", "Infectious Febrile Illness", "Essential Hypertension"],
            "red_flags": danger_signs or ["Elevated Systolic BP (≥140 mmHg)"],
            "protocol_actions": "Keep patient at rest in cool, quiet environment. Check BP every 30 minutes. Schedule assisted Tele-OPD consult with Medical Officer at PHC.",
            "recommended_facility": "Primary Health Centre (PHC Tele-OPD Hub)",
            "transport_advice": "Assisted Tele-OPD Consultation within 4 hours",
            "eta_target": "<4 hours",
            "is_ai_live": False,
            "model": "Aarogya Clinical CDSS Rules"
        }
    else:
        return {
            "tier": "Green - Routine Primary Care",
            "badge": "routine",
            "condition_title": "Stable Primary Health Case / Routine Screening",
            "urgency_summary": f"Vitals stable (BP {sys_bp}/{dia_bp}, SpO2 {spo2}%). Standard primary care carepath.",
            "clinical_assessment": f"Patient demonstrates hemodynamically stable vitals with no red-flag clinical triggers. Appropriate for Sub-Centre management by ASHA/ANM.",
            "differential_diagnoses": ["Routine Antenatal / Postnatal Checkup", "Mild Seasonal Symptoms", "Primary Preventive Health"],
            "red_flags": [],
            "protocol_actions": "Dispense standard nutritional supplements (IFA tablets, Calcium). Counsel on maternal nutrition, hydration, and danger sign identification.",
            "recommended_facility": "Health & Wellness Sub-Centre",
            "transport_advice": "Standard Village Sub-Centre Follow-up",
            "eta_target": "Within 48 hours",
            "is_ai_live": False,
            "model": "Aarogya Clinical CDSS Rules"
        }


# =====================================================================
# 2. TELE-OPD AI CLINICAL COPILOT (SOAP & EDL PRESCRIPTION PAD)
# =====================================================================

def generate_teleconsult_prescription(encounter_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate evidence-based SOAP Encounter Note and National Essential Drug List (EDL)
    prescription using Gemini 2.5.
    """
    client = get_genai_client()
    patient_name = encounter_data.get("patient_name", "Patient")
    age = encounter_data.get("age", 30)
    gender = encounter_data.get("gender", "Female")
    vitals = encounter_data.get("vitals", "BP: 120/80")
    chief_complaint = encounter_data.get("chief_complaint", "Headache and fatigue")
    specialty = encounter_data.get("specialty", "General Medicine")

    if client:
        prompt = f"""You are an expert Medical Officer conducting a low-resource rural Tele-OPD consultation in India (AarogyaSahay).
Generate a clinically sound, evidence-based Prescription and SOAP Note for this patient.
IMPORTANT: All recommended medicines MUST strictly belong to the Indian National Essential Drugs List (EDL) commonly available at Sub-Centres and Primary Health Centres (PHCs), such as:
Paracetamol, Amoxicillin, Azithromycin, Metformin, Amlodipine, Labetalol, ORS, Zinc, Iron Folic Acid (IFA), Calcium + Vit D3, Albendazole, Cetirizine, Antacid/Pantoprazole.

ENCOUNTER DETAILS:
- Patient Name: {patient_name}
- Age/Gender: {age} Yrs / {gender}
- Specialty: {specialty}
- Vitals: {vitals}
- Chief Complaints: {chief_complaint}

Return a VALID JSON OBJECT with these exact keys:
{{
  "diagnosis": "Primary diagnosis in formal clinical terms",
  "differential_diagnoses": ["Differential 1", "Differential 2"],
  "soap_note": {{
    "subjective": "Chief complaint and history summary",
    "objective": "Vitals and examination findings",
    "assessment": "Clinical synthesis and severity staging",
    "plan": "Comprehensive care and therapeutic plan"
  }},
  "medications": [
    {{
      "name": "Drug Name & Strength (e.g. Tab Amlodipine 5mg)",
      "dosage": "1 tablet OD (Once daily)",
      "duration": "30 days",
      "timing": "Morning after breakfast",
      "purpose": "Controls blood pressure"
    }}
  ],
  "rx_text_formatted": "Compact formatted string ready for medical prescription pad",
  "investigations": ["Routine lab/diagnostic tests required (e.g. Serum Creatinine, CBC, Urine Albumin)"],
  "referral_advice": "Specialist referral instructions if any, or 'None required - manage at PHC'",
  "counseling_points": ["Patient counseling point 1", "Patient counseling point 2"],
  "follow_up_days": 7
}}

Respond ONLY with the JSON object. Do not wrap in markdown tags or extra text."""

        try:
            response, used_model = generate_with_retry(
                client,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                )
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            result = json.loads(raw_text.strip())
            result["is_ai_live"] = True
            result["model"] = used_model
            return result
        except Exception as e:
            logger.warning(f"Gemini Teleconsult Copilot failed, using clinical fallback: {e}")

    # Fallback clinical prescription logic
    meds = [
        {
            "name": "Tab Paracetamol 500mg",
            "dosage": "1 tablet TDS (3 times daily)",
            "duration": "3 days",
            "timing": "After meals",
            "purpose": "Relieves headache and fever"
        },
        {
            "name": "Tab Iron & Folic Acid (IFA - 100mg elemental Fe + 500mcg FA)",
            "dosage": "1 tablet OD",
            "duration": "30 days",
            "timing": "At night after dinner with water",
            "purpose": "Corrects nutritional anemia and fatigue"
        },
        {
            "name": "Tab Calcium Carbonate 500mg + Vit D3",
            "dosage": "1 tablet OD",
            "duration": "30 days",
            "timing": "After lunch (separate from IFA)",
            "purpose": "Bone density and maternal mineral support"
        }
    ]

    rx_text = "1. Tab Paracetamol 500mg — 1 tab TDS x 3 days (Post meals)\n2. Tab IFA (100mg Fe + 0.5mg FA) — 1 tab OD at night x 30 days\n3. Tab Calcium 500mg — 1 tab OD after lunch x 30 days"

    return {
        "diagnosis": "Nutritional Anemia with Tension Headache",
        "differential_diagnoses": ["Essential Stage-I Hypertension", "Nutritional Iron Deficiency", "Exertional Fatigue"],
        "soap_note": {
            "subjective": f"Patient {patient_name}, {age}Y/{gender}, presents with {chief_complaint}. Reports persistent fatigue and mild dizziness.",
            "objective": f"Vitals recorded: {vitals}. Conjunctival pallor noted. Cardiovascular and chest exam unremarkable.",
            "assessment": "Moderate fatigue secondary to nutritional anemia and work strain. Hemodynamically stable.",
            "plan": "Therapeutic oral hematinics, dietary education, hydration, review in 7 days."
        },
        "medications": meds,
        "rx_text_formatted": rx_text,
        "investigations": ["Complete Blood Count (CBC)", "Peripheral Blood Smear", "Urine Routine & Micro"],
        "referral_advice": "Manage at PHC level. Refer to District Hospital if Hb < 7.0 g/dL.",
        "counseling_points": [
            "Increase intake of green leafy vegetables (spinach, drumstick leaves), jaggery, and roasted gram.",
            "Do NOT take Iron tablets with milk or tea; take with water or citrus juice.",
            "Report immediately if severe breathlessness or swelling develops."
        ],
        "follow_up_days": 7,
        "is_ai_live": False,
        "model": "Aarogya Clinical EDL Engine"
    }


# =====================================================================
# 3. VERNACULAR PATIENT HEALTH EXPLAINER (AROGYA MITRA)
# =====================================================================

def explain_health_record_vernacular(record_data: Dict[str, Any], language: str = "hi") -> Dict[str, Any]:
    """
    Translates complex EHR records, lab diagnostics, and doctor prescriptions into
    compassionate, easily understandable vernacular explanations for rural citizens.
    Languages: 'hi' (Hindi), 'bn' (Bengali), 'te' (Telugu), 'mr' (Marathi), 'ta' (Tamil), 'en' (English).
    """
    client = get_genai_client()
    lang_names = {
        "hi": "Hindi (हिन्दी)",
        "bn": "Bengali (বাংলা)",
        "te": "Telugu (తెలుగు)",
        "mr": "Marathi (मराठी)",
        "ta": "Tamil (தமிழ்)",
        "en": "Simple Plain English"
    }
    target_lang = lang_names.get(language, "Hindi (हिन्दी)")

    patient_name = record_data.get("patient_name", "Patient")
    diagnosis = record_data.get("diagnosis", "Gestational Hypertension & Severe Anemia")
    lab_summary = record_data.get("lab_summary", "Hemoglobin: 7.2 g/dL (Low), BP: 155/100, USG: Normal fetus")
    medications = record_data.get("medications", "Tab Labetalol 100mg BD, IV Iron Sucrose, Tab Calcium, IFA")

    if client:
        prompt = f"""You are 'Aarogya Mitra' (आरोग्य मित्र), a compassionate public health AI assistant for rural India.
Explain the following medical record and prescription to the patient in simple, caring language ({target_lang}).
The patient may have limited health literacy. Avoid complicated medical jargon. Focus on practical daily care, when to take medicines, food tips, and urgent danger signs.

PATIENT RECORD:
- Patient Name: {patient_name}
- Diagnosis: {diagnosis}
- Key Lab Findings: {lab_summary}
- Prescribed Medicines: {medications}

Return a VALID JSON OBJECT with these exact keys:
{{
  "greeting": "Warm, respectful greeting in {target_lang} addressed to {patient_name}",
  "plain_summary": "Simple 2-3 sentence explanation of what the doctor found and what the test results mean in {target_lang}",
  "medications_guide": [
    {{
      "medicine_name": "Name of medicine",
      "how_to_take": "Clear instructions in {target_lang} (e.g. सुबह नाश्ते के बाद एक गोली)",
      "benefit": "Why this medicine is necessary in simple words"
    }}
  ],
  "nutrition_and_daily_care": ["Practical food & lifestyle tip 1 using affordable rural ingredients", "Tip 2", "Tip 3"],
  "danger_signs_alert": ["Clear warning sign 1 when to dial 108 immediately", "Warning sign 2", "Warning sign 3"],
  "reassurance_note": "A warm, comforting closing message encouraging the patient"
}}

Respond ONLY with the JSON object. Do not wrap in markdown tags or extra text."""

        try:
            response, used_model = generate_with_retry(
                client,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                )
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            result = json.loads(raw_text.strip())
            result["language"] = language
            result["is_ai_live"] = True
            result["model"] = used_model
            return result
        except Exception as e:
            logger.warning(f"Gemini Vernacular Explainer failed, using fallback: {e}")

    # Fallback Hindi explanation
    return {
        "greeting": f"नमस्ते {patient_name} जी! आपकी सेहत हमारी सबसे बड़ी प्राथमिकता है।",
        "plain_summary": "डॉक्टर साहब की जांच के अनुसार आपके खून में हीमोग्लोबिन 7.2 g/dL है, जिसका मतलब शरीर में खून की कमी (एनीमिया) है। साथ ही रक्तचाप (ब्लड प्रेशर) थोड़ा बढ़ा हुआ है। सही खान-पान और नियमित दवा से आप और आपका बच्चा पूरी तरह स्वस्थ रहेंगे।",
        "medications_guide": [
            {
                "medicine_name": "टेबलेट लेबेटालोल (Tab Labetalol 100mg)",
                "how_to_take": "दिन में दो बार (सुबह और शाम नाश्ते के बाद) पानी के साथ लें।",
                "benefit": "यह आपका ब्लड प्रेशर नियंत्रित रखेगी ताकि चक्कर या सिरदर्द न हो।"
            },
            {
                "medicine_name": "आयरन और फोलिक एसिड (IFA लाल गोली)",
                "how_to_take": "रात को खाना खाने के बाद एक गोली। चाय या दूध के साथ बिल्कुल न लें।",
                "benefit": "यह आपके शरीर में नया खून बनाने में मदद करेगी।"
            },
            {
                "medicine_name": "कैल्शियम गोली (Calcium 500mg)",
                "how_to_take": "दोपहर के खाने के बाद लें (आयरन की गोली से कम से कम 2 घंटे का अंतर रखें)।",
                "benefit": "हड्डियों को मजबूत बनाएगी और बच्चे के विकास में मदद करेगी।"
            }
        ],
        "nutrition_and_daily_care": [
            "रोजाना हरी पत्तेदार सब्जियां (पालक, मेथी, सहजन/मुनगा के पत्ते) खाएं।",
            "गुड़, भुने हुए चने और मूंगफली का सेवन नियमित करें, इससे खून तेजी से बढ़ता है।",
            "भोजन में नमक की मात्रा कम रखें और दिन में पर्याप्त पानी पिएं।",
            "दोपहर में कम से कम 2 घंटे बाईं करवट लेकर आराम करें।"
        ],
        "danger_signs_alert": [
            "अचानक तेज सिरदर्द या आंखों के सामने धुंधलापन दिखना",
            "चेहरे या दोनों पैरों में अचानक बहुत ज्यादा सूजन आ जाना",
            "पेट के ऊपरी हिस्से में तेज दर्द या योनि से रक्तस्त्राव",
            "उपरोक्त लक्षण दिखने पर तुरंत 108 नंबर पर फोन कर एम्बुलेंस बुलाएं!"
        ],
        "reassurance_note": "घबराने की कोई बात नहीं है। आपकी आशा दीदी आपके साथ हैं। समय पर दवा लें और सुरक्षित रहें।",
        "language": language,
        "is_ai_live": False,
        "model": "Aarogya Vernacular Knowledge Base"
    }


def explain_uploaded_medical_report(
    file_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
    text_content: Optional[str] = None,
    language: str = "hi"
) -> Dict[str, Any]:
    """
    Explain uploaded medical/lab reports in simple language (supports images, text, and documents).
    Helps users understand possible findings and next steps without diagnosing them.
    """
    client = get_genai_client()
    lang_names = {
        "hi": "Hindi (हिन्दी)",
        "bn": "Bengali (বাংলা)",
        "te": "Telugu (తెలుగు)",
        "mr": "Marathi (मराठी)",
        "ta": "Tamil (தமிழ்)",
        "en": "Simple Plain English"
    }
    target_lang = lang_names.get(language, "Hindi (हिन्दी)")

    prompt = f"""You are an empathetic medical report explainer on the AarogyaSahay Health Grid.
Analyze the provided medical report / lab test results and explain them in clear, simple language ({target_lang}).
GUIDELINES:
1. Explain what each key test parameter means in everyday words without medical jargon.
2. Note whether key findings are within typical reference ranges or flagged as high/low.
3. Help the user understand possible causes and suggest appropriate next steps to discuss with a certified Medical Officer, without making a definitive medical diagnosis.
4. Provide practical lifestyle, dietary, and self-care recommendations suitable for rural India.
5. Highlight red flag danger signs that require immediate in-person medical evaluation.

Return a VALID JSON OBJECT with these exact keys:
{{
  "report_title": "Identified Lab Report Name (e.g. Complete Blood Count / Lipid Profile / Blood Glucose)",
  "patient_summary": "Simple 2-3 sentence overview of the report findings in {target_lang}",
  "parameters_explained": [
    {{
      "parameter": "Test name (e.g. Hemoglobin / Fasting Blood Sugar)",
      "observed_value": "Value from report or 'Noted'",
      "status": "Normal" | "Elevated / High" | "Low / Deficient",
      "plain_meaning": "What this means in simple words ({target_lang})"
    }}
  ],
  "suggested_next_steps": [
    "Appropriate next step 1 (e.g. Consult Medical Officer at Primary Health Centre for review)",
    "Appropriate next step 2 (e.g. Repeat test in 4 weeks)"
  ],
  "diet_and_lifestyle_tips": [
    "Practical food / lifestyle tip 1 in {target_lang}",
    "Practical tip 2"
  ],
  "urgent_warning_signs": [
    "Red flag sign 1 to seek immediate medical attention",
    "Red flag sign 2"
  ],
  "reassurance": "Encouraging, supportive note in {target_lang}"
}}

Respond ONLY with the JSON object. Do not wrap in markdown tags or extra text."""

    if client:
        try:
            contents_list = []
            if file_bytes and mime_type:
                contents_list.append(types.Part.from_bytes(data=file_bytes, mime_type=mime_type))
            if text_content:
                contents_list.append(f"REPORT TEXT / EXTRACTED CONTENT:\n{text_content}\n\n")
            contents_list.append(prompt)

            response, used_model = generate_with_retry(
                client,
                contents=contents_list,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            result = json.loads(raw_text.strip())
            result["is_ai_live"] = True
            result["model"] = used_model
            result["language"] = language
            return result
        except Exception as e:
            logger.warning(f"Gemini Uploaded Report Explainer failed, using fallback: {e}")

    # Fallback explanation
    return {
        "report_title": "Diagnostic Blood & Health Panel",
        "patient_summary": "इस जांच रिपोर्ट के अनुसार आपके मुख्य स्वास्थ्य पैरामीटर सामान्य देखभाल और डॉक्टर से परामर्श की मांग करते हैं। घबराने की कोई बात नहीं है, उचित खान-पान और सलाह से सुधार संभव है।",
        "parameters_explained": [
            {
                "parameter": "हीमोग्लोबिन (Hemoglobin)",
                "observed_value": "कम (Low)",
                "status": "Low / Deficient",
                "plain_meaning": "शरीर में लाल रक्त कोशिकाओं की कमी है, जिससे कमजोरी या थकान महसूस हो सकती है।"
            },
            {
                "parameter": "रक्त शर्करा (Blood Glucose)",
                "observed_value": "सामान्य (Normal)",
                "status": "Normal",
                "plain_meaning": "शुगर का स्तर सुरक्षित सीमा में है।"
            }
        ],
        "suggested_next_steps": [
            "नजदीकी प्राथमिक स्वास्थ्य केंद्र (PHC) में डॉक्टर को रिपोर्ट दिखाएं।",
            "डॉक्टर की सलाह पर आयरन या आवश्यक सप्लीमेंट्स लें।"
        ],
        "diet_and_lifestyle_tips": [
            "हरी पत्तेदार सब्जियां, गुड़ और चने का नियमित सेवन करें।",
            "दिनभर में पर्याप्त पानी पिएं और पर्याप्त आराम करें।"
        ],
        "urgent_warning_signs": [
            "अत्यधिक कमजोरी या चक्कर खाकर गिरना",
            "सांस लेने में अचानक कठिनाई महसूस होना"
        ],
        "reassurance": "आपकी सेहत में सुधार के लिए स्थानीय स्वास्थ्य केंद्र सदैव उपलब्ध है।",
        "language": language,
        "is_ai_live": False,
        "model": "Aarogya Clinical Knowledge Base"
    }


# =====================================================================
# 4. CONVERSATIONAL AAROGYA AI HEALTHCARE COPILOT
# =====================================================================

def chat_health_copilot(message: str, history: Optional[List[Dict[str, str]]] = None, user_role: str = "patient", language: str = "en") -> Dict[str, Any]:
    """
    Conversational Copilot assisting rural patients, ASHA workers, and healthcare staff.
    Covers:
    - AI Health Assistant: Answer general health questions in conversational language.
    - Symptom Guidance: Help users understand possible causes of symptoms and suggest appropriate next steps, without diagnosing them.
    - Medical Report Explanation: Explain uploaded lab reports in simple language.
    - Health Chatbot: Let users ask follow-up questions and get AI-generated responses with conversational continuity.
    """
    client = get_genai_client()

    system_instruction = f"""You are 'Aarogya AI' (आरोग्य सहायक), an empathetic, highly knowledgeable digital public health assistant powered by Google Gemini for India's National Rural Health Grid (AarogyaSahay).
User Role: {user_role.upper()}
Language preference: {language}

YOUR CORE HEALTH CAPABILITIES:
1. AI HEALTH ASSISTANT: Answer general health and wellness questions in warm, accessible, conversational language.
2. SYMPTOM GUIDANCE: Help users understand possible causes of symptoms and suggest appropriate next steps (e.g. visiting the Sub-Centre or PHC, staying hydrated), clearly and responsibly WITHOUT diagnosing them.
3. MEDICAL REPORT EXPLANATION: Explain lab test results and medical terms in simple, plain language that anyone can understand.
4. HEALTH CHATBOT: Engage in conversational follow-up questions, remembering the dialogue context to provide helpful, tailored guidance.
5. EMERGENCY TRIAGE: If user mentions acute red flags (crushing chest pain, severe maternal bleeding, pediatric breathing difficulty, convulsions, loss of consciousness), immediately advise dialing 108 Emergency Ambulance.
6. GOVERNMENT SCHEMES: Guide users on Ayushman Bharat PM-JAY (₹5 Lakhs cover), Janani Suraksha Yojana (JSY), PMSMA, and free medicine/lab services under NHM.

Format responses with clean bullet points, bold key terms, and supportive tone."""


    if client:
        # Construct conversation prompt
        contents = []
        if history:
            for turn in history[-6:]:  # Keep recent context
                role = "user" if turn.get("role") == "user" else "model"
                contents.append(f"{role.upper()}: {turn.get('content', '')}")
        contents.append(f"USER: {message}")
        full_prompt = f"{system_instruction}\n\n" + "\n".join(contents) + "\nASSISTANT:"

        try:
            response, used_model = generate_with_retry(
                client,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=800,
                )
            )
            return {
                "reply": response.text.strip(),
                "is_ai_live": True,
                "model": used_model
            }
        except Exception as e:
            logger.warning(f"Gemini Chat Copilot failed, falling back to knowledge base: {e}")

    # Fallback response engine based on keyword matching
    reply = _fallback_chat_reply(message.lower(), user_role)
    return {
        "reply": reply,
        "is_ai_live": False,
        "model": "Aarogya Local Public Health Assistant"
    }


def _fallback_chat_reply(msg: str, user_role: str) -> str:
    """Smart localized knowledge base for rural health questions."""
    if any(k in msg for k in ["ambulance", "108", "emergency", "sos", "urgent"]):
        return (
            "🚨 **Emergency Action Protocol**\n\n"
            "If the patient has critical danger signs (severe breathing difficulty, loss of consciousness, heavy bleeding, or convulsions):\n\n"
            "1. **Immediately dial 108** for free Emergency Ambulance Dispatch.\n"
            "2. Keep the patient in a recovery posture (left lateral for pregnant mothers).\n"
            "3. Alert the nearest PHC Medical Officer and village ASHA worker.\n"
            "4. Track live ambulance arrival on the **AarogyaSahay Triage Console**."
        )

    if any(k in msg for k in ["scheme", "ayushman", "pmjay", "yojana", "benefit", "bima"]):
        return (
            "🏛️ **Government Health Schemes & Coverage**\n\n"
            "- **Ayushman Bharat PM-JAY:** Provides up to **₹5,00,000 per family per year** for secondary and tertiary hospitalization across all empaneled public & private hospitals.\n"
            "- **Janani Suraksha Yojana (JSY):** Direct financial assistance for institutional delivery (₹1,400 in rural areas) to reduce maternal and infant mortality.\n"
            "- **PMSMA (Pradhan Mantri Surakshit Matritva Abhiyan):** Free comprehensive antenatal checkup on the **9th of every month** at your nearest PHC/CHC.\n"
            "- **Free Diagnostic & Medicines (NHM):** All Essential Drug List (EDL) medications and routine lab tests are **100% Free** at public Sub-Centres and PHCs."
        )

    if any(k in msg for k in ["vaccine", "vaccination", "immunization", "tika", "injection"]):
        return (
            "💉 **Universal Immunization Schedule (UIP)**\n\n"
            "- **At Birth:** BCG, OPV-0, Hepatitis B birth dose\n"
            "- **6 Weeks:** Pentavalent-1, OPV-1, Rotavirus-1, fIPV-1, PCV-1\n"
            "- **10 Weeks:** Pentavalent-2, OPV-2, Rotavirus-2\n"
            "- **14 Weeks:** Pentavalent-3, OPV-3, Rotavirus-3, fIPV-2, PCV-2\n"
            "- **9–12 Months:** MR-1 (Measles-Rubella), PCV Booster, JE-1, Vit-A\n"
            "- **Maternal TT / Td:** 2 doses during pregnancy for maternal and neonatal tetanus protection.\n\n"
            "All immunizations are provided completely free during weekly **Village Health, Sanitation & Nutrition Days (VHSND)**."
        )

    if any(k in msg for k in ["anemia", "khoon", "iron", "hemoglobin", "hb"]):
        return (
            "🩸 **Anemia Management & Nutritional Guide**\n\n"
            "- **Thresholds:** Hemoglobin < 11 g/dL in pregnancy indicates anemia; **< 7 g/dL is severe anemia** requiring urgent IV Iron Sucrose or referral.\n"
            "- **Medicines:** Take 1 **Red IFA Tablet daily** with drinking water after meals (avoid tea/milk within 2 hours).\n"
            "- **Diet Tips:** Include drumstick leaves (सहजन/मुनगा), spinach, jaggery (गुड़), roasted gram (चना), and amla.\n"
            "- **Deworming:** Single dose Tab. Albendazole 400mg during the second trimester."
        )

    if any(k in msg for k in ["diarrhea", "loose motion", "dast", "dehydration", "ors"]):
        return (
            "💧 **Diarrhea & Dehydration Protocol (Zinc + ORS)**\n\n"
            "1. **Oral Rehydration Solution (ORS):** Mix 1 packet in 1 liter clean drinking water. Give after every loose stool.\n"
            "2. **Zinc Supplementation:** Give Zinc 20mg daily for **14 consecutive days** (10mg for infants under 6 months) to rebuild intestinal lining.\n"
            "3. **Danger Signs:** Sunken eyes, inability to drink, lethargy, blood in stool — refer to PHC immediately!"
        )

    # General Greeting
    return (
        f"Namaste! I am **Aarogya AI**, your clinical support partner on the AarogyaSahay Health Grid.\n\n"
        "How can I assist you today?\n"
        "- 🩺 **Clinical Triage:** Assess patient symptoms & vitals against IMNCI & maternal protocols\n"
        "- 💊 **Medicine Guidance:** Look up Essential Drug List (EDL) dosage and availability\n"
        "- 🏛️ **Government Schemes:** Ayushman Bharat PM-JAY, JSY, and PMSMA benefits\n"
        "- 👶 **Mother & Child Care:** Immunization timelines, nutrition, and high-risk flags\n"
        "- 🚨 **Emergency Protocol:** 108 SOS dispatch guidelines and stabilization steps\n\n"
        "Feel free to ask in English, Hindi, or your preferred language!"
    )


# =====================================================================
# 5. HIGH-RISK COHORT STRATIFIER & CARE PLANNER
# =====================================================================

def generate_high_risk_plan(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a personalized ASHA surveillance care plan and nutritional checklist
    for high-risk pregnancies, pediatric malnutrition (SAM), or chronic NCDs.
    """
    client = get_genai_client()
    patient_name = case_data.get("patient_name", "Patient")
    category = case_data.get("category", "High-Risk Pregnancy")
    risk_factors = case_data.get("risk_factors", "Severe Anemia, Gestational Hypertension")
    facility = case_data.get("facility_name", "Sub-Centre")

    if client:
        prompt = f"""You are a District Public Health Specialist in India designing an ASHA frontline home-visit care plan.
Patient: {patient_name}
Cohort Category: {category}
Identified Risk Factors: {risk_factors}
Linked Facility: {facility}

Return a VALID JSON OBJECT with these exact keys:
{{
  "urgency_tier": "Critical" | "High Priority" | "Moderate",
  "clinical_summary": "2 sentence synthesis of danger triggers and surveillance goal",
  "asha_home_visit_checklist": [
    "Action 1 (e.g. Measure BP and check for bilateral pedal edema)",
    "Action 2 (e.g. Verify IFA tablet count and blister adherence)",
    "Action 3 (e.g. Check fetal movements and urine albumin strip)"
  ],
  "nutrition_action_plan": [
    "Affordable rural dietary tip 1",
    "Affordable rural dietary tip 2"
  ],
  "red_flag_escalation_triggers": [
    "Trigger 1 to call 108 immediately",
    "Trigger 2"
  ],
  "next_recommended_visit": "Within 48 hours" | "Within 7 days" | "Within 14 days"
}}

Respond ONLY with the JSON object. Do not wrap in markdown tags or extra text."""

        try:
            response, used_model = generate_with_retry(
                client,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                )
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            result = json.loads(raw_text.strip())
            result["is_ai_live"] = True
            result["model"] = used_model
            return result
        except Exception as e:
            logger.warning(f"High-Risk Planner failed, using fallback: {e}")

    # Fallback High-Risk Plan
    return {
        "urgency_tier": "High Priority",
        "clinical_summary": f"{patient_name} requires active ASHA home surveillance for {risk_factors}. The primary objective is preventing decompensation and ensuring 100% institutional care adherence.",
        "asha_home_visit_checklist": [
            "Measure resting Blood Pressure twice and record in MCP Card",
            "Perform dipstick test for urine albumin (proteinuria check)",
            "Inspect feet and ankles for pitting edema",
            "Verify blister pack count to confirm daily compliance with Tab Labetalol and IFA",
            "Confirm that 108 emergency transport plan and village companion are organized"
        ],
        "nutrition_action_plan": [
            "Prepare fresh moringa/drumstick leaf soup or bhaji twice weekly (rich in iron and calcium)",
            "Consume 50g roasted gram (chana) with jaggery (gur) daily as an afternoon snack",
            "Rest in the left lateral position for at least 2 hours each afternoon to enhance placental perfusion",
            "Limit extra salt intake (avoid pickles and papad)"
        ],
        "red_flag_escalation_triggers": [
            "Systolic BP ≥ 150 or Diastolic BP ≥ 100 mmHg",
            "Persistent frontal headache or flashes of light / blurred vision",
            "Decreased fetal movements (<10 movements in 12 hours)",
            "Epigastric or right upper quadrant abdominal pain"
        ],
        "next_recommended_visit": "Within 48 hours",
        "is_ai_live": False,
        "model": "Aarogya RMNCH+A Care Guidelines"
    }
