import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import user as user_model

auth_bp = Blueprint("auth", __name__)


# =====================================================================
# AUTHENTICATION ROUTES: LOGIN, REGISTER, LOGOUT
# =====================================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Multi-role login with Phone / Email / ABHA ID & Quick-Fill Demo."""
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()
        role_tab = request.form.get("role_tab", "frontline")

        if not identifier or not password:
            flash("Please enter both your identifier (Phone / Email / ABHA) and password.", "danger")
            return render_template("login.html", identifier=identifier, role_tab=role_tab)

        user = user_model.find_by_identifier(identifier)

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


@auth_bp.route("/register", methods=["GET", "POST"])
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
            new_user_id = user_model.create(
                full_name, identifier, role,
                facility_name or "Community Health Sub-Centre",
                district, state, abha_id, language,
                generate_password_hash(password)
            )

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


@auth_bp.route("/logout")
def logout():
    """Clear session and log user out."""
    session.clear()
    flash("You have been safely signed out. Thank you for strengthening community public health.", "info")
    return redirect(url_for("index"))

