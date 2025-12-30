from extensions import db

class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(50), nullable=False, unique=True)    # for "ID"
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
