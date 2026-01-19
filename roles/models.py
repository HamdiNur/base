from extensions import db
from permissions.models import role_permission


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))  # 🔥 REQUIRED
    is_active = db.Column(db.Boolean, default=True)

    permissions = db.relationship(
      "Permission",
    secondary=role_permission,
    backref=db.backref("roles", lazy="dynamic")
   )

    def __repr__(self):
        return f"<Role {self.code}>"
