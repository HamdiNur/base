from functools import wraps
from flask import redirect, url_for
from flask_login import current_user
from auth.permissions import has_permission

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not has_permission(current_user, permission):
                # 👇 viewer / staff friendly redirect
                return redirect(url_for("projects.index"))
            return f(*args, **kwargs)
        return wrapper
    return decorator
