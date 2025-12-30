from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from roles.models import Role
from flask import jsonify

role_bp = Blueprint('role', __name__, url_prefix='/roles')

@role_bp.route('/')
def index():
    roles = Role.query.all()
    return render_template('roles/role.html', roles=roles)
@role_bp.route('/add', methods=['GET'])
def create():
    return render_template('roles/role_add.html')


@role_bp.route('/add', methods=['POST'])
def add():
    rolename = request.form.get('RoleName')
    role_code = request.form.get('code')
    description = request.form.get('Description')
    is_active = True if request.form.get('is_active') else False

    # 1 Basic validation
    if not rolename or not role_code:
        return jsonify({
            "message": "Role name and code are required"
        }), 400

    #  2 Check if role already exists
    existing_role = Role.query.filter_by(name=rolename).first()
    if existing_role:
        # ⛔ STOP HERE — NO REDIRECT
        return jsonify({
            "message": "Role already exists. Please create a different role."
        }), 409   # 👈 THIS IS THE KEY

    # 3Create role
    role = Role(
        name=rolename,
        code=role_code,
        description=description,
        is_active=is_active
    )

    db.session.add(role)
    db.session.commit()

    return jsonify({
        "message": "Role created successfully"
    }), 201
@role_bp.route('/edit/<int:role_id>', methods=['GET'])
def edit_page(role_id):
    role = Role.query.get_or_404(role_id)
    return render_template('roles/role_edit.html', role=role)
@role_bp.route('/edit/<int:role_id>', methods=['POST'])
def edit(role_id):
    role = Role.query.get_or_404(role_id)

    rolename = request.form.get('RoleName')
    code = request.form.get('code')
    description = request.form.get('Description')

    if not rolename or not code:
        return jsonify({"message": "Invalid form submission"}), 400

    existing_role = Role.query.filter(
        Role.name == rolename,
        Role.id != role_id
    ).first()

    if existing_role:
        return jsonify({
            "message": "Role name already exists"
        }), 409

    role.name = rolename
    role.code = code
    role.description = description
    role.is_active = True if request.form.get('is_active') else False

    db.session.commit()

    return jsonify({
        "message": "Role updated successfully"
    }), 200



@role_bp.route('/delete/<int:role_id>', methods=['POST'])
def delete(role_id):
    role = Role.query.get_or_404(role_id)

    db.session.delete(role)
    db.session.commit()

    return jsonify({
        "message": "Role deleted successfully"
    }), 200