from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError


class UserForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )

    full_name = StringField(
        'Full Name',
        validators=[DataRequired()]
    )

    email = EmailField(
        'Email',
        validators=[DataRequired()]
    )

    role_id = SelectField(
        'Role',
        choices=[],              # filled dynamically in routes
        coerce=int,
        validators=[DataRequired()]
    )

    is_active = BooleanField('Active')

    submit = SubmitField('Save')

    # =========================
    # Custom Validation
    # =========================
    def validate_full_name(self, field):
        if any(char.isdigit() for char in field.data):
            raise ValidationError("Full name must not contain numbers")
