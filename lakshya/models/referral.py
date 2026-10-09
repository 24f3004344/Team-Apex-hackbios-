from .database import delete_row, get_db, row_exists, update_fields

TABLE = "referrals"


def list_all():
    """All referrals, newest first."""
    return get_db().execute("SELECT * FROM referrals ORDER BY id DESC").fetchall()


def create(patient_name, abha_id, source_facility, target_facility, specialty, urgency, notes):
    """Initiate a referral. Returns new referral id."""
    db = get_db()
    cur = db.execute("""
        INSERT INTO referrals (patient_name, abha_id, source_facility, target_facility, specialty, urgency, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, 'Initiated', ?)
    """, (patient_name, abha_id, source_facility, target_facility, specialty, urgency, notes))
    db.commit()
    return cur.lastrowid


def exists(ref_id):
    return row_exists(TABLE, ref_id)


def update_status(ref_id, status):
    return update_fields(TABLE, ref_id, {"status": status})


def delete(ref_id):
    delete_row(TABLE, ref_id)
