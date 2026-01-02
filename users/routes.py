from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlalchemy.exc import IntegrityError

from extensions import db
from users.models import User
from users.forms import UserForm
from roles.models import Role   # ✅ IMPORTANT

user_bp = Blueprint('user', __name__, url_prefix='/user')
@user_bp.route('/')
def index():
    users = User.query.all()
    roles = Role.query.filter_by(is_active=True).all()

    form = UserForm()
    form.role_id.choices = [(r.id, r.name) for r in roles]

    return render_template(
        'user/user.html',
        data=users,
        roles=roles,
        form=form
    )



@user_bp.route('/add', methods=['POST'])
def add():
    form = UserForm()

    active_roles = Role.query.filter_by(is_active=True).all()
    form.role_id.choices = [(r.id, r.name) for r in active_roles]

    if not form.validate_on_submit():
        return jsonify({
            'status': 'error',
            'message': 'Invalid form data'
        }), 400

    role = Role.query.get(form.role_id.data)
    if not role or not role.is_active:
        return jsonify({
            "message": "Selected role is inactive"
        }), 400

    user = User(
        username=form.username.data,
        full_name=form.full_name.data,
        email=form.email.data,
        role_id=form.role_id.data,
        is_active=form.is_active.data
    )

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'User created successfully'
        })
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Username or email already exists'
        }), 409


@user_bp.route('/edit/<int:user_id>', methods=['GET'])
def edit_page(user_id):
    user = User.query.get_or_404(user_id)

    form = UserForm(obj=user)
    roles = Role.query.all()

    choices = []
    for r in roles:
       label = r.name
       if not r.is_active:
           label = f"{r.name} (Inactive)"
       choices.append((r.id, label))

    form.role_id.choices = choices

    return render_template(
        'user/user_edit.html',
        form=form,
                data=user   # ✅ THIS FIXES IT

    )
    

@user_bp.route('/edit/<int:user_id>', methods=['POST'])
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm()

    roles = Role.query.all()
    choices = []
    for r in roles:
        label = r.name
        if not r.is_active:
            label = f"{r.name} (Inactive)"
        choices.append((r.id, label))

    form.role_id.choices = choices

    if not form.validate_on_submit():
        return jsonify({
            "message": "Invalid form submission"
        }), 400

    role = Role.query.get(form.role_id.data)
    if not role or not role.is_active:
        return jsonify({
            "message": "Selected role is inactive"
        }), 400

    user.username = form.username.data
    user.full_name = form.full_name.data
    user.email = form.email.data
    user.role_id = form.role_id.data
    user.is_active = form.is_active.data

    try:
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Username or email already exists"}), 409


@user_bp.route('/delete/<int:user_id>', methods=['POST'])
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return {'status': 'success'}

@user_bp.route('/roles/search')
def role_search():
    q = request.args.get('q', '')
    roles = Role.query.filter(
    Role.is_active == True,
    Role.name.ilike(f'%{q}%')
).limit(10).all()

    return jsonify([
        {"id": r.id, "text": r.name}
        for r in roles
    ])

