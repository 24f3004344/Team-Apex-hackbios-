# lakshya MVC Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `lakshya/` Flask app ko strict MVC layout (models/, views/, controllers/, middleware/) me move karna, zero behavior change.

**Architecture:** Pure mechanical restructure on branch `mvc-restructure`. `routes/` → `controllers/` (git mv + rename), `db.py` → `models/` package (connection mgmt + schema/seeds + 7 domain query modules), `templates/`+`static/` → `views/`, `auth_middleware.py` → `middleware/`. `app.py` becomes `create_app()` factory with explicit template/static folders; new `run.py` entrypoint. Controllers me SQL nahi — sab model functions ke through.

**Tech Stack:** Python 3, Flask 3, Werkzeug 3, sqlite3 (stdlib). No new dependencies.

## Global Constraints

- `app1/` poora untouched.
- Endpoint names, URL rules, template context vars, seed data, DB schema — sab identical.
- Top-level flat imports style preserved (`from models import ...`, run from `lakshya/` dir).
- `swasthya.db` tracked file ko modify mat karo — verify ke baad restore karo agar WAL/timestamp change ho.
- Har task ke baad commit.

---

## File map

| Old | New | Change type |
| :--- | :--- | :--- |
| `lakshya/db.py` L1-28 | `models/database.py` | move + DATABASE path parent.parent + add `update_fields/delete_row/row_exists` helpers |
| `lakshya/db.py` L30-199 | `models/schema.py` | verbatim move of `init_db()`; `from .database import DATABASE` |
| — | `models/__init__.py` | NEW: re-exports |
| — | `models/user.py`, `teleconsult.py`, `referral.py`, `medicine.py`, `diagnostic.py`, `high_risk_case.py`, `hospital.py` | NEW: query functions (SQL yahan se uthaya gaya, controllers se nahi — controllers ke SQL yahan move honge) |
| `routes/auth.py` etc. (8) | `controllers/*_controller.py` (8) | git mv + import rewrite + db calls → model calls |
| `routes/__init__.py` | `controllers/__init__.py` | git mv + import lines rename |
| `templates/` (17 html) | `views/templates/` | git mv, zero content change |
| `static/` (css, js) | `views/static/` | git mv, zero content change |
| `auth_middleware.py` | `middleware/auth_middleware.py` + `middleware/__init__.py` | git mv, zero content change |
| `app.py` | `app.py` (rewritten) | factory + explicit folders |
| — | `run.py` | NEW entrypoint |
| — | `test_smoke.py` | NEW assert-based check (`python test_smoke.py`) |

---

### Task 1: models/ package

**Files:**
- Create: `lakshya/models/__init__.py`, `lakshya/models/database.py`, `lakshya/models/schema.py`, `lakshya/models/user.py`, `lakshya/models/teleconsult.py`, `lakshya/models/referral.py`, `lakshya/models/medicine.py`, `lakshya/models/diagnostic.py`, `lakshya/models/high_risk_case.py`, `lakshya/models/hospital.py`

**Interfaces:**
- Consumes: nothing (stdlib sqlite3 + flask.g only)
- Produces: `get_db()`, `close_db(exc)`, `init_db()`, `DATABASE: str`, `update_fields(table, row_id, fields)`, `delete_row(table, row_id)`, `row_exists(table, row_id)`, domain modules below. All SELECTs return `sqlite3.Row` (Jinja dot-access compatible); `hospital.py` returns plain `dict`s (existing controller behavior preserved).

- [ ] **Step 1: Write `models/database.py`**

```python
import os
import sqlite3
from flask import g

DATABASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "swasthya.db")

# Tables the generic row helpers may touch (internal callers only; blocks table-name injection).
_WRITABLE_TABLES = frozenset({
    "users", "referrals", "medicines", "teleconsults",
    "high_risk_cases", "diagnostics", "hospitals",
})


def get_db():
    """Get or create a database connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(exception=None):
    """Automatically close DB connection when the request ends."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _check_table(table):
    if table not in _WRITABLE_TABLES:
        raise ValueError(f"Refusing to write unknown table: {table!r}")


def update_fields(table, row_id, fields):
    """Partial update of one row: fields is {'col': value}. Returns True."""
    _check_table(table)
    if not fields:
        return False
    cols = ", ".join(f"{col} = ?" for col in fields)
    db = get_db()
    db.execute(f"UPDATE {table} SET {cols} WHERE id = ?", (*fields.values(), row_id))
    db.commit()
    return True


def delete_row(table, row_id):
    _check_table(table)
    db = get_db()
    db.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
    db.commit()


def row_exists(table, row_id):
    _check_table(table)
    return get_db().execute(f"SELECT id FROM {table} WHERE id = ?", (row_id,)).fetchone() is not None
```

- [ ] **Step 2: Write `models/schema.py`** — copy `db.py` lines 30-199 (`init_db()` + all 6 seeds) verbatim, replace header imports with:

```python
import sqlite3
from werkzeug.security import generate_password_hash
from .database import DATABASE
```

- [ ] **Step 3: Write `models/__init__.py`**

```python
from .database import DATABASE, close_db, delete_row, get_db, row_exists, update_fields
from .schema import init_db
from . import diagnostic, high_risk_case, hospital, medicine, referral, teleconsult, user

__all__ = [
    "DATABASE", "close_db", "delete_row", "get_db", "row_exists",
    "update_fields", "init_db",
    "diagnostic", "high_risk_case", "hospital", "medicine",
    "referral", "teleconsult", "user",
]
```

- [ ] **Step 4: Write domain modules** (SQL copied verbatim from current controllers/db.py)

`models/user.py`:
```python
from .database import get_db


def get_by_id(user_id):
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def find_by_identifier(identifier):
    return get_db().execute(
        "SELECT * FROM users WHERE identifier = ? OR abha_id = ?",
        (identifier, identifier),
    ).fetchone()


def create(full_name, identifier, role, facility_name, district, state, abha_id, language, password_hash):
    db = get_db()
    cur = db.execute("""
        INSERT INTO users (full_name, identifier, role, facility_name, district, state, abha_id, language, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (full_name, identifier, role, facility_name, district, state, abha_id, language, password_hash))
    db.commit()
    return cur.lastrowid
```

`models/teleconsult.py`:
```python
from .database import delete_row, get_db, row_exists, update_fields

TABLE = "teleconsults"
_QUEUE_ORDER = "ORDER BY CASE priority WHEN 'Emergency' THEN 1 WHEN 'Priority' THEN 2 ELSE 3 END, id DESC"


def list_queue():
    return get_db().execute(f"SELECT * FROM {TABLE} {_QUEUE_ORDER}").fetchall()


def create(patient_name, abha_id, age, gender, asha_worker, doctor_name, specialty, chief_complaint, vitals, priority):
    db = get_db()
    cur = db.execute("""
        INSERT INTO teleconsults (patient_name, abha_id, age, gender, asha_worker, doctor_name, specialty, chief_complaint, vitals, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'In-Queue')
    """, (patient_name, abha_id, age, gender, asha_worker, doctor_name, specialty, chief_complaint, vitals, priority))
    db.commit()
    return cur.lastrowid


def exists(tc_id):
    return row_exists(TABLE, tc_id)


def update(tc_id, fields):
    return update_fields(TABLE, tc_id, fields)


def delete(tc_id):
    delete_row(TABLE, tc_id)
```

`models/referral.py`: `list_all()` = `SELECT * FROM referrals ORDER BY id DESC`; `create(...)` INSERT with status 'Initiated' (7 params + notes); `update_status(ref_id, status)` → `update_fields("referrals", ref_id, {"status": status})`; `exists`, `delete` same pattern as teleconsult.

`models/medicine.py`: `list_all()` = `SELECT * FROM medicines ORDER BY stock_status ASC, name ASC`; `search(query, district)` = live-search SQL with LIMIT 15 (verbatim from inventory.py); `update(med_id, fields)`; `exists`; `delete`.

`models/diagnostic.py`: `list_all()` = `SELECT * FROM diagnostics ORDER BY tier ASC, test_name ASC`.

`models/high_risk_case.py`: `list_all()` with Critical→Due Today→Monitored CASE ordering (verbatim); `update(case_id, fields)`; `exists`; `delete`.

`models/hospital.py` (returns dicts; filter SQL verbatim from hospitals.py):
```python
from .database import get_db

_LIST_COLS = "SELECT * FROM hospitals WHERE 1=1"


def _filtered(base, district, hospital_type, search):
    params = []
    if district:
        base += " AND district = ?"
        params.append(district)
    if hospital_type:
        base += " AND hospital_type = ?"
        params.append(hospital_type)
    if search:
        base += " AND (hospital_name LIKE ? OR address LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    return base, params


def count(district="", hospital_type="", search=""):
    q, p = _filtered("SELECT COUNT(*) FROM hospitals WHERE 1=1", district, hospital_type, search)
    return get_db().execute(q, p).fetchone()[0]


def list_paginated(district="", hospital_type="", search="", per_page=20, page=1):
    q, p = _filtered(_LIST_COLS, district, hospital_type, search)
    q += " ORDER BY district, hospital_name LIMIT ? OFFSET ?"
    p.extend([per_page, (page - 1) * per_page])
    return [dict(h) for h in get_db().execute(q, p).fetchall()]


def list_for_map(district="", hospital_type="", search="", limit=150):
    q = "SELECT id, sno, district, hospital_type, hospital_name, address, phone1, phone2, email, latitude, longitude FROM hospitals WHERE 1=1"
    q, p = _filtered(q, district, hospital_type, search)
    q += " AND latitude IS NOT NULL AND longitude IS NOT NULL ORDER BY district, hospital_name LIMIT 150"
    return [dict(h) for h in get_db().execute(q, p[:]).fetchall()]


def get(hospital_id):
    row = get_db().execute("SELECT * FROM hospitals WHERE id = ?", (hospital_id,)).fetchone()
    return dict(row) if row else None


def nearby(district, exclude_id, limit=6):
    rows = get_db().execute(
        "SELECT id, hospital_name, hospital_type, district, address, phone1, latitude, longitude FROM hospitals WHERE district = ? AND id != ? ORDER BY hospital_name LIMIT 6",
        (district, exclude_id),
    ).fetchall()
    return [dict(h) for h in rows]


def districts():
    return [d["district"] for d in get_db().execute("SELECT DISTINCT district FROM hospitals ORDER BY district").fetchall()]


def types():
    return [t["hospital_type"] for t in get_db().execute("SELECT DISTINCT hospital_type FROM hospitals ORDER BY hospital_type").fetchall()]


def stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]
    by_district = [dict(d) for d in db.execute("SELECT district, COUNT(*) as count FROM hospitals GROUP BY district ORDER BY count DESC").fetchall()]
    by_type = [dict(t) for t in db.execute("SELECT hospital_type, COUNT(*) as count FROM hospitals GROUP BY hospital_type ORDER BY count DESC").fetchall()]
    return {"total": total, "by_district": by_district, "by_type": by_type}
```

- [ ] **Step 5: Verify models import standalone**

Run: `python3 -c "import sys; sys.path.insert(0,'lakshya'); import models; print(sorted(models.hospital.districts())[:3])"`
Expected: districts print hota hai, no ImportError. (DB read-only; WAL pragma lag sakta hai — Task 6 me restore.)

- [ ] **Step 6: Commit**

```bash
git add lakshya/models
git commit -m "refactor: add models/ package (db split + domain query modules)"
```

---

### Task 2: controllers/ (git mv + model calls)

**Files:** `git mv lakshya/routes lakshya/controllers`, then rename each to `*_controller.py`, rewrite per-file edits below. `controllers/__init__.py`: sirf 8 import lines rename (`from .auth import auth_bp` → `from .auth_controller import auth_bp`, etc.); alias loop verbatim.

- [ ] **Step 1: git mv + renames**

```bash
git mv lakshya/routes lakshya/controllers
git mv lakshya/controllers/auth.py lakshya/controllers/auth_controller.py
git mv lakshya/controllers/main.py lakshya/controllers/main_controller.py
git mv lakshya/controllers/teleconsult.py lakshya/controllers/teleconsult_controller.py
git mv lakshya/controllers/referrals.py lakshya/controllers/referrals_controller.py
git mv lakshya/controllers/inventory.py lakshya/controllers/inventory_controller.py
git mv lakshya/controllers/high_risk.py lakshya/controllers/high_risk_controller.py
git mv lakshya/controllers/triage.py lakshya/controllers/triage_controller.py
git mv lakshya/controllers/hospitals.py lakshya/controllers/hospitals_controller.py
```

- [ ] **Step 2: Per-controller exact edits**

`auth_controller.py`: line 5 `from db import get_db` → `from models import user as user_model`. login(): delete `db = get_db()` line, `user = db.execute(...).fetchone()` → `user = user_model.find_by_identifier(identifier)`. register(): `db = get_db()` + `db.execute(...INSERT...)` + `db.commit()` + `new_user_id = db.execute("SELECT last_insert_rowid()")...` → `new_user_id = user_model.create(full_name, identifier, role, facility_name or "Community Health Sub-Centre", district, state, abha_id, language, generate_password_hash(password))`. Keep `import sqlite3` (IntegrityError catch).

`main_controller.py`: lines 2-3 → `from models import user as user_model, referral, medicine, teleconsult, high_risk_case`. dashboard(): 5 query lines → `user = user_model.get_by_id(session["user_id"])`, `referrals = referral.list_all()`, `medicines = medicine.list_all()`, `teleconsults = teleconsult.list_queue()`, `high_risk_cases = high_risk_case.list_all()`. (Note: dashboard ordering teleconsults me `id ASC` hai vs model `id DESC` — model me teleconsult.list_queue DESC use karta hai jo teleconsult page jaisa hai; dashboard.html order-sensitive nahi (cards render), lekin exact preserve ke liye dashboard apna SQL rakhe? Ponytail: ek hi list_queue canonical — dashboard.html me koi index-based logic nahi, dono orders render hote hain. DESC canonical rakho.)

Hmm — wait. Self-review: spec me "template context vars identical" hai, ordering vars ka part nahi. Dashboard template loops only. DESC acceptable, aur consistent. OK.

`teleconsult_controller.py`: line 3 → `from models import teleconsult as tc_model`. POST block ke `db = get_db()` + `db.execute(INSERT)` + `db.commit()` → `tc_model.create(patient_name, abha_id or f"91-...", age, gender, session.get("user_name", "Frontline Worker"), "Dr. Rajesh Sharma (MO Bilaspur)", specialty, chief_complaint, vitals, priority)`. GET: `queue = tc_model.list_queue()`. update API: `existing` check → `if not tc_model.exists(tc_id): 404`; updates dict build same; `tc_model.update(tc_id, {status/prescription})` — dhyan: purana code `if updates:` guard rakhta tha (empty dict pe no-op success). Model ka update_fields empty dict pe False return karta hai, controller phir bhi success return kare — same behavior. delete API: exists check + `tc_model.delete(tc_id)`.

`referrals_controller.py`: `from models import referral as ref_model`. POST → `ref_model.create(...)`. update API → validate status, exists, `ref_model.update_status(ref_id, new_status)`. delete → exists + `ref_model.delete(ref_id)`.

`inventory_controller.py`: `from models import medicine as med_model`. page: `medicines = med_model.list_all()`, `diagnostics` ke liye `from models import diagnostic as diag_model; diagnostics = diag_model.list_all()`. update API: auto-status logic same (controller me rehta hai), phir `fields` dict banao (units? status? last_updated) → `med_model.update(med_id, fields)`; exists check via `med_model.exists(med_id)`. delete → exists + delete. search API → `results = med_model.search(query, district)`.

`high_risk_controller.py`: `from models import high_risk_case as hr_model`. page → `hr_model.list_all()`. update API: validate, exists, fields dict (status/notes/next_action_date) → `hr_model.update(case_id, fields)`. delete similar.

`triage_controller.py`: koi import change nahi (db import tha hi nahi). Sirf rename.

`hospitals_controller.py`: line 5 → `from models import hospital as hospital_model`. `get_nearby_hospitals()` helper DELETE karo (model me hai); `get_nearby_hospitals_global` body → `return hospital_model.nearby(district, exclude_id, limit)`. list: `total = hospital_model.count(...)`, `hospitals = hospital_model.list_paginated(..., per_page, page)`, `map_hospitals = hospital_model.list_for_map(...)`, `districts = hospital_model.districts()`, `types = hospital_model.types()`; `districts=[d...]` comprehension lines delete (model already list deta hai). detail: `hospital = hospital_model.get(hospital_id)`; `if not hospital: 404`; `nearby_list = hospital_model.nearby(hospital["district"], hospital_id)`. api fns: `hospital_model.list_paginated(...)`, `hospital_model.districts()`, `hospital_model.stats()`.

- [ ] **Step 3: Verify controllers import**

Run: `python3 -c "import sys; sys.path.insert(0,'lakshya'); from controllers import register_routes; print('controllers OK')"`
Expected: PASS (Flask import chahiye — installed hai per requirements).

- [ ] **Step 4: Commit**

```bash
git add -A lakshya/controllers
git commit -m "refactor: routes/ -> controllers/, SQL moved to models/"
```

---

### Task 3: views/ + middleware/ moves (zero content change)

- [ ] **Step 1: git mv**

```bash
mkdir -p lakshya/views lakshya/middleware
git mv lakshya/templates lakshya/views/templates
git mv lakshya/static lakshya/views/static
git mv lakshya/auth_middleware.py lakshya/middleware/auth_middleware.py
```

- [ ] **Step 2: `middleware/__init__.py`**

```python
from .auth_middleware import login_required

__all__ = ["login_required"]
```

- [ ] **Step 3: controllers me middleware import fix** — `main_controller.py` line `from auth_middleware import login_required` → `from middleware.auth_middleware import login_required`. (Sirf main_controller me hai ye import.)

- [ ] **Step 4: Verify**

Run: `ls lakshya/views/templates | wc -l` → 14 files (12 root + hospitals/ dir). `ls lakshya/views/static/js` → 3 js.

- [ ] **Step 5: Commit**

```bash
git add -A lakshya/views lakshya/middleware lakshya/controllers/main_controller.py
git commit -m "refactor: templates+static -> views/, auth_middleware -> middleware/"
```

---

### Task 4: app factory + run.py + README

- [ ] **Step 1: Rewrite `lakshya/app.py`** (purana content replace; `db`/`routes` imports khatam, `db.py` abhi bhi disk pe hai — Task 5 me delete)

```python
import os
from flask import Flask, session
from models import close_db, get_db, init_db
from models import user as user_model
from controllers import register_routes


def create_app():
    """Application factory: models -> controllers wiring with explicit view folders."""
    app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
    app.secret_key = os.environ.get("SECRET_KEY", "swasthya-setu-secure-secret-key-2026")

    # Automatically close database connection when the request ends
    app.teardown_appcontext(close_db)

    # Initialize database schema and demo seed data upon launch
    init_db()

    @app.context_processor
    def inject_global_data():
        """Inject current_user into all templates (uses per-request DB)."""
        current_user = None
        if "user_id" in session:
            current_user = user_model.get_by_id(session["user_id"])
        return dict(current_user=current_user)

    register_routes(app)
    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting AarogyaSahay Health Grid on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
```

- [ ] **Step 2: Write `lakshya/run.py`**

```python
import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting AarogyaSahay Health Grid on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
```

- [ ] **Step 3: Delete `lakshya/db.py`** (`git rm`), README run block update (`python3 app.py` → `python run.py`, path note same rehta hai).

- [ ] **Step 4: Verify boot (no requests yet)**

Run: `python3 -c "import sys; sys.path.insert(0,'lakshya'); from app import app; print(sorted(r.endpoint for r in app.url_map.iter_rules() if not r.endpoint.startswith('static')))"`
Expected: index, dashboard, login, register, logout, teleconsult, referrals_page, inventory_page, high_risk_page, triage_page, records_page, analytics_page + blueprint-qualified names + short aliases (auth.login + login dono).

- [ ] **Step 5: Commit**

```bash
git add -A lakshya/app.py lakshya/run.py lakshya/db.py lakshya/README.md
git commit -m "refactor: app factory + run.py entrypoint, drop db.py"
```

---

### Task 5: smoke test + full verification

- [ ] **Step 1: Write `lakshya/test_smoke.py`** (read-only: sirf GETs + 2 read APIs; koi POST insert nahi)

```python
"""MVC smoke test: structure + endpoints + pages. Run: python test_smoke.py (from lakshya/)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_structure():
    for p in ["models/__init__.py", "models/database.py", "models/schema.py",
              "models/user.py", "models/hospital.py",
              "controllers/__init__.py", "controllers/auth_controller.py",
              "controllers/hospitals_controller.py",
              "views/templates/base.html", "views/templates/hospitals/list.html",
              "views/static/css/style.css", "views/static/js/main.js",
              "middleware/auth_middleware.py", "run.py"]:
        assert os.path.exists(p), f"missing {p}"
    assert not os.path.exists("db.py"), "old db.py still present"
    assert not os.path.exists("routes"), "old routes/ still present"


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
                 "/analytics", "/hospitals", "/static/css/style.css",
                 "/hospitals/api/stats"]:
        assert c.get(path).status_code == 200, f"GET {path} failed"
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
```

- [ ] **Step 2: Run checks**

```bash
python3 -m compileall -q lakshya && echo COMPILE_OK
python3 lakshya/test_smoke.py
```

Expected: COMPILE_OK + 3x PASS + ALL SMOKE TESTS PASSED.

- [ ] **Step 3: DB restore (agar tracked db dirty hua)**

```bash
git status --porcelain -- lakshya/*.db lakshya/*.db-wal lakshya/*.db-shm lakshya/*.db-journal
```

Agar `swasthya.db` modified dikhe → `git checkout -- lakshya/swasthya.db`; agar `-wal/-shm/-journal` untracked files bane → delete karo.

- [ ] **Step 4: Live boot check (optional, 10 sec)**

```bash
timeout 12 python3 lakshya/run.py & sleep 6; curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5050/ http://127.0.0.1:5050/hospitals; wait
```

Expected: `200` `200`.

- [ ] **Step 5: Commit + final detect**

```bash
git add lakshya/test_smoke.py
git commit -m "test: add MVC smoke test (structure + endpoints + pages)"
git log --oneline -6
git status --short
```

---

## Self-review (spec coverage)

- Spec §3 target structure → Tasks 1-4 file-by-file. OK
- Spec §5 import rules → Task 2/3/4 edits. OK (middleware import sirf main_controller me — grep se confirm kiya, 11 matches me wahi ek tha)
- Spec §6 connectivity (url_for aliases, fetch endpoints, JS funcs, template vars, import chain) → Task 5 test_url_map/test_routes cover; JS/templates untouched (git mv only). OK
- Spec §7 non-goals → koi services/, koi app1 change, koi schema change nahi. OK
- Spec §8 verification → Task 5 steps 2-4. OK
- No placeholders: har file ka exact content/mapping diya hai. OK
