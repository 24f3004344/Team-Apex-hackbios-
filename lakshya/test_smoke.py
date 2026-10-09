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
    for path in ["/", "/login", "/register", "/teleconsult", "/triage",
                 "/records", "/referrals", "/inventory", "/high-risk",
                 "/analytics", "/hospitals/", "/hospitals/1", "/static/css/style.css",
                 "/hospitals/api/stats"]:
        assert c.get(path).status_code == 200, f"GET {path} failed"
    assert c.get("/hospitals").status_code == 308  # strict-slash redirect to /hospitals/
    assert c.get("/dashboard").status_code == 302  # login_required redirect
    r = c.post("/api/triage-evaluate", json={"breathing_difficulty": True})
    assert r.status_code == 200 and "Red" in r.get_json()["tier"]
    r = c.get("/api/medicine-search?q=ORS")
    assert r.status_code == 200 and r.get_json()["count"] >= 1


if __name__ == "__main__":
    for fn in [test_structure, test_url_map, test_routes]:
        fn()
        print(f"PASS {fn.__name__}")
    print("ALL SMOKE TESTS PASSED")
