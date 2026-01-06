from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, BooleanField, SubmitField, SelectField
from wtforms.validators import InputRequired, ValidationError


class UserForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[InputRequired()]
    )

    full_name = StringField(
        "Full Name",
        validators=[InputRequired()]
    )

    email = EmailField(
        "Email",
        validators=[InputRequired()]
    )

    # IMPORTANT: InputRequired (NOT DataRequired)
    role_id = SelectField(
        "Role",
        coerce=int,
        validators=[InputRequired()]
    )

    is_active = BooleanField("Active", default=True)

    submit = SubmitField("Save")

    # =====================
    # CUSTOM VALIDATION
    # =====================
    def validate_full_name(self, field):
        if any(char.isdigit() for char in field.data):
            raise ValidationError("Full name must not contain numbers")
