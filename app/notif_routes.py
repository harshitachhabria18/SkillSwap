from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Notification

notif_bp = Blueprint('notif', __name__, url_prefix='/notifications',
                     template_folder='templates')


@notif_bp.route('/')
@login_required
def list_notifications():
    """Show all notifications for the logged-in user, newest first, paginated."""
    page = __import__('flask').request.args.get('page', 1, type=int)

    pagination = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )

    return render_template(
        'notifications/list.html',
        notifications=pagination.items,
        pagination=pagination,
    )


@notif_bp.route('/<int:notif_id>/read', methods=['GET', 'POST'])
@login_required
def mark_read(notif_id):
    """
    Mark one notification as read.
    Only the owner of the notification can mark it — anyone else gets a 403.
    After marking, redirect to the notification's link (e.g. /swap/requests).
    """
    notif = db.session.get(Notification, notif_id)

    # Safety check — users can only touch their OWN notifications
    if not notif or notif.user_id != current_user.id:
        flash('Notification not found.', 'danger')
        return redirect(url_for('notif.list_notifications'))

    notif.is_read = True
    db.session.commit()

    # Redirect to the relevant page (e.g. swap requests) instead of staying on the list
    return redirect(notif.link or url_for('notif.list_notifications'))


@notif_bp.route('/read-all', methods=['POST'])
@login_required
def mark_all_read():
    """Mark every unread notification for the current user as read in one query."""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notif.list_notifications'))
