from .database import get_db


def _filtered(base, district, hospital_type, search):
    """Append shared district/type/search filters. Returns (query, params)."""
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
    """Total hospitals matching filters."""
    q, p = _filtered("SELECT COUNT(*) FROM hospitals WHERE 1=1", district, hospital_type, search)
    return get_db().execute(q, p).fetchone()[0]


def list_paginated(district="", hospital_type="", search="", per_page=20, page=1):
    """Filtered hospital rows as dicts, paginated."""
    q, p = _filtered("SELECT * FROM hospitals WHERE 1=1", district, hospital_type, search)
    q += " ORDER BY district, hospital_name LIMIT ? OFFSET ?"
    p.extend([per_page, (page - 1) * per_page])
    return [dict(h) for h in get_db().execute(q, p).fetchall()]


def list_for_map(district="", hospital_type="", search="", limit=150):
    """Geocoded hospitals for map rendering."""
    q = ("SELECT id, sno, district, hospital_type, hospital_name, address, phone1, phone2, email,"
         " latitude, longitude FROM hospitals WHERE 1=1")
    q, p = _filtered(q, district, hospital_type, search)
    q += " AND latitude IS NOT NULL AND longitude IS NOT NULL ORDER BY district, hospital_name LIMIT 150"
    return [dict(h) for h in get_db().execute(q, p).fetchall()]


def get(hospital_id):
    """One hospital as dict, or None."""
    row = get_db().execute("SELECT * FROM hospitals WHERE id = ?", (hospital_id,)).fetchone()
    return dict(row) if row else None


def nearby(district, exclude_id, limit=6):
    """Nearby hospitals in the same district."""
    rows = get_db().execute(
        "SELECT id, hospital_name, hospital_type, district, address, phone1, latitude, longitude"
        " FROM hospitals WHERE district = ? AND id != ? ORDER BY hospital_name LIMIT 6",
        (district, exclude_id),
    ).fetchall()
    return [dict(h) for h in rows]


def districts():
    """Sorted list of districts."""
    return [d["district"] for d in get_db().execute("SELECT DISTINCT district FROM hospitals ORDER BY district").fetchall()]


def types():
    """Sorted list of hospital types."""
    return [t["hospital_type"] for t in get_db().execute("SELECT DISTINCT hospital_type FROM hospitals ORDER BY hospital_type").fetchall()]


def stats():
    """Aggregate hospital statistics."""
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]
    by_district = [dict(d) for d in db.execute(
        "SELECT district, COUNT(*) as count FROM hospitals GROUP BY district ORDER BY count DESC").fetchall()]
    by_type = [dict(t) for t in db.execute(
        "SELECT hospital_type, COUNT(*) as count FROM hospitals GROUP BY hospital_type ORDER BY count DESC").fetchall()]
    return {"total": total, "by_district": by_district, "by_type": by_type}
