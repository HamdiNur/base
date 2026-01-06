from flask import Blueprint, render_template, request, jsonify
from extensions import db
from roles.models import Role
from roles.forms import RoleForm
from sqlalchemy import or_

role_bp = Blueprint('role', __name__, url_prefix='/roles')


# =========================
# LIST ROLES
# =========================
@role_bp.route('/')
def index():
    return render_template('roles/role.html')

# =========================
# CREATE ROLE (PAGE)
# =========================
@role_bp.route('/add', methods=['GET'])
def create():
    form = RoleForm()
    return render_template('roles/role_add.html', form=form)


# =========================
# CREATE ROLE (AJAX)
# =========================
@role_bp.route('/add', methods=['POST'])
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
def edit_page(role_id):
    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)

    return render_template(
        'roles/role_edit.html',
        form=form,
        role=role
    )


# =========================
# EDIT ROLE (AJAX)
# =========================
from sqlalchemy import or_

@role_bp.route('/edit/<int:role_id>', methods=['POST'])
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
# DELETE ROLE
# =========================
@role_bp.route('/delete/<int:role_id>', methods=['POST'])
def delete(role_id):
    role = Role.query.get_or_404(role_id)

    # ⚠️ Safety check (IMPORTANT)
    if role.users:
        return jsonify({
            "message": "Cannot delete role assigned to users"
        }), 400

    db.session.delete(role)
    db.session.commit()

    return jsonify({
        "message": "Role deleted successfully"
    }), 200


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
