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
    roles = Role.query.all()   # 👈 ADD THIS

    form = UserForm()

    # ✅ Load roles into SelectField
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

    return render_template('user/user.html', 
                           data=users, roles=roles ,form=form)


@user_bp.route('/add', methods=['POST'])
def add():
    form = UserForm()
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

    if not form.validate_on_submit():
        return jsonify({
            'status': 'error',
            'message': 'Invalid form data'
        }), 400

    user = User(
        username=form.username.data,
        full_name=form.full_name.data,
        email=form.email.data,
        role_id=form.role_id.data,   # ✅ FIX
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
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

    return render_template(
        'user/user_edit.html',
        form=form,
                data=user   # ✅ THIS FIXES IT

    )
@user_bp.route('/edit/<int:user_id>', methods=['POST'])
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm()

    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

    if not form.validate_on_submit():
        return jsonify({
            "message": "Invalid form submission"
        }), 400

    user.username = form.username.data
    user.full_name = form.full_name.data
    user.email = form.email.data
    user.role_id = form.role_id.data
    user.is_active = form.is_active.data

    try:
        db.session.commit()
        return jsonify({
            "message": "User updated successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "message": "Username or email already exists"
        }), 409



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
        Role.name.ilike(f'%{q}%')
    ).limit(10).all()

    return jsonify([
        {"id": r.id, "text": r.name}
        for r in roles
    ])
