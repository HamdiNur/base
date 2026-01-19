# auth/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user
from auth.permissions import has_permission

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not has_permission(current_user, permission):
                abort(403)   # ⛔ HARD STOP
            return f(*args, **kwargs)
        return wrapper
    return decorator
