from flask import render_template, redirect, url_for, flash, session, abort, request,current_app

from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from auth.utils import hash_token
from extensions import db
from . import auth_bp
from auth.forms import LoginForm, SetPasswordForm
from users.models import User
from auth.emails import send_setup_email
from flask_mail import  Message
from extensions import mail  
from auth.utils import generate_setup_token, hash_token

# =====================
# LOGIN
# =====================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("Invalid username or password", "danger")
            return render_template("auth/login.html", form=form)
        if not user.is_active:
            flash("Your account is inactive. Contact admin.", "warning")
            return render_template("auth/login.html", form=form)
        if user.must_set_password:
            flash("Please use the setup link sent to your email.", "warning")
            return render_template("auth/login.html", form=form)
        if not user.password_hash or not check_password_hash(user.password_hash, form.password.data):
            flash("Invalid username or password", "danger")
            return render_template("auth/login.html", form=form)
        login_user(user)
        return redirect(url_for("home"))
    return render_template("auth/login.html", form=form)

# =====================
# LOGOUT
# =====================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

# =====================
# SET PASSWORD (FIRST LOGIN)
# =====================

@auth_bp.route("/set-password", methods=["GET", "POST"])
def set_password():
    user_id = session.get("password_setup_user_id")
    if not user_id:
        flash("Session expired or invalid link", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user:
        abort(404)

    form = SetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        user.must_set_password = False
        user.setup_token_hash = None
        user.setup_token_created_at = None
        db.session.commit()
        flash("Password set successfully. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/set_password.html", form=form)

@auth_bp.route("/setup")
def setup_account():
    token = request.args.get("token")
    if not token:
        abort(400)

    token_hash = hash_token(token)
    user = User.query.filter_by(
        setup_token_hash=token_hash,
        must_set_password=True,
        is_active=True
    ).first()

    if not user:
        flash("Invalid setup link.", "danger")
        return redirect(url_for("auth.login"))

    # EXPIRY: 2 minutes for testing
    if not user.setup_token_created_at or \
       (datetime.utcnow() - user.setup_token_created_at > timedelta(minutes=2)):
        session["resend_user_id"] = user.id
        return render_template("auth/setup-expired.html")  # render the expired page

    # Token valid → allow password setup
    session["password_setup_user_id"] = user.id
    return redirect(url_for("auth.set_password"))


@auth_bp.route("/resend-setup")
def resend_setup_email():
    user_id = session.get("resend_user_id")
    if not user_id:
        flash("No user selected for setup email.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user or not user.must_set_password:
        flash("User cannot receive setup email.", "danger")
        return redirect(url_for("auth.login"))

    # RATE LIMIT: prevent resend if last token was created < 2 min ago
    if user.setup_token_created_at and (datetime.utcnow() - user.setup_token_created_at < timedelta(minutes=2)):
        wait_time = 2 - int((datetime.utcnow() - user.setup_token_created_at).total_seconds() // 60)
        flash(f"Please wait {wait_time} minute(s) before requesting a new setup email.", "warning")
        return render_template("auth/setup-expired.html")  # stay on expired page

    # Generate new setup token
    setup_token = generate_setup_token()
    user.setup_token_hash = hash_token(setup_token)
    user.setup_token_created_at = datetime.utcnow()
    db.session.commit()

    # Send email
    setup_link = f"{current_app.config['BASE_URL']}/auth/setup?token={setup_token}"
    try:
        msg = Message(
            subject="Your new setup link",
            recipients=[user.email],
            html=f"""
            <p>Hi {user.full_name},</p>
            <p>Click the link below to set your password. The link expires in 2 minutes (for testing).</p>
            <p><a href='{setup_link}'>Set Password</a></p>
            <p>If you didn’t expect this email, ignore it.</p>
            """
        )
        mail.send(msg)
        flash("A new setup email has been sent. Check your inbox.", "success")
    except Exception as e:
        flash("Failed to send email. Try again later.", "danger")
        print(e)

    return render_template("auth/setup-expired.html")  # stay on page so user can try again if needed
