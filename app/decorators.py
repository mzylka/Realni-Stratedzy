from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


#  f = permission_required(permission)(f)


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def content_editor_required(f):
    return permission_required(Permission.CONTENT_EDITOR)(f)


def poster_required(f):
    return permission_required(Permission.POSTER)(f)
