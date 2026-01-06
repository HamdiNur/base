from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.exc import IntegrityError

from extensions import db
from users.models import User
from users.forms import UserForm
from roles.models import Role


user_bp = Blueprint("user", __name__, url_prefix="/user")


# =====================
# USERS PAGE
# =====================
@user_bp.route("/")
def index():
    form = UserForm()
    form.role_id.choices = []  # Select2 handles loading
    return render_template("user/user.html", form=form)


# =====================
# ADD USER (AJAX)
# =====================
@user_bp.route("/add", methods=["POST"])
def add():
    form = UserForm()

    # IMPORTANT: allow Select2 value
    form.role_id.choices = [(form.role_id.data, "temp")]

    if not form.validate_on_submit():
        return jsonify({"message": "Invalid form data"}), 400

    role = Role.query.get(form.role_id.data)
    if not role or not role.is_active:
        return jsonify({"message": "Selected role is inactive"}), 400

    user = User(
        username=form.username.data,
        full_name=form.full_name.data,
        email=form.email.data,
        role_id=form.role_id.data,
        is_active=bool(form.is_active.data)
    )

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Username or email already exists"}), 409


# =====================
# EDIT USER PAGE
# =====================
@user_bp.route("/edit/<int:user_id>")
def edit_page(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)

    roles = Role.query.all()
    form.role_id.choices = [
        (r.id, f"{r.name} (Inactive)" if not r.is_active else r.name)
        for r in roles
    ]

    return render_template(
        "user/user_edit.html",
        form=form,
        data=user
    )


# =====================
# EDIT USER (AJAX)
# =====================
@user_bp.route("/edit/<int:user_id>", methods=["POST"])
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm()

    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]

    if not form.validate_on_submit():
        return jsonify({"message": "Invalid form submission"}), 400

    role = Role.query.get(form.role_id.data)
    if not role or not role.is_active:
        return jsonify({"message": "Selected role is inactive"}), 400

    user.username = form.username.data
    user.full_name = form.full_name.data
    user.email = form.email.data
    user.role_id = form.role_id.data
    user.is_active = bool(form.is_active.data)

    try:
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Username or email already exists"}), 409


# =====================
# DELETE USER
# =====================
@user_bp.route("/delete/<int:user_id>", methods=["POST"])
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"status": "success"})


# =====================
# SELECT2 ROLE SEARCH
# =====================
@user_bp.route("/roles/search")
def role_search():
    q = request.args.get("q", "")

    roles = (
        Role.query
        .filter(Role.is_active.is_(True))
        .filter(Role.name.ilike(f"%{q}%"))
        .limit(10)
        .all()
    )

    return jsonify([
        {"id": r.id, "text": r.name}
        for r in roles
    ])


# =====================
# DATATABLE SERVER SIDE
# =====================
@user_bp.route("/datatable")
def datatable():
    draw = request.args.get("draw", type=int)
    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)
    search = request.args.get("search[value]", "")

    status = request.args.get("status")
    role = request.args.get("role")

    base_query = User.query.join(User.role)
    query = base_query

    # GLOBAL SEARCH
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Role.name.ilike(f"%{search}%")
            )
        )

    # STATUS FILTER
    if status == "Active":
        query = query.filter(User.is_active.is_(True))
    elif status == "Inactive":
        query = query.filter(User.is_active.is_(False))

    # ROLE FILTER
    if role and role.isdigit():
        query = query.filter(User.role_id == int(role))

    records_total = base_query.count()
    records_filtered = query.count()

    users = query.offset(start).limit(length).all()

    data = []
    for u in users:
        data.append([
            u.id,
            u.username,
            u.full_name,
            u.email,
            u.role.name,
            '<span class="badge bg-inverse-success">Active</span>'
            if u.is_active else
            '<span class="badge bg-inverse-danger">Inactive</span>',
            f"""
            <div class="dropdown dropdown-action text-center">
              <a href="#" class="action-icon dropdown-toggle" data-toggle="dropdown">
                <i class="material-icons">more_vert</i>
              </a>
              <div class="dropdown-menu dropdown-menu-right">
                <a class="dropdown-item" href="/user/edit/{u.id}">
                  <i class="fa fa-pencil"></i> Edit
                </a>
                <a href="javascript:void(0)" class="dropdown-item delete-user" data-id="{u.id}">
                  <i class="fa fa-trash-o"></i> Delete
                </a>
              </div>
            </div>
            """
        ])

    return jsonify({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data
    })
