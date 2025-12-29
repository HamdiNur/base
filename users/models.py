from extensions import db

class User(db.Model):
    __tablename__ = 'user'  # keep as required

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    user_type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
