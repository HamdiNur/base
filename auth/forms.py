from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


# =====================
# LOGIN FORM
# =====================
class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required"),
            Length(max=100)
        ]
    )

    password = PasswordField(
        "Password / Setup Token",
        validators=[
            DataRequired(message="Password or setup token is required")
        ]
    )

    submit = SubmitField("Login")


# =====================
# SET PASSWORD FORM (FIRST LOGIN)
# =====================
class SetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters")
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match")
        ]
    )

    submit = SubmitField("Set Password")
