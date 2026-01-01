from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class RoleForm(FlaskForm):
    name = StringField(
        'Role Name',
        validators=[DataRequired(), Length(max=100)]
    )

    code = StringField(
        'Code',
        validators=[DataRequired(), Length(max=50)]
    )

    description = TextAreaField(
        'Description'
    )

    is_active = BooleanField(
        'Active',
        default=True
    )

    submit = SubmitField('Save')
