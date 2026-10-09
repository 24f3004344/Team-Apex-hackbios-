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
        g.db.execute("PRAGMA journal_mode=WAL")       # Better concurrent read perf
        g.db.execute("PRAGMA foreign_keys=ON")         # Enforce referential integrity
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
    """Partial update of one row: fields is {'col': value}. Returns True, False if empty."""
    _check_table(table)
    if not fields:
        return False
    cols = ", ".join(f"{col} = ?" for col in fields)
    db = get_db()
    db.execute(f"UPDATE {table} SET {cols} WHERE id = ?", (*fields.values(), row_id))
    db.commit()
    return True


def delete_row(table, row_id):
    """Delete one row by id."""
    _check_table(table)
    db = get_db()
    db.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
    db.commit()


def row_exists(table, row_id):
    """Check one row exists by id."""
    _check_table(table)
    return get_db().execute(f"SELECT id FROM {table} WHERE id = ?", (row_id,)).fetchone() is not None
