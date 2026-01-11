from extensions import db
from datetime import datetime


class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
 # ✅ NEW: assigned manager
    manager_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    creator = db.relationship("User", foreign_keys=[created_by])
    manager = db.relationship("User", foreign_keys=[manager_id])
    # creator = db.relationship("User", backref="projects")
