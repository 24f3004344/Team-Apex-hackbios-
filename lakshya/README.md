# AarogyaSahay — Integrated Rural Public Health Access Grid
**Team Apex | Rural Healthcare Continuity & Quality Solution**

A comprehensive digital health platform designed specifically for rural, remote, and underserved communities. Rather than replacing the existing public healthcare architecture, it strengthens Sub-Centres, Primary Health Centres (PHCs), Community Health Centres (CHCs), and District Hospitals through digital continuity, assisted teleconsultation, triage, and real-time inventory visibility.

---

## 🌟 Complete Application Architecture & Page Map

The entire suite of modules requested in the problem description is implemented under `lakshya/`:

| Page / Route | Module Name | Key Features & Problem Addressed |
| :--- | :--- | :--- |
| **`/`** | **Landing Page** | High-impact overview, live impact counters, problem-solution matrix, interactive clinical triage screener, live medicine stock search, and ASHA frontline toolkit spotlight. |
| **`/login`** | **Authentication Portal** | Multi-role tabs (ASHA Worker, Doctor, Patient, Admin) with **1-Click Instant Demo Credentials**, OTP simulation, and offline-resilient login. |
| **`/register`** | **Account Onboarding** | Dynamic multi-role registration, automatic ABHA Health ID generation, regional language preference (Hindi, Chhattisgarhi, Odia, Bengali, English). |
| **`/dashboard`** | **Care Coordination Hub** | Logged-in console featuring active Tele-OPD queue, emergency escalations, longitudinal referrals, and local dispensary stock status. |
| **`/teleconsult`** | **Assisted Tele-OPD Hub** | Low-bandwidth video/audio consultation room simulation (2G/EDGE telemetry mode), digital prescription pad with cryptographic signing, and ASHA assisted patient queue. |
| **`/triage`** | **Digital Clinical Triage** | Evidence-based triage protocols (IMNCI & Maternal RMNCH+A) categorizing cases into Green, Yellow, and Red. Direct **108 Emergency Ambulance Dispatch** simulator with live GPS tracking. |
| **`/records`** | **Longitudinal ABHA Records** | Chronological continuum of care with **✨ Aarogya Mitra AI Vernacular Explainer** translating complex lab reports & prescriptions into simple Hindi / regional language. |
| **`/referrals`** | **Closed-Loop Referral Tracking** | 4-stage pipeline (Initiated ➔ In-Transit ➔ Consulted ➔ Closed Loop) ensuring no patient is lost in transit between rural facilities and district hospitals. |
| **`/inventory`** | **Medicine & Lab Availability** | Essential Drug List (EDL) compliance monitor, live stock availability across Sub-Centres and PHCs, and diagnostic test catalog (Free under NHM). |
| **`/high-risk`** | **High-Risk Patient Registry** | Targeted surveillance cohort for High-Risk Pregnancies (HRP), Severe Acute Malnutrition (SAM), and Chronic NCDs with **✨ Gemini AI Home Care Planner**. |
| **`/analytics`** | **Quality & Impact Analytics** | Evidence-based outcomes: 42 min travel time saved, 8.4 min waiting time, 89.4% referral completion rate, and 4.1% stockout frequency. |
| **`/ai-assistant`** | **Aarogya AI Healthcare Copilot** | **Google Gemini 2.5 Flash** conversational health navigator with live voice recognition (Speech-to-Text), text-to-speech audio guidance, multi-role toggles, and government scheme navigator. |

---

## ✨ Google Gemini AI Medical Intelligence Grid

AarogyaSahay is deeply powered by the official **Google GenAI SDK (`google-genai`)** utilizing **Gemini 2.5 Flash**:

1. **Clinical Triage CDSS (`/triage`)**: Evaluates patient hemodynamics and clinical signs against National Health Mission protocols (IMNCI & Maternal RMNCH+A) to identify impending danger signs, tier risks (Green/Yellow/Red), and recommend immediate ASHA on-site stabilization steps.
2. **Tele-OPD Clinical Copilot (`/teleconsult`)**: Formulates comprehensive SOAP Encounter Notes (Subjective, Objective, Assessment, Plan) and auto-populates prescriptions strictly compliant with India's **National Essential Drug List (EDL)**.
3. **Aarogya Mitra Vernacular Explainer (`/records`)**: Transforms confusing medical prescriptions and lab values (e.g. Hemoglobin 7.2 g/dL, USG liquor AFI 12cm) into clear, comforting advice in Hindi, Bengali, Telugu, Marathi, and Tamil with audio read-aloud support.
4. **Conversational Health Copilot (`/ai-assistant`)**: 24/7 multilingual healthcare assistant addressing clinical questions, maternal immunization schedules, and welfare scheme navigation (Ayushman Bharat PM-JAY, JSY, PMSMA).
5. **Zero-Failure Architecture**: Supports direct runtime Gemini API key configuration via in-app modal, environment variable (`GEMINI_API_KEY`), or `.env`. If no key is set or network is offline, it seamlessly falls back to a deterministic clinical protocol engine.

### How to Configure Gemini API Key:
- **Option 1 (Web UI):** Click the **✨ Gemini 2.5** button in the top navigation strip or on `/ai-assistant` and paste your key.
- **Option 2 (Terminal/Environment):**
  ```bash
  export GEMINI_API_KEY="your-gemini-api-key"
  ```
- **Option 3 (.env file):**
  ```bash
  echo "GEMINI_API_KEY=your-gemini-api-key" >> lakshya/.env
  ```

---

## 🎙️ ElevenLabs Lifelike Voice Integration & Healthcare Accessibility

**AarogyaSahay** deeply integrates **ElevenLabs** to make healthcare fundamentally more accessible through natural, human-like voice interaction. 

### Why Voice-Based Interaction in Healthcare?
- **Universal Accessibility:** Overcomes barriers for users with low literacy, elderly patients, or visual impairments who cannot read small medical text or prescription jargon.
- **Conversational Comfort:** Hearing advice in a calm, empathetic, and culturally tuned voice relieves anxiety for rural mothers, expectant parents, and caregivers.
- **Hands-Free Frontline Efficiency:** Frontline ASHA workers can listen to triage recommendations and medication advisories while actively attending to patients.

### Key Capabilities:
1. **Flagship Multilingual Model (`eleven_multilingual_v2`):** Generates realistic conversational speech across Hindi, English, and regional cadences.
2. **Curated Healthcare Personas:**
   - **Rachel (21m00Tcm4TlvDq8ikWAM):** Calm & empathetic — ideal for patient guidance.
   - **Sarah (EXAVITQu4vr4xnSDxMaL):** Warm & gentle maternal caregiver.
   - **Antoni (ErXwobaYiN019PkySvjV):** Reassuring & trustworthy clinical doctor.
   - **Daniel (onwK4e9ZLuTAKqWW03F9):** Authoritative public health advisor.
3. **Omnipresent Voice Support:**
   - **`/ai-assistant`:** Read aloud answers, symptom guidance, and lab explanations.
   - **Floating Copilot Drawer:** 1-click audio playback on all pages.
   - **`/records`:** Vernacular Explainer reads simplified diagnoses and medicine schedules.
4. **Zero-Failure Architecture:** If no ElevenLabs key is configured or when offline, AarogyaSahay automatically falls back to local browser speech synthesis (`hi-IN` / `en-IN`), guaranteeing uninterrupted audio.

### How to Configure ElevenLabs API Key:
- **Option 1 (Web UI Modal):** Click **🎙️ ElevenLabs Voice** in the navigation or on `/ai-assistant` and enter your key.
- **Option 2 (Terminal/Environment):**
  ```bash
  export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
  ```
- **Option 3 (`.env` file):**
  ```bash
  echo "ELEVENLABS_API_KEY=your-elevenlabs-api-key" >> lakshya/.env
  ```

---

## 🚀 Running Locally

From your terminal in the workspace:

```bash
cd lakshya
python3 app.py
```

Open your browser and navigate to: **`http://127.0.0.1:5050`**

---

## 👥 Instant Demo Credentials (1-Click Fill on Login Page)

| Role | Name | Identifier (Phone/Email) | Password | Access Highlights |
| :--- | :--- | :--- | :--- | :--- |
| **Frontline Worker (ASHA)** | Sunita Devi | `9876543210` | `asha123` | Assisted Tele-OPD queue, village high-risk maternal registry, offline sync |
| **Medical Officer (Doctor)** | Dr. Rajesh Sharma | `doctor@swasthya.gov.in` | `doctor123` | Tele-OPD consultation console, triage review, digital e-prescriptions |
| **Rural Citizen / Patient** | Kamla Bai | `9876543212` | `patient123` | ABHA health card, prescription history, medicine availability locator |
| **Facility Administrator** | Anil Verma | `admin@swasthya.gov.in` | `admin123` | PHC queue management, medicine stock indents, referral completion metrics |

---

## 📁 File Structure

```
lakshya/
├── app.py                      # Flask routes, SQLite models, database initialization & seed data
├── requirements.txt            # Dependencies
├── swasthya.db                 # SQLite database storing users, referrals, medicines, teleconsults, high-risk cases
├── templates/
│   ├── base.html               # Shared layout, emergency hotline strip, navigation & footer
│   ├── index.html              # Landing page
│   ├── login.html              # Login page with 1-click test credentials
│   ├── register.html           # Multi-role registration page
│   ├── dashboard.html          # Care coordination dashboard
│   ├── teleconsult.html        # Assisted Tele-OPD consultation room & digital Rx pad
│   ├── triage.html             # Clinical triage screener & 108 Emergency SOS console
│   ├── records.html            # Longitudinal ABHA electronic health records timeline
│   ├── referrals.html          # Closed-loop inter-facility referral tracker
│   ├── inventory.html          # Essential medicines & diagnostic tests availability
│   ├── high_risk.html          # High-risk maternal, child & chronic disease registry
│   └── analytics.html          # District health quality & outcome analytics
└── static/
    ├── css/
    │   └── style.css           # Modern healthcare design system (Vanilla CSS, Glassmorphism)
    └── js/
        └── main.js             # Client-side interactivity, triage evaluator, medicine search & offline sync
```
