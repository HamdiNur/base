from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from extensions import db
from auth.decorators import permission_required
from permissions.models import Permission
from permissions.forms import PermissionForm
from sqlalchemy.exc import IntegrityError

permission_bp = Blueprint(
    "permission",
    __name__,
    url_prefix="/permissions"
)

@permission_bp.route("/")
@login_required
@permission_required("manage_roles")
def index():
    form = PermissionForm()
    return render_template("permissions/permission.html", form=form)

@permission_bp.route("/add", methods=["POST"])
@login_required
@permission_required("manage_roles")
def add():
    form = PermissionForm()

    if not form.validate_on_submit():
        return jsonify({"message": "Invalid data"}), 400

    permission = Permission(
        code=form.code.data.strip(),
        description=form.description.data,
        is_active=form.is_active.data
    )

    try:
        db.session.add(permission)
        db.session.commit()
        return jsonify({"message": "Permission created"}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Permission already exists"}), 409

# =====================
# DATATABLE
@permission_bp.route("/datatable")
@login_required
@permission_required("manage_roles")
def datatable():
    from permissions.models import Permission

    draw = int(request.args.get("draw", 1))
    start = int(request.args.get("start", 0))
    length = int(request.args.get("length", 10))
    search = request.args.get("search[value]", "")

    query = Permission.query

    if search:
        query = query.filter(Permission.code.ilike(f"%{search}%"))

    total = Permission.query.count()
    filtered = query.count()

    permissions = (
        query.order_by(Permission.id.desc())
        .offset(start)
        .limit(length)
        .all()
    )

    data = []
    for p in permissions:
        data.append({
            "id": p.id,
            "code": p.code,
            "description": p.description or "",
            "is_active": p.is_active
        })

    return jsonify({
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": filtered,
        "data": data
    })

