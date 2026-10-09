from .database import get_db


def list_all():
    """All diagnostic tests ordered by facility tier."""
    return get_db().execute("SELECT * FROM diagnostics ORDER BY tier ASC, test_name ASC").fetchall()
