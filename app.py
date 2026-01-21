from flask import Flask, render_template, redirect, url_for,abort
from flask_login import login_required, current_user
from dotenv import load_dotenv
import os
load_dotenv()
from users.routes import user_bp
from roles.routes import role_bp
from projects import projects_bp
from auth import auth_bp
from auth.permissions import has_permission
from permissions.routes import permission_bp

from users.models import User
from roles.models import Role
from projects.models import Project
from auth.seed import seed_admin_permissions
from config import Config
from extensions import db, migrate, login_manager, csrf, mail



app = Flask(__name__)
app.config.from_object(Config)

# Init extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
csrf.init_app(app)
mail.init_app(app)

# TEMP (remove later)
with app.app_context():
    db.create_all()
    # seed_admin_permissions()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp)
app.register_blueprint(role_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(permission_bp)

# 🔐 Permissions for templates
@app.context_processor
def inject_permissions():
    return dict(has_permission=has_permission)

# 🧠 Policies for templates (context-aware UI)
@app.context_processor
def inject_policies():
    from auth.policies import (
        can_view_project,
        can_create_project,
        can_update_project,
        can_delete_project,
        can_assign_project_members,
        can_assign_project_manager,
        can_view_users,
        can_create_user,
        can_update_user,
        can_delete_user,
    )

    return dict(
        can_view_project=can_view_project,
        can_create_project=can_create_project,
        can_update_project=can_update_project,
        can_delete_project=can_delete_project,
        can_assign_project_members=can_assign_project_members,
        can_assign_project_manager=can_assign_project_manager,
        can_view_users=can_view_users,
        can_create_user=can_create_user,
        can_update_user=can_update_user,
        can_delete_user=can_delete_user,
    )

# 🏠 Dashboard
@app.route("/")
@login_required
def home():

    # 🔐 DASHBOARD (ADMIN / DASHBOARD USERS)
    if has_permission(current_user, "view_dashboard"):

        stats = {
            "total_projects": Project.query.count(),
            "active_projects": Project.query.filter_by(is_active=True).count(),
            "total_users": User.query.count(),
            "active_users": User.query.filter_by(is_active=True).count(),
            "roles": Role.query.filter_by(is_active=True).count(),
        }

        recent_users = (
            User.query
            .order_by(User.id.desc())
            .limit(5)
            .all()
        )

        recent_projects = (
            Project.query
            .order_by(Project.created_at.desc())
            .limit(5)
            .all()
        )

        return render_template(
            "dashboard/index.html",
            stats=stats,
            recent_users=recent_users,
            recent_projects=recent_projects
        )

    # 🔹 PROJECTS
    if has_permission(current_user, "project_view"):
        return redirect(url_for("projects.index"))

    # 🔹 USERS
    if has_permission(current_user, "user_view"):
        return redirect(url_for("user.index"))

    # 🔹 ROLES
    if has_permission(current_user, "manage_roles"):
        return redirect(url_for("role.index"))

    # 🚫 NOTHING ALLOWED
    abort(403)


if __name__ == "__main__":
    app.run(debug=True)
