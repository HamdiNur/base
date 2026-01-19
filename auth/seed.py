from extensions import db
from roles.models import Role
from permissions.models import Permission


def seed_admin_permissions():
    """
    Ensure ADMIN role always has ALL active permissions.
    Safe to run multiple times.
    """

    admin = Role.query.filter_by(code="ADMIN").first()
    if not admin:
        print("⚠️ ADMIN role not found, skipping admin seeding")
        return

    permissions = Permission.query.filter_by(is_active=True).all()

    # Assign only if missing
    admin.permissions = permissions
    db.session.commit()

    print("✅ ADMIN role seeded with all permissions")
