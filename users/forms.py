from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')
    role_id = SelectField(
    'Role',
    choices=[],
    coerce=int
)
