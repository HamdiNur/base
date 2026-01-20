from auth.permissions import has_permission


# =========================
# USER POLICIES
# =========================
def permission_score(user):
    """
    Rough authority level based on permissions.
    Higher score = more power.
    """
    if not user or not user.role:
        return 0

    permissions = {p.code for p in user.role.permissions if p.is_active}

    score = 0
    if "manage_users" in permissions:
        score += 100
    if "user_delete" in permissions:
        score += 30
    if "user_update" in permissions:
        score += 20
    if "user_create" in permissions:
        score += 10

    return score


def can_view_users(user):
    return has_permission(user, "user_view")


def can_create_user(user):
    return (
        has_permission(user, "user_create")
        or has_permission(user, "manage_users")
    )


def can_update_user(actor, target_user):
    if not actor or not target_user:
        return False

    # 🔑 Admin = full power
    if has_permission(actor, "manage_users"):
        return True

    if not has_permission(actor, "user_update"):
        return False

    if not target_user.is_active:
        return False

    if permission_score(target_user) > permission_score(actor):
        return False

    return True


def can_delete_user(actor, target_user):
    if not actor or not target_user:
        return False

    if has_permission(actor, "manage_users"):
        return True

    if not has_permission(actor, "user_delete"):
        return False

    if permission_score(target_user) > permission_score(actor):
        return False

    return True



# =========================
# PROJECT POLICIES
# =========================

def can_view_project(user):
    return has_permission(user, "project_view")


def can_create_project(user):
    return has_permission(user, "project_create")

def is_admin(user):
    return user.role and user.role.name.lower() == "admin"

def can_update_project(user, project):
    if not user or not project:
        return False

    # 🔑 True admin bypass
    if is_admin(user) or has_permission(user, "manage_projects"):
        return True

    if has_permission(user, "project_update_all"):
        return True

    if has_permission(user, "manage_own_projects") and project.manager_id == user.id:
        return True

    if has_permission(user, "project_update"):
        from projects.members import ProjectMember
        return ProjectMember.query.filter_by(
            project_id=project.id,
            user_id=user.id
        ).first() is not None

    return False

def can_delete_project(user, project):
    if not user or not project:
        return False

    if is_admin(user) or has_permission(user, "manage_projects"):
        return True

    if not has_permission(user, "project_delete"):
        return False

    if project.is_active:
        return False

    return True


def can_assign_project_members(user, project):
    if has_permission(user, "assign_project_members"):
        return True

    if project.manager_id == user.id:
        return True

    return False


def can_assign_project_manager(user):
    return has_permission(user, "assign_project_manager")


def user_capabilities(actor, target_user):
    return {
        "can_view": can_view_users(actor),
        "can_edit": can_update_user(actor, target_user),
        "can_delete": can_delete_user(actor, target_user),
    }
def project_capabilities(user, project):
    return {
        "can_edit": can_update_project(user, project),
        "can_delete": can_delete_project(user, project),
        "can_assign_members": can_assign_project_members(user, project),
    }
