import sqlite3
from werkzeug.security import generate_password_hash
from .database import DATABASE


def init_db():
    """Create all tables and seed demo data on first launch."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            identifier TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('frontline','doctor','patient','admin')),
            facility_name TEXT,
            district TEXT,
            state TEXT,
            abha_id TEXT,
            language TEXT DEFAULT 'English',
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Referrals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            abha_id TEXT,
            source_facility TEXT NOT NULL,
            target_facility TEXT NOT NULL,
            specialty TEXT NOT NULL,
            urgency TEXT NOT NULL CHECK(urgency IN ('Normal','Urgent','Emergency')),
            status TEXT NOT NULL CHECK(status IN ('Initiated','In-Transit','Consulted','Closed')),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Medicines & Consumables Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            facility_name TEXT NOT NULL,
            district TEXT NOT NULL,
            stock_status TEXT NOT NULL CHECK(stock_status IN ('Available','Low Stock','Out of Stock')),
            units INTEGER NOT NULL DEFAULT 0,
            last_updated TEXT
        )
    """)

    # 4. Teleconsultations / OPD Queue Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teleconsults (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            abha_id TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            asha_worker TEXT,
            doctor_name TEXT,
            specialty TEXT,
            chief_complaint TEXT,
            vitals TEXT,
            priority TEXT CHECK(priority IN ('Routine','Priority','Emergency')),
            status TEXT CHECK(status IN ('In-Queue','In-Session','Completed')),
            prescription TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. High-Risk Patients Table (Maternal, Child, Chronic)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS high_risk_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            abha_id TEXT NOT NULL,
            category TEXT NOT NULL,
            risk_factors TEXT NOT NULL,
            facility_name TEXT NOT NULL,
            asha_worker TEXT NOT NULL,
            next_action_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Monitored','Due Today','Critical')),
            notes TEXT
        )
    """)

    # 6. Diagnostic Tests Availability Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnostics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            category TEXT NOT NULL,
            facility_name TEXT NOT NULL,
            tier TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            turnaround_hrs INTEGER,
            cost_text TEXT DEFAULT 'Free (NHM / Ayushman)'
        )
    """)

    # ---- Seed Data (only on first run) ----
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_users = [
            ("Sunita Devi (ASHA)", "9876543210", "frontline", "Rampur Sub-Centre (PHC Bilaspur)", "Bilaspur", "Chhattisgarh", "91-8832-1102-4411", "Hindi", generate_password_hash("asha123")),
            ("Dr. Rajesh Sharma (MD)", "doctor@swasthya.gov.in", "doctor", "District Hospital & Tele-OPD Hub", "Bilaspur", "Chhattisgarh", "91-4401-9923-8821", "English", generate_password_hash("doctor123")),
            ("Kamla Bai", "9876543212", "patient", "Rampur Village Sub-Centre", "Bilaspur", "Chhattisgarh", "91-4021-8890-1123", "Hindi", generate_password_hash("patient123")),
            ("Anil Verma (PHC Admin)", "admin@swasthya.gov.in", "admin", "Bilaspur Rural Primary Health Centre", "Bilaspur", "Chhattisgarh", "91-5511-7788-3344", "English", generate_password_hash("admin123"))
        ]
        cursor.executemany("INSERT INTO users (full_name, identifier, role, facility_name, district, state, abha_id, language, password_hash) VALUES (?,?,?,?,?,?,?,?,?)", seed_users)

    cursor.execute("SELECT COUNT(*) FROM teleconsults")
    if cursor.fetchone()[0] == 0:
        seed_tele = [
            ("Meena Sahu", "91-3321-4451-0982", 28, "Female", "Sunita Devi (ASHA)", "Dr. Rajesh Sharma", "Obstetrics & Gynaecology", "Severe headache, blurred vision, BP 155/100 at 32 weeks gestational age", "BP: 155/100, Pulse: 94, Hb: 7.2 g/dL", "Priority", "In-Queue", "Awaiting consult"),
            ("Rameshwar Gond", "91-7712-8823-6612", 59, "Male", "Sunita Devi (ASHA)", "Dr. Ananya Sen", "General Medicine / Chest", "Persistent cough for 4 weeks with evening low-grade fever and weight loss", "BP: 128/84, SpO2: 95%, Temp: 100.4°F", "Routine", "In-Session", "Tab. Paracetamol 650mg, Sputum AFB test requisitioned"),
            ("Little Aarav Yadav", "91-6623-1192-3341", 2, "Male", "Kamleshwar (ANM)", "Dr. Vivek Murthy", "Pediatrics & Nutrition", "Child unable to feed, extreme wasting, bilateral pedal edema", "MUAC: 112mm, Weight: 8.1kg", "Emergency", "In-Queue", "Immediate transfer to NRC Bilaspur")
        ]
        cursor.executemany("INSERT INTO teleconsults (patient_name, abha_id, age, gender, asha_worker, doctor_name, specialty, chief_complaint, vitals, priority, status, prescription) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", seed_tele)

    cursor.execute("SELECT COUNT(*) FROM high_risk_cases")
    if cursor.fetchone()[0] == 0:
        seed_high_risk = [
            ("Meena Sahu", "91-3321-4451-0982", "Maternal HRP", "Gestational Hypertension + Severe Anemia (Hb 7.2)", "Rampur Sub-Centre", "Sunita Devi", "Tomorrow, 10:00 AM", "Critical", "Requires IV Iron Sucrose infusion at PHC Bilaspur"),
            ("Sukhi Bai Markam", "91-5509-2211-9876", "Maternal HRP", "Previous Caesarean Section + Breech Presentation (34 Wks)", "Hirri Sub-Centre", "Pramila ANM", "12 Oct 2026", "Due Today", "Planned delivery at Bilaspur District Hospital"),
            ("Baby Aarav", "91-6623-1192-3341", "Pediatric SAM", "Severe Acute Malnutrition with Edema (MUAC < 115mm)", "Kotra Sub-Centre", "Kamleshwar ANM", "Immediate", "Critical", "Nutrition Rehabilitation Centre admission"),
            ("Budhram Netam", "91-1122-8899-4455", "Chronic NCD", "Uncontrolled Type 2 Diabetes (FBS 245 mg/dL) + Diabetic Foot", "Rampur Village", "Sunita Devi", "14 Oct 2026", "Monitored", "Metformin + Glimepiride adherence counseling")
        ]
        cursor.executemany("INSERT INTO high_risk_cases (patient_name, abha_id, category, risk_factors, facility_name, asha_worker, next_action_date, status, notes) VALUES (?,?,?,?,?,?,?,?,?)", seed_high_risk)

    cursor.execute("SELECT COUNT(*) FROM diagnostics")
    if cursor.fetchone()[0] == 0:
        seed_diagnostics = [
            ("Hemoglobin (Hb Meter / Strips)", "Maternal & Child Screening", "Rampur Sub-Centre", "Sub-Centre", 1, 1, "Free (NHM)"),
            ("Rapid Malaria Antigen (RDT)", "Infectious Disease", "Rampur Sub-Centre", "Sub-Centre", 1, 1, "Free (NHM)"),
            ("Blood Glucose (Glucometer)", "NCD Chronic Screening", "Rampur Sub-Centre", "Sub-Centre", 1, 1, "Free (NHM)"),
            ("Urine Protein & Albumin Dipstick", "Maternal Pre-eclampsia", "Rampur Sub-Centre", "Sub-Centre", 1, 1, "Free (NHM)"),
            ("Complete Blood Count (CBC Analyzer)", "Hematology", "Bilaspur Rural PHC", "PHC", 1, 4, "Free (NHM)"),
            ("Sputum Smear for AFB (TB Screening)", "Pulmonology", "Bilaspur Rural PHC", "PHC", 1, 24, "Free (NTEP)"),
            ("Obstetric Ultrasound (USG)", "Fetal Wellbeing", "Bilaspur District Hospital", "District Hospital", 1, 2, "Free (PMMVY / Ayushman)"),
            ("Digital X-Ray Chest", "Radiology", "Bilaspur District Hospital", "District Hospital", 1, 2, "Free (Ayushman)")
        ]
        cursor.executemany("INSERT INTO diagnostics (test_name, category, facility_name, tier, is_available, turnaround_hrs, cost_text) VALUES (?,?,?,?,?,?,?)", seed_diagnostics)

    cursor.execute("SELECT COUNT(*) FROM referrals")
    if cursor.fetchone()[0] == 0:
        seed_referrals = [
            ("Meena Sahu (High-Risk Pregnancy - 32 Wks)", "91-3321-4451-0982", "Rampur Sub-Centre", "Bilaspur District Hospital", "Obstetrics & Gynaecology", "Urgent", "Consulted", "Severe anemia (Hb 7.2) with gestational hypertension."),
            ("Rameshwar Gond (Suspected TB / Chronic Cough)", "91-7712-8823-6612", "Hirri PHC", "District TB Diagnostic Centre", "Pulmonology", "Urgent", "In-Transit", "Continuous cough for 4+ weeks with evening fever."),
            ("Aarav Yadav (Severe Acute Malnutrition - 18 Mo)", "91-6623-1192-3341", "Kotra Sub-Centre", "Nutritional Rehabilitation Centre (NRC)", "Pediatrics", "Emergency", "Initiated", "MUAC < 115mm with bilateral pitting edema.")
        ]
        cursor.executemany("INSERT INTO referrals (patient_name, abha_id, source_facility, target_facility, specialty, urgency, status, notes) VALUES (?,?,?,?,?,?,?,?)", seed_referrals)

    cursor.execute("SELECT COUNT(*) FROM medicines")
    if cursor.fetchone()[0] == 0:
        seed_meds = [
            ("Iron & Folic Acid Tablets (IFA)", "Maternal Health", "Rampur Sub-Centre", "Bilaspur", "Available", 450, "Today, 08:30 AM"),
            ("Amoxicillin Dispersible 250mg", "Child Health / Antibiotics", "Rampur Sub-Centre", "Bilaspur", "Low Stock", 40, "Yesterday"),
            ("Metformin 500mg (NCD Essential)", "Chronic Care", "Bilaspur Rural PHC", "Bilaspur", "Available", 1200, "Today, 09:15 AM"),
            ("Oral Rehydration Salts (ORS)", "Child Health", "Hirri PHC", "Bilaspur", "Available", 680, "Today, 10:00 AM"),
            ("Oxytocin 10 IU Injection", "Maternal Emergency", "Bilaspur Rural PHC", "Bilaspur", "Available", 85, "Today, 07:00 AM"),
            ("Amlodipine 5mg (Hypertension)", "Chronic Care", "Rampur Sub-Centre", "Bilaspur", "Out of Stock", 0, "Needs Replenishment")
        ]
        cursor.executemany("INSERT INTO medicines (name, category, facility_name, district, stock_status, units, last_updated) VALUES (?,?,?,?,?,?,?)", seed_meds)

    conn.commit()
    conn.close()
