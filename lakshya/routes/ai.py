"""
AarogyaSahay - Gemini AI Endpoints & AI Assistant Routes
Provides RESTful APIs for AI Clinical Triage, Tele-OPD Copilot,
Vernacular Health Record Explainer, High-Risk Care Plans, and Live Chat Assistant.
"""

from flask import Blueprint, render_template, request, jsonify, session
import gemini_service

ai_bp = Blueprint("ai", __name__)


# =====================================================================
# AI SYSTEM STATUS & CONFIGURATION
# =====================================================================

@ai_bp.route("/api/ai/status", methods=["GET"])
def api_ai_status():
    """Return current Gemini API connectivity status and active model."""
    configured = gemini_service.is_configured()
    key = gemini_service.get_api_key()
    masked_key = ""
    if key and len(key) > 8:
        masked_key = f"{key[:4]}...{key[-4:]}"

    return jsonify({
        "success": True,
        "configured": configured,
        "primary_model": gemini_service.PRIMARY_MODEL,
        "fallback_model": gemini_service.FALLBACK_MODEL,
        "masked_key": masked_key,
        "status_text": "Gemini 2.5 Active (Online)" if configured else "Gemini Ready (Demonstration & CDSS Rules Active)"
    })


@ai_bp.route("/api/ai/set-key", methods=["POST"])
def api_ai_set_key():
    """Configure or update the Gemini API key dynamically."""
    data = request.get_json() or {}
    api_key = data.get("api_key", "").strip()

    if not api_key:
        return jsonify({"success": False, "error": "API key cannot be empty."}), 400

    # Test the key before saving
    test_result = gemini_service.test_gemini_connection(api_key)
    if not test_result.get("success"):
        return jsonify({
            "success": False,
            "error": f"Invalid Gemini API key or connection error: {test_result.get('error')}"
        }), 400

    gemini_service.set_runtime_api_key(api_key)
    session["gemini_configured"] = True

    return jsonify({
        "success": True,
        "message": f"Gemini API key verified successfully! Connected to {test_result.get('model')}.",
        "model": test_result.get("model")
    })


# =====================================================================
# 1. AI CLINICAL TRIAGE CDSS
# =====================================================================

@ai_bp.route("/api/ai/triage", methods=["POST"])
def api_ai_triage():
    """Execute AI Clinical Triage using Gemini 2.5 with IMNCI / RMNCH+A protocols."""
    data = request.get_json() or {}
    try:
        result = gemini_service.evaluate_clinical_triage(data)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =====================================================================
# 2. AI TELE-OPD PRESCRIPTION & SOAP COPILOT
# =====================================================================

@ai_bp.route("/api/ai/soap-prescription", methods=["POST"])
def api_ai_soap_prescription():
    """Generate evidence-based SOAP encounter notes and Essential Drug List prescription."""
    data = request.get_json() or {}
    try:
        result = gemini_service.generate_teleconsult_prescription(data)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =====================================================================
# 3. AI VERNACULAR PATIENT HEALTH EXPLAINER
# =====================================================================

@ai_bp.route("/api/ai/explain-record", methods=["POST"])
def api_ai_explain_record():
    """Translate complex EHR record, lab values, and prescription into simple regional language."""
    data = request.get_json() or {}
    language = data.get("language", "hi")
    try:
        result = gemini_service.explain_health_record_vernacular(data, language=language)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/upload-report-explain", methods=["POST"])
def api_ai_upload_report_explain():
    """Analyze uploaded medical/lab report file (image/PDF) or text and explain in plain language."""
    language = request.form.get("language") or "hi"
    text_content = request.form.get("text_content", "").strip()

    file_bytes = None
    mime_type = None

    if "report_file" in request.files:
        f = request.files["report_file"]
        if f and f.filename:
            file_bytes = f.read()
            mime_type = f.mimetype or "image/jpeg"

    # Also check if submitted as JSON
    if not file_bytes and not text_content and request.is_json:
        data = request.get_json() or {}
        text_content = data.get("text_content", "")
        language = data.get("language", language)

    try:
        result = gemini_service.explain_uploaded_medical_report(
            file_bytes=file_bytes,
            mime_type=mime_type,
            text_content=text_content,
            language=language
        )
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



# =====================================================================
# 4. CONVERSATIONAL AAROGYA AI COPILOT
# =====================================================================

@ai_bp.route("/api/ai/chat", methods=["POST"])
def api_ai_chat():
    """Process natural language clinical & public health queries."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])
    user_role = session.get("user_role") or data.get("role") or "patient"
    language = data.get("language", "en")

    if not message:
        return jsonify({"success": False, "error": "Message cannot be empty."}), 400

    try:
        response = gemini_service.chat_health_copilot(
            message=message,
            history=history,
            user_role=user_role,
            language=language
        )
        return jsonify({"success": True, **response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =====================================================================
# 5. HIGH-RISK CARE SURVEILLANCE PLANNER
# =====================================================================

@ai_bp.route("/api/ai/high-risk-plan", methods=["POST"])
def api_ai_high_risk_plan():
    """Generate personalized ASHA surveillance checklist and rural nutritional plan."""
    data = request.get_json() or {}
    try:
        result = gemini_service.generate_high_risk_plan(data)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =====================================================================
# DEDICATED FULL-PAGE AI HEALTHCARE ASSISTANT
# =====================================================================

@ai_bp.route("/ai-assistant")
def ai_assistant_page():
    """Full-page interactive Aarogya AI Healthcare Copilot portal."""
    return render_template("ai_assistant.html")
