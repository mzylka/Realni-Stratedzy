from flask import Blueprint
from ..models import Permission

control_panel = Blueprint('control_panel', __name__)

from . import views

from .auth import auth as auth_blueprint
control_panel.register_blueprint(auth_blueprint, url_prefix='/auth')


@control_panel.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
