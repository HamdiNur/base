from flask import render_template, request, jsonify
from extensions import db
from auth.policies import is_admin

from . import projects_bp
from projects.models import Project
from projects.forms import ProjectForm
from flask import abort
# projects/routes.py
from flask_login import login_required, current_user
from users.models import User
from roles.models import Role
from extensions import csrf
from projects.members import ProjectMember
from sqlalchemy.exc import IntegrityError
from auth.decorators import permission_required
from auth.permissions import has_permission
from sqlalchemy import func
from auth.policies import (
    can_view_project,
    can_create_project,
    can_update_project,
    can_delete_project,
    can_assign_project_members,
    can_assign_project_manager,
)
@projects_bp.route("/")
@login_required
@permission_required("project_view")
def index():
    return render_template(
        "projects/project.html",
        can_create_project=can_create_project(current_user)
    )

@projects_bp.route("/add", methods=["GET"])
@login_required
@permission_required("project_create")
def add_page():
    if not can_create_project(current_user):
     abort(403)
    form = ProjectForm()
    return render_template("projects/project_add.html", form=form)



@projects_bp.route("/add", methods=["POST"])
@login_required
@permission_required("project_create")
def add():
    # 🔐 Policy check (context-free)
    if not can_create_project(current_user):
        abort(403)

    form = ProjectForm()

    if not form.validate_on_submit():
        return jsonify({"message": "Invalid project data"}), 400

    # 🚫 Duplicate name check (case-insensitive)
    exists = Project.query.filter(
        db.func.lower(Project.name) == form.name.data.strip().lower()
    ).first()

    if exists:
        return jsonify({
            "message": "A project with this name already exists"
        }), 409

    # ✅ Create project (NO AUTH LOGIC HERE)
    project = Project(
        name=form.name.data.strip(),
        description=form.description.data,
        is_active=True,
        created_by=current_user.id
    )

    db.session.add(project)
    db.session.flush()  # ensure project.id exists

    # 🎯 Ownership / manager logic belongs to POLICY
    # The policy may say: creator becomes manager
    if can_assign_project_manager(current_user):
        project.manager_id = current_user.id

        # auto-add manager as member
        db.session.add(ProjectMember(
            project_id=project.id,
            user_id=current_user.id
        ))

    db.session.commit()

    return jsonify({
        "message": "Project created successfully",
        "project_id": project.id
    }), 201

@projects_bp.route("/edit/<int:project_id>", methods=["GET"])
@login_required
def edit_page(project_id):
    project = Project.query.get_or_404(project_id)

    if not can_update_project(current_user, project):
       abort(403)
    form = ProjectForm(obj=project)

    return render_template(
        "projects/project_edit.html",
        form=form,
        project=project
    )
@projects_bp.route("/edit/<int:project_id>", methods=["POST"])
@login_required
def edit(project_id):
    project = Project.query.get_or_404(project_id)

    if not can_update_project(current_user, project):
        abort(403)

    form = ProjectForm()

    if not form.validate_on_submit():
        return jsonify({"message": "Invalid data"}), 400

    project.name = form.name.data.strip()
    project.description = form.description.data
    project.is_active = form.is_active.data

    db.session.commit()
    return jsonify({"message": "Updated"}), 200


@projects_bp.route("/delete/<int:project_id>", methods=["POST"])
@login_required
@csrf.exempt
def delete(project_id):
    project = Project.query.get_or_404(project_id)

    if not can_delete_project(current_user, project):
      abort(403)
    project = Project.query.get_or_404(project_id)

    if project.is_active:
        return jsonify({
            "message": "Only inactive projects can be deleted"
        }), 400

    # 🚫 Block deletion if members exist
    has_members = ProjectMember.query.filter_by(
        project_id=project.id
    ).count() > 0

    if has_members:
        return jsonify({
            "message": "Remove all project members before deleting"
        }), 400

    db.session.delete(project)
    db.session.commit()

    return jsonify({
        "message": "Project deleted successfully"
    }), 200

@projects_bp.route("/datatable")
@login_required
@permission_required("project_view")
def datatable():
    draw = int(request.args.get("draw", 1))
    start = int(request.args.get("start", 0))
    length = int(request.args.get("length", 10))
    search_value = request.args.get("search[value]", "").strip()

    base_query = (
        Project.query
        .outerjoin(User, Project.manager_id == User.id)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .add_columns(
            User.username.label("manager_name"),
            func.count(ProjectMember.user_id).label("members_count")
        )
        .group_by(Project.id, User.username)
    )

    if search_value:
        base_query = base_query.filter(
            Project.name.ilike(f"%{search_value}%")
        )

    records_total = Project.query.count()

    records_filtered = db.session.query(func.count()).select_from(
        base_query.subquery()
    ).scalar()

    projects = (
        base_query
        .order_by(Project.id.desc())
        .offset(start)
        .limit(length)
        .all()
    )

    data = []

    for project, manager_name, members_count in projects:
        is_owner = project.manager_id == current_user.id

        data.append({
    "id": project.id,
    "name": project.name,
    "manager": manager_name or "—",
    "members": members_count,
    "is_active": project.is_active,
    "created_at": project.created_at.strftime("%Y-%m-%d"),

    # ✅ SINGLE SOURCE OF TRUTH
    "can_edit": can_update_project(current_user, project),
    "can_delete": can_delete_project(current_user, project),
})


    return jsonify({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data
    })


@projects_bp.route("/<int:project_id>")
@login_required
@permission_required("project_view")
def detail(project_id):
    project = Project.query.get_or_404(project_id)

    members = (
        User.query
        .join(ProjectMember, ProjectMember.user_id == User.id)
        .filter(ProjectMember.project_id == project.id)
        .all()
    )

    return render_template(
        "projects/project_detail.html",
        project=project,
        members=members
    )


@projects_bp.route("/<int:project_id>/assign-manager", methods=["POST"])
@login_required
@permission_required("assign_project_manager")
def assign_manager(project_id):
    project = Project.query.get_or_404(project_id)

    if not can_assign_project_manager(current_user):
      abort(403)

    manager_id = request.form.get("manager_id")


    manager = User.query.get(manager_id)
    if not manager or not manager.is_active:
        return jsonify({"message": "Invalid manager"}), 400


    # ✅ Assign manager
    project.manager_id = manager.id

    # ✅ Auto-add manager as member
    exists = ProjectMember.query.filter_by(
        project_id=project.id,
        user_id=manager.id
    ).first()

    if not exists:
        db.session.add(ProjectMember(
            project_id=project.id,
            user_id=manager.id
        ))

    db.session.commit()

    return jsonify({
        "message": "Manager assigned successfully",
        "username": manager.username
    }), 200


@projects_bp.route("/managers/select2")
@login_required
@permission_required("project_view")
def managers_select2():
    q = request.args.get("q", "")

    # Base query: active users with username match
    users = (
        User.query
        .filter(User.is_active.is_(True))
        .filter(User.username.ilike(f"%{q}%"))
        .all()
    )

    results = []

    for u in users:
        # Only allow users with role 'Manager'
        if u.role and u.role.name.lower() == "manager":
            # Optional: If current user is a manager, exclude themselves
            if not is_admin(current_user) and u.id == current_user.id:
                continue
            results.append({"id": u.id, "text": u.username})

    return jsonify({"results": results[:10]})
@projects_bp.route("/<int:project_id>/members/select2")
@login_required
@permission_required("project_view")
def members_select2(project_id):
    q = request.args.get("q", "")

    # Users already in this project
    subquery = (
        db.session.query(ProjectMember.user_id)
        .filter(ProjectMember.project_id == project_id)
    )

    # Base query: active users, username match, not already in project
    users = (
        User.query
        .filter(User.is_active.is_(True))
        .filter(User.username.ilike(f"%{q}%"))
        .filter(~User.id.in_(subquery))
        .limit(50)  # can adjust limit
        .all()
    )

    results = []

    for u in users:
        # Exclude Admins and Managers
        if u.role and u.role.name.lower() not in ("admin", "manager"):
            results.append({"id": u.id, "text": u.username})

    return jsonify({"results": results[:10]})

@projects_bp.route("/<int:project_id>/members/add", methods=["POST"])
@login_required
@csrf.exempt
@permission_required("project_view")
def add_member(project_id):
    project = Project.query.get_or_404(project_id)

    if not can_assign_project_members(current_user, project):
        abort(403)
    

    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"message": "User required"}), 400

    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"message": "Invalid user"}), 400

    # 🚫 Prevent duplicates
    exists = ProjectMember.query.filter_by(
        project_id=project.id,
        user_id=user.id
    ).first()

    if exists:
        return jsonify({"message": "User already a member"}), 409

    db.session.add(ProjectMember(
        project_id=project.id,
        user_id=user.id
    ))
    db.session.commit()

    return jsonify({
        "message": "Member added successfully",
        "username": user.username
    }), 201

@projects_bp.route("/<int:project_id>/members/remove", methods=["POST"])
@login_required
@permission_required("project_view")
def remove_member(project_id):
    project = Project.query.get_or_404(project_id)

    if not can_assign_project_members(current_user, project):
        abort(403)


    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"message": "User required"}), 400

    member = ProjectMember.query.filter_by(
        project_id=project.id,
        user_id=user_id
    ).first()

    if not member:
        return jsonify({"message": "Member not found"}), 404

    # 🚫 Business rule: cannot remove manager
    if project.manager_id == int(user_id):
        return jsonify({
            "message": "Cannot remove project manager"
        }), 400

    db.session.delete(member)
    db.session.commit()

    return jsonify({
        "message": "Member removed successfully"
    }), 200



@projects_bp.route("/<int:project_id>/unassign-manager", methods=["POST"])
@login_required
@permission_required("assign_project_manager")
def unassign_manager(project_id):
    project = Project.query.get_or_404(project_id)

    #  Must be inactive
    if project.is_active:
        return jsonify({
            "message": "Deactivate project before unassigning manager"
        }), 400

    if not project.manager_id:
        return jsonify({
            "message": "No manager assigned"
        }), 400

    # remove manager from members
    ProjectMember.query.filter_by(
        project_id=project.id,
        user_id=project.manager_id
    ).delete()

    project.manager_id = None

    db.session.commit()

    return jsonify({
        "message": "Manager unassigned successfully"
    }), 200
