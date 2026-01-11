from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class ProjectForm(FlaskForm):
    name = StringField(
        "Project Name",
        validators=[
            DataRequired(message="Project name is required"),
            Length(max=150, message="Project name must be under 150 characters")
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            Length(max=1000, message="Description is too long")
        ]
    )

    is_active = BooleanField(
        "Active",
        default=True
    )

    submit = SubmitField("Save")
