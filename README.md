🗂️ TaskPlate – Project & User Management System
📌 Overview

TaskPlate is an internal role-based management system designed for organizations to manage:

Users and roles

Projects and team members

Access control using permissions

The system ensures that each user can only see and perform actions allowed by their role.

This project was developed as part of an internship learning program using Flask and Python, following real-world backend patterns.

🛠️ Technologies Used

Backend: Flask (Python)

Database: PostgreSQL

ORM: SQLAlchemy

Authentication: Flask-Login

Forms & Security: Flask-WTF (CSRF protection)

Frontend: Jinja2, Bootstrap

AJAX & UI: jQuery, DataTables, Select2, SweetAlert

📁 Project Features

Secure login system

Role-based access control (RBAC)

User management (create, view, activate/deactivate)

Role management (admin-only)

Project creation and management

Assigning managers and project members

Server-side pagination and filtering

Clean and permission-aware UI

👥 Roles & Permissions

The system uses roles, and each role has a specific set of permissions.

🔑 Roles Overview
1  Admin

Full system access.

Permissions:

View dashboard

Manage users (create, edit, delete)

Manage roles

Create, edit, and delete projects

Assign managers and members

View all data in the system

2  Manager

Project-level management only.

Permissions:

View users list (read-only)

Create projects

Manage projects they own

Assign staff members to their projects

View project details

Restrictions:

Cannot create/edit/delete users

Cannot manage roles

Cannot delete projects

3 Staff

Execution-level access.

Permissions:

View assigned projects

Update project status (limited)

Restrictions:

Cannot view users list

Cannot manage users or roles

Cannot create or delete projects

4 Viewer

Read-only access.

Permissions:

View projects only

Restrictions:

No create, edit, or delete permissions

🔐 Authentication & Security

Authentication is handled using Flask-Login

Passwords are securely hashed

CSRF protection is enabled for all forms

Backend permission checks are enforced using decorators

Frontend UI hides unauthorized actions for better user experience

Note: UI visibility does not replace backend security. All critical actions are protected server-side.


🚀 Setup Instructions
1 Clone or Extract the Project
git clone <repository-url>
cd taskplate

2 Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

3 Install Dependencies
pip install -r requirements.txt



Run Database Migrations (if applicable)
flask db upgrade


🌱 Initial Data (IMPORTANT)

Since the application uses a local database, the system includes a seed script to create initial data.

👉 Run the seed script:
python seed.py


This will create:

An Admin role

A default Admin user

🔐 Default Admin Login
Username: admin
Password: admin123


Running the Application
python app.py

Or:

flask run


Then open:

http://127.0.0.1:5000