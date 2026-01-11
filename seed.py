from werkzeug.security import generate_password_hash

from extensions import db
from app import app   # change if your entry file is different

from users.models import User
from roles.models import Role


ROLES = [
    {
        "name": "Admin",
        "code": "ADMIN",
        "description": "Full system access. Responsible for managing users, roles, and all projects."
    },
    {
        "name": "Manager",
        "code": "MANAGER",
        "description": "Manages assigned projects and team members. Has read-only access to users."
    },
    {
        "name": "Staff",
        "code": "STAFF",
        "description": "Works on assigned projects with limited update permissions."
    },
    {
        "name": "Viewer",
        "code": "VIEWER",
        "description": "Read-only access to projects for monitoring and overview purposes."
    },
]


def run_seed():
    role_map = {}

    # =====================
    # CREATE ROLES
    # =====================
    for r in ROLES:
        role = Role.query.filter_by(code=r["code"]).first()
        if not role:
            role = Role(
                name=r["name"],
                code=r["code"],
                description=r["description"],
                is_active=True
            )
            db.session.add(role)
            db.session.commit()
            print(f"✅ Role created: {r['code']}")
        else:
            print(f"ℹ️ Role already exists: {r['code']}")

        role_map[r["code"]] = role

    # =====================
    # CREATE ADMIN USER
    # =====================
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            full_name="System Administrator",
            email="admin@example.com",
            role_id=role_map["ADMIN"].id,
            is_active=True,
            must_set_password=False,
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created")
    else:
        print("ℹ️ Admin user already exists")


if __name__ == "__main__":
    with app.app_context():
        run_seed()
