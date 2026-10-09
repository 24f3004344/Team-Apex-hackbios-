"""MVC smoke test: structure + endpoints + pages. Run: python test_smoke.py (from lakshya/)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE = os.path.dirname(os.path.abspath(__file__))


def test_structure():
    for p in ["models/__init__.py", "models/database.py", "models/schema.py",
              "models/user.py", "models/hospital.py",
              "controllers/__init__.py", "controllers/auth_controller.py",
              "controllers/hospitals_controller.py",
              "views/templates/base.html", "views/templates/hospitals/list.html",
              "views/static/css/style.css", "views/static/js/main.js",
              "middleware/auth_middleware.py", "run.py"]:
        assert os.path.exists(os.path.join(BASE, p)), f"missing {p}"
    assert not os.path.exists(os.path.join(BASE, "db.py")), "old db.py still present"
    assert not os.path.exists(os.path.join(BASE, "routes")), "old routes/ still present"


def test_url_map():
    from app import app
    rules = {r.endpoint for r in app.url_map.iter_rules()}
    for ep in ["index", "dashboard", "login", "register", "logout", "teleconsult",
               "triage_page", "records_page", "referrals_page", "inventory_page",
               "high_risk_page", "analytics_page",
               "hospitals.list_hospitals", "hospitals.hospital_detail"]:
        assert ep in rules, f"endpoint missing: {ep}"


def test_routes():
    from app import app
    c = app.test_client()
    # Public surface (logged out)
    for path in ["/", "/login", "/register", "/static/css/style.css"]:
        assert c.get(path).status_code == 200, f"GET {path} failed"
    r = c.get("/api/medicine-search?q=ORS")
    assert r.status_code == 200 and r.get_json()["count"] >= 1
    r = c.post("/api/triage-evaluate", json={"breathing_difficulty": True})
    assert r.status_code == 200 and "Red" in r.get_json()["tier"]
    # Logged in: every app page renders
    c.post("/login", data={"identifier": "9876543210", "password": "asha123", "role_tab": "frontline"})
    for path in ["/dashboard", "/teleconsult", "/triage", "/records", "/referrals",
                 "/inventory", "/high-risk", "/analytics", "/hospitals/", "/hospitals/1",
                 "/hospitals/api/stats"]:
        assert c.get(path).status_code == 200, f"GET {path} failed (logged in)"


def test_login_gating():
    """Logged-out users get bounced to /login on every app page/API (except landing + auth + 2 public read APIs)."""
    from app import app
    c = app.test_client()
    locked = ["/dashboard", "/teleconsult", "/triage", "/records", "/referrals",
              "/inventory", "/high-risk", "/analytics", "/hospitals/", "/hospitals/1",
              "/hospitals/api/stats",
              "/api/medicine/1/update", "/api/medicine/1/delete",
              "/api/high-risk/1/update", "/api/teleconsult/1/update",
              "/api/referral/1/update"]
    for path in locked:
        r = c.get(path) if "update" not in path and "delete" not in path else c.post(path, json={})
        assert r.status_code == 302, f"{path} not gated (got {r.status_code})"
        assert "/login" in r.headers.get("Location", ""), f"{path} bounce target wrong"
    # Public surface stays open
    for path in ["/", "/login", "/register", "/static/css/style.css"]:
        assert c.get(path).status_code == 200, f"public {path} broke"
    assert c.get("/api/medicine-search?q=ORS").status_code == 200
    assert c.post("/api/triage-evaluate", json={"breathing_difficulty": True}).status_code == 200


def test_security_fixes():
    """Regression: admin self-register blocked, crash guards, no hardcoded secret."""
    from app import app
    import models
    assert app.secret_key != "swasthya-setu-secure-secret-key-2026", "hardcoded SECRET_KEY still in use"
    c = app.test_client()
    # 1. admin self-registration must be rejected (re-render, no redirect, no DB row)
    r = c.post("/register", data={"full_name": "Evil", "identifier": "9999999999",
                                  "role": "admin", "password": "evil12345",
                                  "confirm_password": "evil12345"})
    assert r.status_code == 200, "admin register not blocked"
    with app.app_context():
        assert models.user.find_by_identifier("9999999999") is None, "admin row was created!"
    # 2. triage garbage input -> 200 with evaluated tier, not 500
    r = c.post("/api/triage-evaluate", json={"systolic_bp": "abc", "maternal_weeks": "x", "pediatric_age": "y"})
    assert r.status_code == 200, "triage garbage crashed"
    # 3. per_page=0 -> 200, not 500 (logged in for hospitals page)
    c.post("/login", data={"identifier": "9876543210", "password": "asha123", "role_tab": "frontline"})
    assert c.get("/hospitals/?per_page=0").status_code == 200, "per_page=0 crashed"
    # 4. non-numeric units -> 400, not 500
    r = c.post("/api/medicine/1/update", json={"units": "abc"})
    assert r.status_code == 400, f"units garbage gave {r.status_code}"


if __name__ == "__main__":
    for fn in [test_structure, test_url_map, test_routes, test_login_gating, test_security_fixes]:
        fn()
        print(f"PASS {fn.__name__}")
    print("ALL SMOKE TESTS PASSED")
