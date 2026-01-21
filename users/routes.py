from flask import Blueprint, render_template, request, jsonify, abort, current_app
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, current_user
from datetime import datetime
from auth.utils import generate_setup_token, hash_token
from auth.policies import (
    can_view_users,
    can_create_user,
    can_update_user,
    can_delete_user,
    user_capabilities
)
from extensions import db, login_manager, mail
from users.models import User
from users.forms import UserForm
from roles.models import Role
from auth.decorators import permission_required
from auth.permissions import has_permission
from auth.emails import send_setup_email
from flask_mail import  Message
from extensions import mail  # if you initialized Mail() in extensions.py


user_bp = Blueprint("user", __name__, url_prefix="/user")



# =====================
# USERS PAGE
@user_bp.route("/")
@login_required
@permission_required("user_view")
def index():
    form = UserForm()
    return render_template(
        "user/user.html",
        form=form,
        can_create=can_create_user(current_user)
    )

# ADD USER (AJAX)

@user_bp.route("/add", methods=["POST"])
@login_required
@permission_required("user_view")
def add():
    if not can_create_user(current_user):
        abort(403)

    form = UserForm()

    if form.role_id.data:
        form.role_id.choices = [(int(form.role_id.data), "temp")]

    if not form.validate_on_submit():
        return jsonify({"message": "Invalid form data"}), 400

    role = Role.query.get(int(form.role_id.data))
    if not role or not role.is_active:
        return jsonify({"message": "Invalid role"}), 400

    setup_token = generate_setup_token()

    user = User(
        username=form.username.data,
        full_name=form.full_name.data,
        email=form.email.data,
        role_id=form.role_id.data,
        is_active=bool(form.is_active.data),
        must_set_password=True,
        setup_token_hash=hash_token(setup_token),
        setup_token_created_at=datetime.utcnow(),
    )

    db.session.add(user)
    db.session.commit()

    # After committing, send email
    setup_link = f"{current_app.config['BASE_URL']}/auth/setup?token={setup_token}"

    try:
        msg = Message(
            subject="Set your password",
            recipients=[user.email],
            html=f"""
                <p>Hi {user.full_name},</p>
                <p>Click the link below to set your password. The link expires in 24 hours.</p>
                <p><a href="{setup_link}">Set Password</a></p>
                <p>If you didn’t expect this email, please ignore it.</p>
            """
        )
        mail.send(msg)
    except Exception as e:
        print("Email sending failed:", e)

    return jsonify({"message": "User created successfully. Setup email sent."}), 201

# EDIT USER PAGE
# =====================
@user_bp.route("/edit/<int:user_id>", methods=["GET"])
@login_required
@permission_required("user_view")
def edit_page(user_id):
    user = User.query.get_or_404(user_id)

    if not can_update_user(current_user, user):
        abort(403)

    form = UserForm(obj=user)

    # ✅ ALWAYS SET CHOICES
    roles = Role.query.all()
    form.role_id.choices = [
        (r.id, r.name) for r in roles
    ]

    return render_template(
        "user/user_edit.html",
        form=form,
        data=user,
        can_manage=has_permission(current_user, "manage_users")

    )
@user_bp.route("/edit/<int:user_id>", methods=["POST"])
@login_required
@permission_required("user_view")
def edit(user_id):
    user = User.query.get_or_404(user_id)

    if not can_update_user(current_user, user):
        abort(403)

    form = UserForm()

    # ✅ ALWAYS SET CHOICES BEFORE VALIDATION
    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]
    
    # ✅ THIS IS THE KEY FIX
    if not has_permission(current_user, "manage_users"):
        del form.username
        del form.role_id
        del form.is_active


    if not form.validate_on_submit():
        return jsonify({"message": "Invalid form submission"}), 400

    # ✅ Everyone allowed
    user.full_name = form.full_name.data
    user.email = form.email.data

    # 🔐 Admin-only
    if has_permission(current_user, "manage_users"):
        user.username = form.username.data
        user.role_id = form.role_id.data
        user.is_active = bool(form.is_active.data)

    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200


# =====================
# DELETE USER
# =====================
@user_bp.route("/delete/<int:user_id>", methods=["POST"])
@login_required
@permission_required("user_view")
def delete(user_id):
    user = User.query.get_or_404(user_id)

    if not can_delete_user(current_user, user):
        abort(403)

    db.session.delete(user)
    db.session.commit()
    return jsonify({"status": "success"})


# =====================
# SELECT2 ROLE SEARCH
# =====================
@user_bp.route("/roles/search")
@login_required
@permission_required("user_view")
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
@login_required
@permission_required("user_view")
def datatable():

    # =====================
    # 1. DATATABLE PARAMS
    # =====================
    draw = request.args.get("draw", type=int, default=1)
    start = request.args.get("start", type=int, default=0)
    length = request.args.get("length", type=int, default=10)
    search = request.args.get("search[value]", "").strip()

    status = request.args.get("status")
    role = request.args.get("role")

    # =====================
    # 2. BASE QUERY
    # =====================
    query = User.query.outerjoin(Role)

    # =====================
    # 3. GLOBAL SEARCH
    # =====================
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Role.name.ilike(f"%{search}%"),
            )
        )

    # =====================
    # 4. STATUS FILTER
    # =====================
    if status == "Active":
        query = query.filter(User.is_active.is_(True))
    elif status == "Inactive":
        query = query.filter(User.is_active.is_(False))

    # =====================
    # 5. ROLE FILTER
    # =====================
    if role and role.isdigit():
        query = query.filter(User.role_id == int(role))

    # =====================
    # 6. COUNTS (IMPORTANT)
    # =====================
    records_total = User.query.count()
    records_filtered = query.count()

    # =====================
    # 7. ORDERING
    # =====================
    order_col_index = request.args.get("order[0][column]", type=int)
    order_dir = request.args.get("order[0][dir]", "asc")

    columns = [
        User.id,
        User.username,
        User.full_name,
        User.email,
        Role.name,
    ]

    if order_col_index is not None and order_col_index < len(columns):
        col = columns[order_col_index]
        if order_dir == "desc":
            col = col.desc()
        query = query.order_by(col)

    # =====================
    # 8. PAGINATION
    # =====================
    users = query.offset(start).limit(length).all()

    # =====================
    # 9. BUILD RESPONSE DATA
    # =====================
    data = []

    for u in users:
        caps = user_capabilities(current_user, u)

        # ---- actions ----
        actions = ""

        if caps["can_edit"]:
            actions += f"""
            <a class="dropdown-item" href="/user/edit/{u.id}">
                <i class="fa fa-pencil"></i> Edit
            </a>
            """

        if caps["can_delete"]:
            actions += f"""
            <a href="javascript:void(0)"
               class="dropdown-item delete-user"
               data-id="{u.id}">
                <i class="fa fa-trash-o"></i> Delete
            </a>
            """

        action_html = ""
        if actions:
            action_html = f"""
            <div class="dropdown dropdown-action text-center">
                <a href="#" class="action-icon dropdown-toggle" data-toggle="dropdown">
                    <i class="material-icons">more_vert</i>
                </a>
                <div class="dropdown-menu dropdown-menu-right">
                    {actions}
                </div>
            </div>
            """

        # Status badge
        status_html = (
            '<span class="badge bg-inverse-success">Active</span>'
            if u.is_active
            else '<span class="badge bg-inverse-danger">Inactive</span>'
        )


        # ---- ALWAYS append row ----
        data.append({
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role.name if u.role else "—",
            "status": status_html,
            "action": action_html,
        })

    # =====================
    # 10. FINAL RESPONSE
    # =====================
    return jsonify({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data,
    })

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user

    if request.method == "POST":
        user.full_name = request.form.get("full_name")
        user.email = request.form.get("email")

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

    return render_template("user/profile.html", user=user)
