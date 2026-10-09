from .database import delete_row, get_db, row_exists, update_fields

TABLE = "teleconsults"
_QUEUE_ORDER = "ORDER BY CASE priority WHEN 'Emergency' THEN 1 WHEN 'Priority' THEN 2 ELSE 3 END, id DESC"


def list_queue():
    """Tele-OPD queue, Emergency first."""
    return get_db().execute(f"SELECT * FROM {TABLE} {_QUEUE_ORDER}").fetchall()


def create(patient_name, abha_id, age, gender, asha_worker, doctor_name, specialty, chief_complaint, vitals, priority):
    """Enqueue a patient. Returns new teleconsult id."""
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
    """Partial update: {'status': ..., 'prescription': ...}."""
    return update_fields(TABLE, tc_id, fields)


def delete(tc_id):
    delete_row(TABLE, tc_id)
