from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    user_type = StringField('User Type', validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')
