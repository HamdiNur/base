from flask import Blueprint

projects_bp = Blueprint(
    "projects",
    __name__,
    url_prefix="/projects",
    template_folder="../templates/projects"
)
from .models import Project

from . import routes
from .members import ProjectMember
