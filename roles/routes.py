from flask import Blueprint, render_template, request, jsonify
from extensions import db
from roles.models import Role
from roles.forms import RoleForm
from sqlalchemy import or_
from flask_login import login_required
from flask import abort
from flask_login import current_user
from users.models import User
from extensions import csrf
from auth.decorators import permission_required
from sqlalchemy.exc import IntegrityError
from permissions.models import Permission

role_bp = Blueprint('role', __name__, url_prefix='/roles')



# =========================
# LIST ROLES
# =========================
@role_bp.route("/")
@login_required
@permission_required("manage_roles")
def index():
    return render_template("roles/role.html")
# CREATE ROLE (PAGE)
# =========================
@role_bp.route('/add', methods=['GET'])
@login_required
@permission_required("manage_roles")
def create():
    form = RoleForm()
    return render_template('roles/role_add.html', form=form)


# =========================
# CREATE ROLE (AJAX)
# =========================
@role_bp.route('/add', methods=['POST'])
@login_required
@permission_required("manage_roles")
def add():
    form = RoleForm()

    # ✅ WTForms validation
    if not form.validate_on_submit():
        return jsonify({
            "message": "Invalid form submission"
        }), 400

    # ✅ Check duplicate role name
    existing_role = Role.query.filter_by(name=form.name.data).first()
    if existing_role:
        return jsonify({
            "message": "Role already exists. Please create a different role."
        }), 409

    role = Role(
        name=form.name.data,
        code=form.code.data,
        description=form.description.data,
        is_active=form.is_active.data
    )

    db.session.add(role)
    db.session.commit()

    return jsonify({
        "message": "Role created successfully"
    }), 201


# =========================
# EDIT ROLE (PAGE)
# =========================

@role_bp.route('/edit/<int:role_id>', methods=['GET'])
@login_required
@permission_required("manage_roles")
def edit_page(role_id):
    role = Role.query.get_or_404(role_id)

    form = RoleForm(obj=role)

    permissions = Permission.query.order_by(Permission.code).all()

    return render_template(
        'roles/role_edit.html',
        form=form,
        role=role,
        permissions=permissions
    )


# =========================
# EDIT ROLE (AJAX)
# =========================
@role_bp.route('/edit/<int:role_id>', methods=['POST'])
@login_required
@permission_required("manage_roles")
def edit(role_id):
    role = Role.query.get_or_404(role_id)
    form = RoleForm()

    if not form.validate_on_submit():
        return jsonify({"message": "Invalid form submission"}), 400

    name = form.name.data.strip()
    code = form.code.data.strip()

    existing_role = Role.query.filter(
        or_(
            db.func.lower(Role.name) == name.lower(),
            db.func.lower(Role.code) == code.lower()
        ),
        Role.id != role_id
    ).first()

    if existing_role:
        return jsonify({
            "message": "Role name or code already exists"
        }), 409

    role.name = name
    role.code = code
    role.description = form.description.data
    role.is_active = form.is_active.data

    db.session.commit()

    return jsonify({"message": "Role updated successfully"}), 200

# =========================
# Assigning  ROLE PERMISSIONS
# =========================
@role_bp.route("/<int:role_id>/permissions", methods=["GET", "POST"])
@login_required
@permission_required("manage_roles")
def role_permissions(role_id):
    role = Role.query.get_or_404(role_id)

    # =========================
    # POST → ASSIGN PERMISSIONS
    # =========================
    if request.method == "POST":
        permission_ids = request.form.getlist("permissions[]")

        # 🚨 SAFETY: prevent accidental wipe
        if not permission_ids:
            return jsonify({
                "message": "At least one permission must be selected"
            }), 400

        permissions = Permission.query.filter(
            Permission.id.in_(permission_ids),
            Permission.is_active.is_(True)
        ).all()

        role.permissions = permissions
        db.session.commit()

        return jsonify({
            "message": "Permissions assigned successfully"
        }), 200

    # =========================
    # GET → SHOW ASSIGN PAGE
    # =========================
    all_permissions = Permission.query.filter_by(is_active=True).all()

    grouped = {
        "projects": [],
        "users": [],
        "roles": [],
        "dashboard": []
    }

    for perm in all_permissions:
        code = perm.code or ""

        # 🔹 PROJECT PERMISSIONS
        if "project" in code:
            grouped["projects"].append(perm)

        # 🔹 USER PERMISSIONS
        elif "user" in code:
            grouped["users"].append(perm)

        # 🔹 ROLE PERMISSIONS
        elif "role" in code:
            grouped["roles"].append(perm)

        # 🔹 DASHBOARD
        elif code == "view_dashboard":
            grouped["dashboard"].append(perm)

    # ✅ THIS IS THE KEY PHASE-3 FIX
    assigned_permission_ids = {p.id for p in role.permissions}

    roles = Role.query.filter_by(is_active=True).all()

    return render_template(
        "roles/role-permissions.html",
        role=role,
        roles=roles,
        permissions=grouped,
        assigned_permission_ids=assigned_permission_ids
    )



@role_bp.route('/delete/<int:role_id>', methods=['POST'])
@login_required
@csrf.exempt
@permission_required("manage_roles")
def delete(role_id):

    role = Role.query.get_or_404(role_id)

    if role.code.upper() == "ADMIN":
      return jsonify({"message": "ADMIN role cannot be deleted"}), 403

    if current_user.role_id == role.id:
        return jsonify({"message": "You cannot delete your own role"}), 403

    if User.query.filter(User.role_id == role.id).count() > 0:
       return jsonify({"message": "Role is assigned to users"}), 409


    try:
        db.session.delete(role)
        db.session.commit()
    except IntegrityError as e:
            return jsonify({
        "message": "Role is referenced elsewhere"
    }), 409

    return jsonify({"message": "Role deleted successfully"}), 200

@role_bp.route("/select2")
def roles_select2():
    q = request.args.get("q", "")

    roles = (
        Role.query
        .filter(Role.is_active.is_(True))
        .filter(Role.name.ilike(f"%{q}%"))
        .limit(10)
        .all()
    )

    return jsonify({
        "results": [
            {"id": r.id, "text": r.name}
            for r in roles
        ]
    })

@role_bp.route("/datatable")
@login_required
@permission_required("manage_roles")
def datatable():
    draw = int(request.args.get("draw", 1))
    start = int(request.args.get("start", 0))
    length = int(request.args.get("length", 10))
    search_value = request.args.get("search[value]", "").strip()

    query = Role.query

    # 🔍 SEARCH (name, code, description)
    if search_value:
        query = query.filter(
            or_(
                Role.name.ilike(f"%{search_value}%"),
                Role.code.ilike(f"%{search_value}%"),
                Role.description.ilike(f"%{search_value}%")
            )
        )

    total_records = Role.query.count()
    filtered_records = query.count()

    roles = (
        query
        .order_by(Role.id.desc())
        .offset(start)
        .limit(length)
        .all()
    )

    data = []
    for r in roles:
        data.append({
            "id": r.id,
            "name": r.name,
            "code": r.code,
            "description": r.description or "",
            "is_active": r.is_active
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })



@role_bp.route("/permissions")
@login_required
@permission_required("manage_roles")
def permissions_home():
    roles = Role.query.filter_by(is_active=True).all()
    return render_template(
        "roles/permissions_home.html",
        roles=roles
    )
