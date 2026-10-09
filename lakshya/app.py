import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    g
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "swasthya-setu-secure-secret-key-2026")

DATABASE = os.path.join(os.path.dirname(__file__), "swasthya.db")


# =====================================================================
# DATABASE CONNECTION MANAGEMENT (Optimized: per-request connection pool)
# =====================================================================
# BUG FIX: Previous get_db() created a new connection on every call,
# leaking connections across context_processor + route handlers.
# Now uses Flask's `g` object for one connection per request, auto-closed.

def get_db():
    """Get or create a database connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")       # Better concurrent read perf
        g.db.execute("PRAGMA foreign_keys=ON")         # Enforce referential integrity
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Automatically close DB connection when the request ends."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


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


# Initialize database upon startup
init_db()


# =====================================================================
# AUTH MIDDLEWARE
# =====================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access your healthcare portal.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_global_data():
    """Inject current_user into all templates (uses per-request DB)."""
    current_user = None
    if "user_id" in session:
        db = get_db()
        current_user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    return dict(current_user=current_user)


# =====================================================================
# CRUD ROUTES: LANDING, AUTH, DASHBOARD
# =====================================================================

@app.route("/")
def index():
    """Landing Page."""
    return render_template("index.html")


# ----- CREATE (User) + READ (User for auth) -----
@app.route("/login", methods=["GET", "POST"])
def login():
    """Multi-role login with Phone / Email / ABHA ID & Quick-Fill Demo."""
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()
        role_tab = request.form.get("role_tab", "frontline")

        if not identifier or not password:
            flash("Please enter both your identifier (Phone / Email / ABHA) and password.", "danger")
            return render_template("login.html", identifier=identifier, role_tab=role_tab)

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE identifier = ? OR abha_id = ?",
            (identifier, identifier)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_role"] = user["role"]
            session["facility_name"] = user["facility_name"]
            flash(f"Welcome back, {user['full_name']}! Connected to {user['facility_name'] or 'National Health Grid'}.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Use Quick-Demo credentials below for instant access.", "danger")
            return render_template("login.html", identifier=identifier, role_tab=role_tab)

    return render_template("login.html")


# ----- CREATE (User) -----
@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page for Frontline Workers, Doctors, Patients & Facility Admins."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        identifier = request.form.get("identifier", "").strip()
        role = request.form.get("role", "patient").strip()
        facility_name = request.form.get("facility_name", "").strip()
        district = request.form.get("district", "Bilaspur").strip()
        state = request.form.get("state", "Chhattisgarh").strip()
        abha_id = request.form.get("abha_id", "").strip()
        language = request.form.get("language", "Hindi").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # Validate role whitelist
        if role not in ("frontline", "doctor", "patient", "admin"):
            flash("Invalid role selected.", "danger")
            return render_template("register.html", form_data=request.form)

        if not full_name or not identifier or not password:
            flash("Please complete all required fields (Name, Phone/Email, Password).", "danger")
            return render_template("register.html", form_data=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html", form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match. Please verify and re-enter.", "danger")
            return render_template("register.html", form_data=request.form)

        if not abha_id:
            abha_id = f"91-{datetime.now().strftime('%m%d')}-{identifier[-4:] if len(identifier) >= 4 else '1092'}-7721"

        try:
            db = get_db()
            db.execute("""
                INSERT INTO users (full_name, identifier, role, facility_name, district, state, abha_id, language, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                full_name, identifier, role,
                facility_name or "Community Health Sub-Centre",
                district, state, abha_id, language,
                generate_password_hash(password)
            ))
            db.commit()
            new_user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            session["user_id"] = new_user_id
            session["user_name"] = full_name
            session["user_role"] = role
            session["facility_name"] = facility_name or "Community Health Sub-Centre"

            flash(f"Account successfully registered! Your Digital Health Profile (ABHA: {abha_id}) is active.", "success")
            return redirect(url_for("dashboard"))

        except sqlite3.IntegrityError:
            flash("An account with this Mobile Number / Email already exists. Please login instead.", "warning")
            return render_template("register.html", form_data=request.form)
        except Exception as e:
            flash(f"Registration error: {str(e)}", "danger")
            return render_template("register.html", form_data=request.form)

    return render_template("register.html")


# ----- READ (Dashboard aggregation) -----
@app.route("/dashboard")
@login_required
def dashboard():
    """Integrated Care Portal."""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    referrals = db.execute("SELECT * FROM referrals ORDER BY id DESC").fetchall()
    medicines = db.execute("SELECT * FROM medicines ORDER BY stock_status ASC, units ASC").fetchall()
    teleconsults = db.execute("SELECT * FROM teleconsults ORDER BY CASE priority WHEN 'Emergency' THEN 1 WHEN 'Priority' THEN 2 ELSE 3 END, id ASC").fetchall()
    high_risk_cases = db.execute("SELECT * FROM high_risk_cases ORDER BY CASE status WHEN 'Critical' THEN 1 WHEN 'Due Today' THEN 2 ELSE 3 END, id ASC").fetchall()

    return render_template("dashboard.html", user=user, referrals=referrals, medicines=medicines, teleconsults=teleconsults, high_risk_cases=high_risk_cases)


# =====================================================================
# CRUD ROUTES: TELECONSULT (CREATE, READ, UPDATE, DELETE)
# =====================================================================

# ----- CREATE + READ -----
@app.route("/teleconsult", methods=["GET", "POST"])
def teleconsult():
    """Assisted Teleconsultation & Tele-OPD Hub."""
    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        abha_id = request.form.get("abha_id", "").strip()
        age = request.form.get("age", 30, type=int)
        gender = request.form.get("gender", "Female")
        specialty = request.form.get("specialty", "General Medicine")
        chief_complaint = request.form.get("chief_complaint", "").strip()
        vitals = request.form.get("vitals", "BP: 120/80").strip()
        priority = request.form.get("priority", "Routine")

        if not patient_name or not chief_complaint:
            flash("Patient name and chief complaint are required.", "danger")
            return redirect(url_for("teleconsult"))

        if priority not in ("Routine", "Priority", "Emergency"):
            priority = "Routine"

        db = get_db()
        db.execute("""
            INSERT INTO teleconsults (patient_name, abha_id, age, gender, asha_worker, doctor_name, specialty, chief_complaint, vitals, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'In-Queue')
        """, (
            patient_name, abha_id or f"91-{datetime.now().strftime('%m%d')}-0000-0000",
            age, gender, session.get("user_name", "Frontline Worker"),
            "Dr. Rajesh Sharma (MO Bilaspur)", specialty,
            chief_complaint, vitals, priority
        ))
        db.commit()
        flash(f"Patient {patient_name} added to Tele-OPD Queue with priority: {priority}.", "success")
        return redirect(url_for("teleconsult"))

    db = get_db()
    queue = db.execute("SELECT * FROM teleconsults ORDER BY CASE priority WHEN 'Emergency' THEN 1 WHEN 'Priority' THEN 2 ELSE 3 END, id DESC").fetchall()
    return render_template("teleconsult.html", queue=queue)


# ----- UPDATE (Teleconsult status & prescription) -----
@app.route("/api/teleconsult/<int:tc_id>/update", methods=["POST"])
def api_teleconsult_update(tc_id):
    data = request.get_json() or {}
    status = data.get("status", "").strip()
    prescription = data.get("prescription", "").strip()

    if status and status not in ("In-Queue", "In-Session", "Completed"):
        return jsonify({"success": False, "error": "Invalid status value"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM teleconsults WHERE id = ?", (tc_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Teleconsult not found"}), 404

    updates, params = [], []
    if status:
        updates.append("status = ?")
        params.append(status)
    if prescription:
        updates.append("prescription = ?")
        params.append(prescription)

    if updates:
        params.append(tc_id)
        db.execute(f"UPDATE teleconsults SET {', '.join(updates)} WHERE id = ?", params)
        db.commit()

    return jsonify({"success": True, "message": f"Teleconsult #{tc_id} updated"})


# ----- DELETE (Teleconsult) -----
@app.route("/api/teleconsult/<int:tc_id>/delete", methods=["POST"])
def api_teleconsult_delete(tc_id):
    db = get_db()
    existing = db.execute("SELECT id FROM teleconsults WHERE id = ?", (tc_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Teleconsult not found"}), 404

    db.execute("DELETE FROM teleconsults WHERE id = ?", (tc_id,))
    db.commit()
    return jsonify({"success": True, "message": f"Teleconsult #{tc_id} removed from queue"})


# =====================================================================
# CRUD: TRIAGE (READ-only, computed via API)
# =====================================================================

@app.route("/triage")
def triage_page():
    """Comprehensive Digital Clinical Triage & Emergency Escalation Hub."""
    return render_template("triage.html")


# =====================================================================
# CRUD: PATIENT RECORDS (READ)
# =====================================================================

@app.route("/records")
def records_page():
    """Longitudinal Patient Records / ABHA Unified Medical Journey."""
    abha_query = request.args.get("abha", "91-3321-4451-0982").strip()
    return render_template("records.html", active_abha=abha_query)


# =====================================================================
# CRUD ROUTES: REFERRALS (CREATE, READ, UPDATE, DELETE)
# =====================================================================

# ----- CREATE + READ -----
@app.route("/referrals", methods=["GET", "POST"])
def referrals_page():
    """Closed-Loop Referral Tracking & Inter-Facility Handover."""
    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        abha_id = request.form.get("abha_id", "").strip()
        source_facility = request.form.get("source_facility", "").strip()
        target_facility = request.form.get("target_facility", "").strip()
        specialty = request.form.get("specialty", "").strip()
        urgency = request.form.get("urgency", "Urgent").strip()
        notes = request.form.get("notes", "").strip()

        if not patient_name or not source_facility or not target_facility or not specialty:
            flash("Patient name, source/target facility, and specialty are all required.", "danger")
            return redirect(url_for("referrals_page"))

        if urgency not in ("Normal", "Urgent", "Emergency"):
            urgency = "Urgent"

        db = get_db()
        db.execute("""
            INSERT INTO referrals (patient_name, abha_id, source_facility, target_facility, specialty, urgency, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, 'Initiated', ?)
        """, (patient_name, abha_id or f"91-{datetime.now().strftime('%m%d')}-0000-0000", source_facility, target_facility, specialty, urgency, notes))
        db.commit()
        flash(f"Referral successfully initiated for {patient_name} to {target_facility}!", "success")
        return redirect(url_for("referrals_page"))

    db = get_db()
    referrals = db.execute("SELECT * FROM referrals ORDER BY id DESC").fetchall()
    return render_template("referrals.html", referrals=referrals)


# ----- UPDATE (Referral status) -----
@app.route("/api/referral/<int:ref_id>/update", methods=["POST"])
def api_referral_update(ref_id):
    data = request.get_json() or {}
    new_status = data.get("status", "").strip()

    if new_status not in ("Initiated", "In-Transit", "Consulted", "Closed"):
        return jsonify({"success": False, "error": "Invalid status. Must be Initiated, In-Transit, Consulted, or Closed."}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM referrals WHERE id = ?", (ref_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Referral not found"}), 404

    db.execute("UPDATE referrals SET status = ? WHERE id = ?", (new_status, ref_id))
    db.commit()
    return jsonify({"success": True, "message": f"Referral #{ref_id} status updated to {new_status}"})


# ----- DELETE (Referral) -----
@app.route("/api/referral/<int:ref_id>/delete", methods=["POST"])
def api_referral_delete(ref_id):
    db = get_db()
    existing = db.execute("SELECT id FROM referrals WHERE id = ?", (ref_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Referral not found"}), 404

    db.execute("DELETE FROM referrals WHERE id = ?", (ref_id,))
    db.commit()
    return jsonify({"success": True, "message": f"Referral #{ref_id} deleted"})


# =====================================================================
# CRUD ROUTES: INVENTORY — Medicines (CREATE, READ, UPDATE, DELETE)
# =====================================================================

@app.route("/inventory")
def inventory_page():
    """Live Medicine & Diagnostic Tests Inventory Management."""
    db = get_db()
    medicines = db.execute("SELECT * FROM medicines ORDER BY stock_status ASC, name ASC").fetchall()
    diagnostics = db.execute("SELECT * FROM diagnostics ORDER BY tier ASC, test_name ASC").fetchall()
    return render_template("inventory.html", medicines=medicines, diagnostics=diagnostics)


# ----- UPDATE (Medicine stock) -----
@app.route("/api/medicine/<int:med_id>/update", methods=["POST"])
def api_medicine_update(med_id):
    data = request.get_json() or {}
    units = data.get("units")
    stock_status = data.get("stock_status", "").strip()

    db = get_db()
    existing = db.execute("SELECT id FROM medicines WHERE id = ?", (med_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Medicine not found"}), 404

    updates, params = [], []
    if units is not None:
        units = int(units)
        updates.append("units = ?")
        params.append(units)
        # Auto-compute stock_status from units if not explicitly provided
        if not stock_status:
            if units == 0:
                stock_status = "Out of Stock"
            elif units < 50:
                stock_status = "Low Stock"
            else:
                stock_status = "Available"

    if stock_status:
        if stock_status not in ("Available", "Low Stock", "Out of Stock"):
            return jsonify({"success": False, "error": "Invalid stock_status"}), 400
        updates.append("stock_status = ?")
        params.append(stock_status)

    updates.append("last_updated = ?")
    params.append(datetime.now().strftime("%d %b %Y, %I:%M %p"))

    if updates:
        params.append(med_id)
        db.execute(f"UPDATE medicines SET {', '.join(updates)} WHERE id = ?", params)
        db.commit()

    return jsonify({"success": True, "message": f"Medicine #{med_id} stock updated"})


# ----- DELETE (Medicine) -----
@app.route("/api/medicine/<int:med_id>/delete", methods=["POST"])
def api_medicine_delete(med_id):
    db = get_db()
    existing = db.execute("SELECT id FROM medicines WHERE id = ?", (med_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Medicine not found"}), 404

    db.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
    db.commit()
    return jsonify({"success": True, "message": f"Medicine #{med_id} removed from inventory"})


# =====================================================================
# CRUD ROUTES: HIGH-RISK PATIENTS (READ, UPDATE, DELETE)
# =====================================================================

@app.route("/high-risk")
def high_risk_page():
    """High-Risk Patient Follow-up for Maternal, Child & Chronic Conditions."""
    db = get_db()
    cases = db.execute("SELECT * FROM high_risk_cases ORDER BY CASE status WHEN 'Critical' THEN 1 WHEN 'Due Today' THEN 2 ELSE 3 END, id ASC").fetchall()
    return render_template("high_risk.html", cases=cases)


# ----- UPDATE (High-Risk case status & notes) -----
@app.route("/api/high-risk/<int:case_id>/update", methods=["POST"])
def api_high_risk_update(case_id):
    data = request.get_json() or {}
    status = data.get("status", "").strip()
    notes = data.get("notes", "").strip()
    next_action_date = data.get("next_action_date", "").strip()

    if status and status not in ("Monitored", "Due Today", "Critical"):
        return jsonify({"success": False, "error": "Invalid status"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM high_risk_cases WHERE id = ?", (case_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "High-risk case not found"}), 404

    updates, params = [], []
    if status:
        updates.append("status = ?")
        params.append(status)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if next_action_date:
        updates.append("next_action_date = ?")
        params.append(next_action_date)

    if updates:
        params.append(case_id)
        db.execute(f"UPDATE high_risk_cases SET {', '.join(updates)} WHERE id = ?", params)
        db.commit()

    return jsonify({"success": True, "message": f"High-risk case #{case_id} updated"})


# ----- DELETE (High-Risk case) -----
@app.route("/api/high-risk/<int:case_id>/delete", methods=["POST"])
def api_high_risk_delete(case_id):
    db = get_db()
    existing = db.execute("SELECT id FROM high_risk_cases WHERE id = ?", (case_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "High-risk case not found"}), 404

    db.execute("DELETE FROM high_risk_cases WHERE id = ?", (case_id,))
    db.commit()
    return jsonify({"success": True, "message": f"High-risk case #{case_id} removed"})


# =====================================================================
# CRUD: ANALYTICS (READ — computed)
# =====================================================================

@app.route("/analytics")
def analytics_page():
    """Public Health Facility Quality & Impact Dashboard."""
    return render_template("analytics.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been safely signed out. Thank you for strengthening community public health.", "info")
    return redirect(url_for("index"))


# =====================================================================
# API ENDPOINTS (Search & Triage — READ operations)
# =====================================================================

@app.route("/api/medicine-search")
def api_medicine_search():
    query = request.args.get("q", "").strip()
    district = request.args.get("district", "").strip()

    db = get_db()
    sql = "SELECT * FROM medicines WHERE 1=1"
    params = []
    if query:
        sql += " AND (name LIKE ? OR category LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if district:
        sql += " AND district LIKE ?"
        params.append(f"%{district}%")
    sql += " LIMIT 15"
    results = [dict(row) for row in db.execute(sql, params).fetchall()]

    return jsonify({"success": True, "count": len(results), "medicines": results})


@app.route("/api/triage-evaluate", methods=["POST"])
def api_triage_evaluate():
    data = request.get_json() or {}
    fever = data.get("fever", False)
    breathing = data.get("breathing_difficulty", False)
    systolic_bp = int(data.get("systolic_bp", 120))
    maternal_weeks = int(data.get("maternal_weeks", 0))
    pediatric_age = int(data.get("pediatric_age", 99))

    if breathing or (maternal_weeks > 20 and systolic_bp >= 160) or (pediatric_age < 5 and fever and breathing):
        tier = "Red - Emergency Escalation"
        action = "Immediate 108 Ambulance Dispatch & Alert District Emergency Hub. Keep patient in recovery posture."
        badge = "emergency"
        facility = "Sub-Divisional Hospital / District Emergency"
    elif systolic_bp >= 140 or fever or (maternal_weeks > 0 and systolic_bp >= 135):
        tier = "Yellow - Priority Tele-Consultation"
        action = "Schedule Assisted Tele-OPD within 4 hours. Connect with Medical Officer at Primary Health Centre."
        badge = "urgent"
        facility = "Primary Health Centre (PHC Tele-OPD)"
    else:
        tier = "Green - Routine Primary Care & Counseling"
        action = "Manage at Sub-Centre via ASHA/ANM protocol. Dispense essential supplements and schedule follow-up."
        badge = "routine"
        facility = "Health & Wellness Sub-Centre"

    return jsonify({
        "tier": tier, "action": action, "badge": badge,
        "facility": facility,
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p")
    })


# =====================================================================
# ENTRYPOINT
# =====================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting AarogyaSahay Health Grid on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
