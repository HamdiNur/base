from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from users.models import User
from users.forms import UserForm
from sqlalchemy.exc import IntegrityError
from flask import jsonify
user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/')
def index():
    users = User.query.all()
    form = UserForm()
    return render_template('user/user.html', data=users, form=form)

@user_bp.route('/add', methods=['POST'])
def add():
    form = UserForm()

    if not form.validate_on_submit():
        return jsonify({
            'status': 'error',
            'message': 'Invalid form data'
        }), 400

    user = User(
        username=form.username.data,
        full_name=form.full_name.data,
        email=form.email.data,
        user_type=form.user_type.data,
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
    


    
@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    user = User.query.get_or_404(user_id)

    # Bind form to existing user
    form = UserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.full_name = form.full_name.data
        user.email = form.email.data
        user.user_type = form.user_type.data
        user.is_active = form.is_active.data

        try:
            db.session.commit()
            return redirect(url_for('user.index'))
        except IntegrityError:
            db.session.rollback()
            form.username.errors.append("Username or email already exists")

    return render_template(
        'user/user_edit.html',
        form=form,
        data=user
    )




@user_bp.route('/delete/<int:user_id>', methods=['POST'])
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return {'status': 'success'}
