import time

#: Max failed logins per identifier inside WINDOW_SECONDS before lockout.
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 15 * 60

# identifier -> [fail_count, window_start_epoch]. In-memory: resets on restart.
_attempts = {}


def _record(identifier):
    now = time.time()
    count, start = _attempts.get(identifier, (0, now))
    if now - start > WINDOW_SECONDS:
        count, start = 0, now
    return count, start, now


def is_blocked(identifier):
    """True when identifier exhausted its attempts in the current window."""
    count, start, now = _record(identifier)
    if now - start > WINDOW_SECONDS:
        _attempts.pop(identifier, None)
        return False
    return count >= MAX_ATTEMPTS


def register_failure(identifier):
    """Count one failed login. Returns remaining attempts before lockout."""
    count, start, now = _record(identifier)
    if now - start > WINDOW_SECONDS:
        count, start = 0, now
    count += 1
    _attempts[identifier] = (count, start)
    return max(0, MAX_ATTEMPTS - count)


def clear(identifier):
    """Reset counter (call on successful login)."""
    _attempts.pop(identifier, None)
