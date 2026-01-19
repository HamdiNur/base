from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class PermissionForm(FlaskForm):
    code = StringField(
        "Permission Code",
        validators=[DataRequired(), Length(max=100)]
    )

    label = StringField(
        "Label",
        validators=[DataRequired(), Length(max=150)]
    )

    description = StringField(
        "Description",
        validators=[Length(max=255)]
    )

    is_active = BooleanField("Active", default=True)

    submit = SubmitField("Save")
