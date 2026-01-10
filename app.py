from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user
from dotenv import load_dotenv
import os

from extensions import db, migrate, login_manager, csrf
from users.routes import user_bp
from roles.routes import role_bp
from projects import projects_bp
from auth import auth_bp
from auth.permissions import has_permission

from users.models import User
from roles.models import Role
from projects.models import Project

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
csrf.init_app(app)

# TEMP (remove later)
with app.app_context():
    db.create_all()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(role_bp)
app.register_blueprint(projects_bp)

# Make permissions available in templates
@app.context_processor
def inject_permissions():
    return dict(has_permission=has_permission)

# ✅ DASHBOARD ROUTE
@app.route("/")
@login_required
def home():
    # 🔐 Viewer → redirect to projects
    if not has_permission(current_user, "view_dashboard"):
        return redirect(url_for("projects.index"))

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

if __name__ == "__main__":
    app.run(debug=True)
