from extensions import db
from permissions.models import Permission

permissions = [
    # Dashboard
    ("view_dashboard", "View Dashboard"),

    # Projects
    ("project_view", "View Projects"),
    ("project_create", "Create Project"),
    ("project_update", "Update Project"),
    ("project_delete", "Delete Project"),
    ("assign_project_manager", "Assign Project Manager"),
    ("assign_project_members", "Assign Project Members"),
    ("manage_own_projects", "Manage Own Projects"),

    # Users
    ("user_view", "View Users"),
    ("user_create", "Create User"),
    ("user_update", "Update User"),
    ("user_delete", "Delete User"),
    ("manage_users", "Manage Users"),

    # Roles
    ("role_view", "View Roles"),
    ("role_create", "Create Role"),
    ("role_update", "Update Role"),
    ("role_delete", "Delete Role"),
    ("manage_roles", "Manage Roles"),
]


def run():
    for code, label in permissions:
        exists = Permission.query.filter_by(code=code).first()
        if not exists:
            db.session.add(
                Permission(
                    code=code,
                    label=label,
                    is_active=True
                )
            )
    db.session.commit()
    print("✅ Permissions seeded successfully")
