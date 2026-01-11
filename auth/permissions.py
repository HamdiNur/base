# auth/permissions.py

ADMIN = "ADMIN"
MANAGER = "MANAGER"
STAFF = "STAFF"
VIEWER = "VIEWER"


ROLE_PERMISSIONS = {
    ADMIN: {
    "view_dashboard",   # ← THIS MUST EXIST
        "manage_users",
        "manage_roles",   # 🔥 ADD THIS
        "create_projects",
        "assign_users",
        "view_all",
    },
    MANAGER: {
        "view_dashboard",
        "create_projects",
        "assign_staff",
        "view_projects",
        "view_users"
    },
    STAFF: {
        "view_projects",
        "update_projects",
    },
    VIEWER: {
        "view_projects",
    },
}

def has_permission(user, permission: str) -> bool:
    if not user.is_authenticated or not user.role:
        return False

    role_code = user.role.code.upper()
    perms = ROLE_PERMISSIONS.get(role_code, set())

    # 🔥 SUPER PERMISSION
    if "view_all" in perms:
        return True

    return permission in perms
