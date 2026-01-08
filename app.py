from flask import Flask, render_template
from extensions import db, csrf
from users.routes import user_bp
from roles.routes import role_bp   # ✅ ADD THIS
from projects import projects_bp
from auth import auth_bp
from extensions import db, migrate, login_manager
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
csrf.init_app(app)  # 🔥 REQUIRED

# TEMP: create tables once
with app.app_context():
    db.create_all()

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(role_bp)    
app.register_blueprint(projects_bp)
app.register_blueprint(auth_bp)


@app.route('/')
def home():
    return render_template('dashboard/index.html')

if __name__ == '__main__':
    app.run(debug=True)
