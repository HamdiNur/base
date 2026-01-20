# auth/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user
from auth.permissions import has_permission


def is_admin(user):
    # checks if the user has a role and if the role name is 'Admin'
    return user.role and user.role.name.lower() == "admin"

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # admins bypass permission checks
            if not (is_admin(current_user) or has_permission(current_user, permission)):
                abort(403)   # ⛔ HARD STOP
            return f(*args, **kwargs)
        return wrapper
    return decorator
