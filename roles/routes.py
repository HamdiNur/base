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
    roles = Role.query.all()
    return render_template('roles/role.html', roles=roles)


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
