from extensions import db
from roles.models import Role
from permissions.models import Permission  # THIS FILE ONLY, NO ROUTES

def has_permission(user, permission_code: str) -> bool:
    if not user or not user.role:
        return False

    return (
        db.session.query(Permission)
        .join(Permission.roles)
        .filter(
            Role.id == user.role_id,
            Permission.code == permission_code,
            Permission.is_active.is_(True)
        )
        .count()
        > 0
    )
