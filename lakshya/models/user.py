from .database import get_db


def get_by_id(user_id):
    """Fetch one user by id."""
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def find_by_identifier(identifier):
    """Find user by phone/email identifier or ABHA ID."""
    return get_db().execute(
        "SELECT * FROM users WHERE identifier = ? OR abha_id = ?",
        (identifier, identifier),
    ).fetchone()


def create(full_name, identifier, role, facility_name, district, state, abha_id, language, password_hash):
    """Insert a new user. Returns new user id. May raise sqlite3.IntegrityError."""
    db = get_db()
    cur = db.execute("""
        INSERT INTO users (full_name, identifier, role, facility_name, district, state, abha_id, language, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (full_name, identifier, role, facility_name, district, state, abha_id, language, password_hash))
    db.commit()
    return cur.lastrowid
