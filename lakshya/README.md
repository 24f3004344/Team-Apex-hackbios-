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
| **`/records`** | **Longitudinal ABHA Records** | Chronological continuum of care tracking a patient from Village Sub-Centre ➔ PHC Tele-OPD ➔ District Hospital day-care ➔ Post-discharge ASHA home visit. |
| **`/referrals`** | **Closed-Loop Referral Tracking** | 4-stage pipeline (Initiated ➔ In-Transit ➔ Consulted ➔ Closed Loop) ensuring no patient is lost in transit between rural facilities and district hospitals. |
| **`/inventory`** | **Medicine & Lab Availability** | Essential Drug List (EDL) compliance monitor, live stock availability across Sub-Centres and PHCs, and diagnostic test catalog (Free under NHM). |
| **`/high-risk`** | **High-Risk Patient Registry** | Targeted surveillance cohort for High-Risk Pregnancies (HRP), Severe Acute Malnutrition (SAM), and Chronic NCDs with automated vernacular reminder broadcasts. |
| **`/analytics`** | **Quality & Impact Analytics** | Evidence-based outcomes: 42 min travel time saved, 8.4 min waiting time, 89.4% referral completion rate, and 4.1% stockout frequency. |

---

## 🚀 How to Run the Application

From your terminal in the workspace:

```bash
cd /Users/lakshyaparakh/Documents/Team-Apex-hackbios-/lakshya
python run.py
```

Open your browser and navigate to: **`http://127.0.0.1:5050`**

> Codebase layout is strict MVC: `models/` (SQLite schema + domain queries),
> `views/` (templates + static), `controllers/` (Flask blueprints), `middleware/` (auth).

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
├── run.py                    # Entrypoint: python run.py (http://127.0.0.1:5050)
├── app.py                    # create_app() factory + global template context
├── models/                   # M — SQLite schema, seeds & domain queries
│   ├── database.py           # get_db/close_db + generic row helpers
│   ├── schema.py             # init_db() tables + seed data
│   └── user.py, teleconsult.py, referral.py, medicine.py,
│       diagnostic.py, high_risk_case.py, hospital.py
├── controllers/              # C — Flask blueprints (auth, main, teleconsult,
│   │                           referrals, inventory, high_risk, triage, hospitals)
│   └── __init__.py           # register_routes() + endpoint aliases
├── middleware/               # login_required decorator
│   └── auth_middleware.py
├── views/                    # V
│   ├── templates/            # 17 Jinja pages (base, index, login, register,
│   │                         # dashboard, teleconsult, triage, records, referrals,
│   │                         # inventory, high_risk, analytics, hospitals/*)
│   └── static/               # css/style.css, js (main, translations, hospital-map)
├── requirements.txt          # Dependencies
├── swasthya.db               # SQLite database storing users, referrals, medicines, teleconsults, high-risk cases
├── import_hospitals.py       # One-shot hospital data import script
└── geocode_hospitals.py      # One-shot hospital geocoding script
```
