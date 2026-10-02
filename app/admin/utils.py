from functools import wraps
from flask import abort
from flask_login import login_required, current_user


def admin_required(f):
    """
    Decorator for admin-only routes.

    - Must be logged in (via @login_required).
    - Must have is_admin = True.
    - Returns 404 (not 403) so the panel is invisible to non-admins.

    Usage:
        @admin_bp.route('/something')
        @admin_required
        def something():
            ...
    """
    @login_required
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(404)
        return f(*args, **kwargs)
    return decorated
