from .database import delete_row, get_db, row_exists, update_fields

TABLE = "high_risk_cases"
_STATUS_ORDER = "ORDER BY CASE status WHEN 'Critical' THEN 1 WHEN 'Due Today' THEN 2 ELSE 3 END, id ASC"


def list_all():
    """All high-risk cases, Critical first."""
    return get_db().execute(f"SELECT * FROM {TABLE} {_STATUS_ORDER}").fetchall()


def exists(case_id):
    return row_exists(TABLE, case_id)


def update(case_id, fields):
    """Partial update: {'status': ..., 'notes': ..., 'next_action_date': ...}."""
    return update_fields(TABLE, case_id, fields)


def delete(case_id):
    delete_row(TABLE, case_id)
