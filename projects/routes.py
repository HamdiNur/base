from flask import render_template, request, jsonify
from extensions import db
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

from sqlalchemy import func

def block_if_inactive(project):
    if not project.is_active and current_user.role.code != "ADMIN":
        abort(403)


@projects_bp.route("/")
def index():
    return render_template("projects/project.html")


@projects_bp.route("/add", methods=["GET"])
def create():
    form = ProjectForm()
    return render_template("projects/project_add.html", form=form)
@projects_bp.route("/add", methods=["POST"])
@login_required
def add():
    # 🔐 Only ADMIN or MANAGER can create projects
    if current_user.role.code not in ["ADMIN", "MANAGER"]:
        abort(403)

    form = ProjectForm()

    if not form.validate_on_submit():
        return jsonify({"message": "Invalid project data"}), 400

    # 🚫 Duplicate project name check (case-insensitive)
    existing_project = Project.query.filter(
        db.func.lower(Project.name) == form.name.data.strip().lower()
    ).first()

    if existing_project:
        return jsonify({
            "message": "A project with this name already exists"
        }), 409

    # ✅ Create project
    project = Project(
        name=form.name.data.strip(),
        description=form.description.data,
        is_active=True,
        created_by=current_user.id,
        manager_id=current_user.id if current_user.role.code == "MANAGER" else None
    )

    db.session.add(project)
    db.session.flush()  # 🔥 ensures project.id exists

    # ✅ Auto-add MANAGER as member
    if current_user.role.code == "MANAGER":
        db.session.add(ProjectMember(
            project_id=project.id,
            user_id=current_user.id
        ))

    # ✅ ONE commit only
    db.session.commit()

    return jsonify({
        "message": "Project created successfully",
        "project_id": project.id
    }), 201



@projects_bp.route("/edit/<int:project_id>", methods=["GET"])
@login_required
def edit_page(project_id):
    project = Project.query.get_or_404(project_id)

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
    role = current_user.role.code

    form = ProjectForm()

    # 🔐 VIEWER → no edits
    if role == "VIEWER":
        return jsonify({
            "message": "You only have permission to view projects."
        }), 403

    # 🔐 STAFF → ONLY toggle active/inactive
    if role == "STAFF":
        project.is_active = form.is_active.data
        db.session.commit()

        return jsonify({
            "message": "Project status updated successfully"
        }), 200

    # 🔐 MANAGER → only own projects
    if role == "MANAGER" and project.manager_id != current_user.id:
        return jsonify({
            "message": "You can only edit projects you manage."
        }), 403

    # 🔐 ADMIN / MANAGER → full validation
    if not form.validate_on_submit():
        return jsonify({"message": "Invalid project data"}), 400

    project.name = form.name.data.strip()
    project.description = form.description.data
    project.is_active = form.is_active.data

    db.session.commit()

    return jsonify({
        "message": "Project updated successfully"
    }), 200




@projects_bp.route("/delete/<int:project_id>", methods=["POST"])
@login_required
@csrf.exempt

def delete(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role.code != "ADMIN":
      return jsonify({
        "message": "You do not have permission to delete projects. Please contact an administrator."
    }), 403

    if project.is_active:
      return jsonify({"message": "Only inactive projects can be deleted"
}), 400
     # 🚫 BLOCK if members exist
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
def datatable():
    draw = int(request.args.get("draw", 1))
    start = int(request.args.get("start", 0))
    length = int(request.args.get("length", 10))
    search_value = request.args.get("search[value]", "").strip()

    base_query = (
        db.session.query(
            Project.id,
            Project.name,
            Project.is_active,
            Project.created_at,
            User.username.label("manager_name"),
            func.count(ProjectMember.user_id).label("members_count")
        )
        .outerjoin(User, Project.manager_id == User.id)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .group_by(Project.id, User.username)
    )

    # 🔍 SEARCH
    if search_value:
        base_query = base_query.filter(
            Project.name.ilike(f"%{search_value}%")
        )

    # ✅ TOTAL RECORDS (NO GROUP)
    records_total = Project.query.count()

    # ✅ FILTERED RECORDS (SUBQUERY FIX)
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
    for p in projects:
        data.append({
            "id": p.id,
            "name": p.name,
            "manager": p.manager_name or "—",
            "members": p.members_count,
            "is_active": p.is_active,
            "created_at": p.created_at.strftime("%Y-%m-%d")
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data
    })

@projects_bp.route("/<int:project_id>")
@login_required
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
def assign_manager(project_id):
    # 🔐 Admin only
    if current_user.role.code not in ["ADMIN", "MANAGER"]:
        abort(403)

    project = Project.query.get_or_404(project_id)
    block_if_inactive(project)


    manager_id = request.form.get("manager_id")
    if not manager_id:
        return jsonify({"message": "Manager is required"}), 400

    manager = User.query.get(manager_id)

    if not manager or manager.role.code != "MANAGER":
        return jsonify({"message": "Invalid manager"}), 400

    # ✅ Assign manager
    project.manager_id = manager.id

    # ✅ AUTO-ADD MANAGER AS MEMBER (THIS IS WHAT WAS MISSING)
    exists = ProjectMember.query.filter_by(
        project_id=project.id,
        user_id=manager.id
    ).first()

    if not exists:
        member = ProjectMember(
            project_id=project.id,
            user_id=manager.id
        )
        db.session.add(member)

    db.session.commit()

    return jsonify({
        "message": "Manager assigned successfully",
        "username": manager.username
    }), 200


@projects_bp.route("/managers/select2")
@login_required
def managers_select2():
    q = request.args.get("q", "")

    managers = (
        User.query
        .join(Role, User.role_id == Role.id)
        .filter(Role.code == "MANAGER")
        .filter(User.username.ilike(f"%{q}%"))
        .limit(10)
        .all()
    )

    return jsonify({
        "results": [
            {"id": u.id, "text": u.username}
            for u in managers
        ]
    })


@projects_bp.route("/<int:project_id>/members/select2")
@login_required
def members_select2(project_id):
    q = request.args.get("q", "")

    # users already in project
    subquery = (
        db.session.query(ProjectMember.user_id)
        .filter(ProjectMember.project_id == project_id)
    )

    users = (
        User.query
        .join(Role)
        .filter(Role.code.notin_(["ADMIN", "SUPER_ADMIN"]))  # 🔥 FIX
        .filter(User.is_active.is_(True))                    # ✅ optional but good
        .filter(User.username.ilike(f"%{q}%"))
        .filter(~User.id.in_(subquery))
        .limit(10)
        .all()
    )

    return jsonify({
        "results": [
            {"id": u.id, "text": u.username}
            for u in users
        ]
    })


@projects_bp.route("/<int:project_id>/members/add", methods=["POST"])
@login_required
@csrf.exempt
def add_member(project_id):
    project = Project.query.get_or_404(project_id)
    block_if_inactive(project)


    # 🔐 Permission: ADMIN or Project Manager only
    if not (
        current_user.role.code == "ADMIN"
        or project.manager_id == current_user.id
    ):
        abort(403)

    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"message": "User required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Invalid user"}), 400

    # 🔒 SAFETY NET (admins should never reach here via UI)
    if user.role.code in ["ADMIN", "SUPER_ADMIN"]:
        abort(403)

    # 🚫 Prevent duplicates
    exists = ProjectMember.query.filter_by(
        project_id=project.id,
        user_id=user.id
    ).first()

    if exists:
        return jsonify({"message": "User already a member"}), 409

    member = ProjectMember(
        project_id=project.id,
        user_id=user.id
    )

    db.session.add(member)
    db.session.commit()

    return jsonify({
        "message": "Member added successfully",
        "username": user.username
    }), 201


@projects_bp.route("/<int:project_id>/members/remove", methods=["POST"])
@login_required
def remove_member(project_id):
    project = Project.query.get_or_404(project_id)
    block_if_inactive(project)


    # 🔐 Permission: ADMIN or Project Manager
    if not (
        current_user.role.code == "ADMIN"
        or project.manager_id == current_user.id
    ):
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

    # 🚫 Optional safety: don't allow removing manager
    if project.manager_id == int(user_id):
        return jsonify({"message": "Cannot remove project manager"}), 400

    db.session.delete(member)
    db.session.commit()

    return jsonify({"message": "Member removed"}), 200


@projects_bp.route("/<int:project_id>/unassign-manager", methods=["POST"])
@login_required
def unassign_manager(project_id):
    project = Project.query.get_or_404(project_id)

    # 🔐 Admin only
    if current_user.role.code != "ADMIN":
        abort(403)

    # 🚫 Must be inactive
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

    # unset manager
    project.manager_id = None

    db.session.commit()

    return jsonify({
        "message": "Manager unassigned successfully"
    }), 200
