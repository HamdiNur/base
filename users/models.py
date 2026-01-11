from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))

    password_hash = db.Column(db.String(255))

    setup_token_hash = db.Column(db.String(255))
    must_set_password = db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    is_active = db.Column(db.Boolean, default=True)

    role = db.relationship("Role")
