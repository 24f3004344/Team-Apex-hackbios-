from .database import delete_row, get_db, row_exists, update_fields

TABLE = "medicines"


def list_all():
    """All medicines ordered by stock status."""
    return get_db().execute("SELECT * FROM medicines ORDER BY stock_status ASC, name ASC").fetchall()


def search(query, district):
    """Live search by name/category (+district filter), max 15 rows."""
    sql = "SELECT * FROM medicines WHERE 1=1"
    params = []
    if query:
        sql += " AND (name LIKE ? OR category LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if district:
        sql += " AND district LIKE ?"
        params.append(f"%{district}%")
    sql += " LIMIT 15"
    return [dict(row) for row in get_db().execute(sql, params).fetchall()]


def exists(med_id):
    return row_exists(TABLE, med_id)


def update(med_id, fields):
    """Partial update: {'units': ..., 'stock_status': ..., 'last_updated': ...}."""
    return update_fields(TABLE, med_id, fields)


def delete(med_id):
    delete_row(TABLE, med_id)
