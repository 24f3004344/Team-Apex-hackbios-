# Design: lakshya/ ka strict MVC restructure

**Date:** 2026-10-10
**Branch:** `mvc-restructure`
**Status:** Approved by user

## 1. Goal

Repo me 2 Flask apps hain: `lakshya/` (working app — "AarogyaSahay Rural Health Grid") aur
`app1/` (SQLAlchemy models library, unused by lakshya). Sirf `lakshya/` ko textbook
Model-View-Controller structure me convert karna hai. `app1/`, templates, static files,
database, endpoint names, URLs, aur frontend behavior bilkul unchanged rehne chahiye.

## 2. Scope

| In scope | Out of scope (untouched) |
| :--- | :--- |
| `lakshya/` python code restructuring | `app1/` (poora folder) |
| Folder layout: models/, views/, controllers/, middleware/ | `lakshya/*.db`, seed data |
| Import path rewrites | `import_hospitals.py`, `geocode_hospitals.py` (logic same, sirf DATABASE import shayad) |
| Spec + plan + verification | Templates (17 html), static (css/js), README content (run command ka path update ho sakta hai) |

## 3. Target structure

```
lakshya/
├── run.py                      # NEW entrypoint: `python run.py` (port 5050, host 127.0.0.1)
├── app.py                      # create_app() factory + context processor + register_routes
├── models/                     # ===== MODEL =====
│   ├── __init__.py             # re-exports: get_db, close_db, init_db + sab domain query fns
│   ├── database.py             # get_db(), close_db(), DATABASE (WAL + FK pragmas)
│   ├── schema.py               # init_db(): CREATE TABLE + seed data (db.py ka content)
│   ├── user.py                 # users: get_by_id, find_by_identifier, create
│   ├── teleconsult.py          # teleconsults: list_queue, create, update, delete
│   ├── referral.py             # referrals: list_all, create, update_status, delete
│   ├── medicine.py             # medicines: list_all, search, update, delete
│   ├── diagnostic.py           # diagnostics: list_all
│   ├── high_risk_case.py       # high_risk_cases: list_all, update, delete
│   └── hospital.py             # hospitals: list (paginated/filtered), get, nearby, stats, districts
├── controllers/                # ===== CONTROLLER =====
│   ├── __init__.py             # register_routes(app) + short-endpoint alias generation (existing logic)
│   ├── auth_controller.py      # login, register, logout
│   ├── main_controller.py      # index, dashboard, records_page, analytics_page
│   ├── teleconsult_controller.py
│   ├── referrals_controller.py
│   ├── inventory_controller.py
│   ├── high_risk_controller.py
│   ├── triage_controller.py    # triage_page + api_triage_evaluate (clinical rule inline, no services/ layer)
│   └── hospitals_controller.py # blueprint url_prefix=/hospitals + app_template_global helper
├── views/                      # ===== VIEW =====
│   ├── templates/              # 17 html files (git mv)
│   └── static/                 # css/, js/ (git mv)
├── middleware/
│   └── auth_middleware.py      # login_required decorator (git mv)
├── swasthya.db                 # unchanged
├── import_hospitals.py          # unchanged (root-level DATABASE path already correct)
├── geocode_hospitals.py         # unchanged
├── requirements.txt             # unchanged
└── README.md                    # run command update: cd lakshya && python run.py
```

## 4. File migration map (git mv)

| Old | New |
| :--- | :--- |
| `lakshya/app.py` | `lakshya/app.py` (rewritten as factory) |
| `lakshya/db.py` | split: `models/database.py` + `models/schema.py` + `models/__init__.py` |
| `lakshya/auth_middleware.py` | `middleware/auth_middleware.py` |
| `lakshya/routes/*.py` (8 files) | `controllers/*_controller.py` (8 files) |
| `lakshya/templates/` | `views/templates/` |
| `lakshya/static/` | `views/static/` |
| — | NEW `lakshya/run.py` |

## 5. Import rewrite rules (contract)

- `from db import get_db` → `from models import get_db` (ya specific model module fn)
- `from auth_middleware import login_required` → `from middleware.auth_middleware import login_required`
- `from routes import register_routes` → `from controllers import register_routes`
- `models/database.py`: `DATABASE = Path(__file__).resolve().parent.parent / "swasthya.db"` (models/ ek level neeche hai)
- `app.py`: `Flask(__name__, template_folder="views/templates", static_folder="views/static")`
- Controllers: no SQL — saare DB calls model functions ke through

## 6. Component connectivity contract (audit results — ye links post-restructure bhi intact hone chahiye)

### 6.1 url_for endpoints used in templates (sab exist karte hain, alias mechanism zaroori)

Short names (aliases via controllers/__init__.py): `index`, `dashboard`, `login`, `logout`,
`register`, `teleconsult`, `triage_page`, `records_page`, `referrals_page`, `inventory_page`,
`high_risk_page`, `analytics_page`, `static`.
Blueprint-qualified: `hospitals.list_hospitals`, `hospitals.hospital_detail`.

base.html:96 me `request.endpoint in ('hospitals.list_hospitals', 'hospitals')` check —
alias `hospitals` bhi generate hota hai, dono preserve karne hain.

### 6.2 JS fetch endpoint calls

| JS call (file:line) | Endpoint | Controller |
| :--- | :--- | :--- |
| `main.js:130` `fetch('/api/triage-evaluate')` | triage_bp.api_triage_evaluate | triage_controller |
| `main.js:227` `fetch('/api/medicine-search?q=..&district=..')` | inventory_bp.api_medicine_search | inventory_controller |

### 6.3 API endpoints defined but frontend use nahi karta (still preserve karo)

`/api/medicine/<id>/update`, `/api/medicine/<id>/delete`, `/api/high-risk/<id>/update`,
`/api/high-risk/<id>/delete`, `/api/teleconsult/<id>/update`, `/api/teleconsult/<id>/delete`,
`/api/referral/<id>/update`, `/api/referral/<id>/delete`, `/hospitals/api`, `/hospitals/api/districts`,
`/hospitals/api/stats`.

### 6.4 JS function dependency map (kaunsi function kahan defined — restructure me JS files move hoti hain, functions same rehne chahiye)

| Source file | Functions |
| :--- | :--- |
| views/static/js/main.js | fillDemo, resetTriageForm, searchMedicines, selectRoleTab, showToast, simulateTeleConsultModal, switchAuthMethod, syncFieldData, togglePasswordVisibility, toggleTheme, triage evaluate fetch, medicine search fetch |
| views/static/js/translations.js | switchLanguage + translation table |
| views/static/js/hospital-map.js | filterMapByType, focusHospital, locateUser |
| Inline `<script>` in templates | chooseRole, connectQueuePatient, endConsultation, filterCohort, filterReferrals, generateAudioRx, playMedicationAudio, raiseRestockIndent, switchInventoryTab, switchTriageCategory, toggleCam, toggleMic, triggerAmbulanceSOS, updateBandwidthMode |

### 6.5 Template context variables (controller → template contract)

| Template | Variables |
| :--- | :--- |
| dashboard.html | user, referrals, medicines, teleconsults, high_risk_cases |
| inventory.html | medicines, diagnostics |
| high_risk.html | cases |
| referrals.html | referrals |
| teleconsult.html | queue |
| records.html | active_abha |
| hospitals/list.html | hospitals, map_hospitals, districts, types, current_district, current_type, search, page, per_page, total, total_pages |
| hospitals/detail.html | hospital, nearby_hospitals |
| login.html | identifier, role_tab (POST re-render) |
| register.html | form_data (POST re-render) |
| base.html (all) | current_user (app context processor) |
| hospitals/detail.html | `get_nearby_hospitals_global` app_template_global |

### 6.6 Import chain (app boot order)

`run.py` → `app.py` (create_app) → `models` (init_db at startup) → `controllers.register_routes(app)` →
`middleware.auth_middleware` (imported by controllers). Koi circular import nahi: models ko
controllers ki zaroorat nahi, controllers models ko import karte hain.

## 7. Deliberate non-goals (ponytail: YAGNI)

- Koi `services/` layer nahi — MVC me business logic (triage rule) controller me rehta hai.
- app1/ ko merge/wire nahi karna (user ka scope: sirf lakshya).
- DB migration nahi — schema identical.
- Naya tests framework nahi — ek smoke test script (route boot + curl checks) kaafi.

## 8. Verification plan

1. `python -c "import ast; ..."` / compile check: `python -m compileall lakshya`
2. Boot: `cd lakshya && python run.py` → 200 on `/`, `/login`, `/register`, `/dashboard` (302→login),
   `/teleconsult`, `/triage`, `/records`, `/referrals`, `/inventory`, `/high-risk`, `/analytics`,
   `/hospitals`, `/hospitals/api/stats`
3. API: POST `/api/triage-evaluate` (red/yellow/green), `/api/medicine-search?q=ORS`
4. Alias check: `app.url_map` me short endpoints (`login`, `dashboard`, ...) exist karte hain
5. Static: `/static/css/style.css` 200 (views/static wired correctly)

## 9. Risks

| Risk | Mitigation |
| :--- | :--- |
| Import breakage (top-level `from models import ...` cwd-dependent) | run.py root se; compileall + boot test |
| template/static folder path galat | app.py factory explicit folders; static URL 200 check |
| Alias generation missing → base.html nav active state + middleware redirect toot jaayega | alias loop verbatim preserve; url_map assertion test |
