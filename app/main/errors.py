from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('505.html'), 500
