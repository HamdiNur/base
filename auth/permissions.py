# auth/permissions.py

ADMIN = "admin"
MANAGER = "Manager"
STAFF = "Staff"
VIEWER = "Viewer"

ROLE_PERMISSIONS = {
    ADMIN: {
        "manage_users",
        "create_projects",
        "assign_users",
        "view_all",
    },
    MANAGER: {
        "create_projects",
        "assign_staff",
        "view_projects",
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
    if not user.is_authenticated:
        return False

    role_name = user.role.name
    return permission in ROLE_PERMISSIONS.get(role_name, set())
