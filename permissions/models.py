from extensions import db

# 🔗 Association table (MUST be here or imported)
role_permission = db.Table(
    "role_permission",
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True
    ),
    db.Column(
        "permission_id",
        db.Integer,
        db.ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Permission(db.Model):
    __tablename__ = "permission"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(100), unique=True, nullable=False)
    label = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f"<Permission {self.code}>"
