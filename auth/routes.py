from flask import render_template, redirect, url_for, flash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from . import auth_bp
from auth.forms import LoginForm, SetPasswordForm
from users.models import User


# =====================
# LOGIN
# =====================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # ❌ User not found
        if not user:
            flash("Invalid username or credentials", "danger")
            return render_template("auth/login.html", form=form)

        # ❌ Inactive account
        if not user.is_active:
            flash("Your account is inactive. Contact admin.", "warning")
            return render_template("auth/login.html", form=form)

        # 🔐 FIRST LOGIN (SETUP TOKEN)
        if user.must_set_password:
            if not user.setup_token_hash or not check_password_hash(
                user.setup_token_hash,
                form.password.data
            ):
                flash("Invalid setup token", "danger")
                return render_template("auth/login.html", form=form)

            login_user(user)
            return redirect(url_for("auth.set_password"))

        # 🔐 NORMAL LOGIN (PASSWORD)
        if not user.password_hash or not check_password_hash(
            user.password_hash,
            form.password.data
        ):
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
@login_required
def set_password():
    # 🔒 Only allowed if user must set password
    if not current_user.must_set_password:
        return redirect(url_for("home"))

    form = SetPasswordForm()

    if form.validate_on_submit():
        current_user.password_hash = generate_password_hash(
            form.password.data
        )
        current_user.setup_token_hash = None
        current_user.must_set_password = False

        db.session.commit()

        flash("Password set successfully. Please log in.", "success")
        logout_user()
        return redirect(url_for("auth.login"))

    return render_template("auth/set_password.html", form=form)
