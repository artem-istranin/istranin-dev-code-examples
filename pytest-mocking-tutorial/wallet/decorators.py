"""Report successful operations without changing their return values."""

from functools import wraps

from wallet.events import report_event


def report(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        report_event(f"{func.__name__} completed")
        return result

    return wrapped
