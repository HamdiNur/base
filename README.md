🗂️ NGO – Project & User Management System
📌 Overview

NGO is a role-based management system designed to help organizations manage users, projects, and access control. It ensures that each user can only see and perform actions permitted by their role.

Originally developed as part of an internship program, NGO follows real-world backend patterns and emphasizes security, clean UI, and scalability.

🛠️ Technologies Used

Backend: Flask (Python)

Database: PostgreSQL

ORM: SQLAlchemy

Authentication: Flask-Login

Forms & Security: Flask-WTF (CSRF protection)

Frontend: Jinja2, Bootstrap

AJAX & UI: jQuery, DataTables, Select2, SweetAlert

📁 Key Features

Secure Login & Authentication with hashed passwords

Role-Based Access Control (RBAC)

User Management: create, view, activate/deactivate users

Role Management: admin-only permissions

Project Management: create, edit, delete projects

Assign Managers & Members with flexible permissions

Server-Side Pagination & Filtering for projects and users

Dynamic UI that hides unauthorized actions

AJAX-powered Search & Selection (Select2)

Confirmation Modals for critical actions (SweetAlert)

Activity Tracking & Audit Logs (new feature)

Notifications & Alerts for project updates (new feature)

Note: Frontend visibility is a UX enhancement. All critical actions are secured server-side.

👥 Roles & Permissions

The system uses predefined roles with different levels of access:

🔑 Admin

Full system access

Permissions:

Manage users (create, edit, delete)

Manage roles

Create, edit, delete projects

Assign managers & members

View all system data

🔑 Manager

Project-level management

Permissions:

Create projects

Manage projects they own

Assign team members

View project details

Restrictions:

Cannot manage users or roles

Cannot delete projects they don’t own

🔑 Staff

Execution-level access

Permissions:

View assigned projects

Update project status

Restrictions:

Cannot view users list

Cannot manage roles or users

Cannot create/delete projects

🔑 Viewer

Read-only access

Permissions:

View projects

Restrictions:

Cannot create, edit, or delete projects

🔐 Authentication & Security

Managed using Flask-Login

Passwords securely hashed

CSRF protection enabled for all forms

Backend permission checks enforced with decorators

Frontend dynamically hides unauthorized actions

🚀 Setup Instructions

1️⃣ Clone the repository

git clone <repo_url>
cd NGO


2️⃣ Create a virtual environment

python -m venv venv


Activate it:

Linux/Mac: source venv/bin/activate

Windows: venv\Scripts\activate

3️⃣ Install dependencies

pip install -r requirements.txt


4️⃣ Configure environment variables
Create a .env file based on .env.example and update database credentials.

5️⃣ Run database migrations

flask db upgrade


6️⃣ Seed initial data

python seed.py


This will create:

An Admin role

A default Admin user

Default Admin Login:

Username: admin

Password: admin123

7️⃣ Run the application

python app.py

//

flask run


Open your browser:
http://127.0.0.1:5000