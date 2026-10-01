"""
notifications.py — reusable helper for creating in-app notifications.

How to call it:
    from app.notifications import create_notification

    create_notification(
        user_id = receiver.id,
        notif_type = 'swap_received',
        message = f'{sender.name} sent you a swap request',
        link = '/swap/requests',
        ref_id = swap_request.id   # optional, enables collapse
    )

Collapse behaviour (simple explanation):
    If a notification already exists with the SAME (user_id + notif_type + ref_id)
    and it is still UNREAD, we UPDATE that row instead of inserting a new one.
    This avoids flooding the user's notification list with duplicates.

    Example:
        Call 1  → no existing row → INSERT  (count=1, message="John sent you a request")
        Call 2  → unread row found → UPDATE (count=2, message updated, created_at refreshed)

    If ref_id is None, collapse is skipped — a new row is always inserted.
    This is safe for future event types (messaging, scheduling) that may not have a ref_id.
"""

from app import db
from app.models import Notification
from sqlalchemy import func


def create_notification(user_id, notif_type, message, link, ref_id=None):
    """
    Create or collapse a notification for a user.

    Parameters
    ----------
    user_id    : int   — the user who should receive this notification
    notif_type : str   — event type code, e.g. 'swap_received', 'swap_accepted'
    message    : str   — human-readable text shown in the bell dropdown / list
    link       : str   — where to redirect when the user clicks the notification
    ref_id     : int   — optional id of the related object (e.g. swap_request.id)
                         used to detect and collapse duplicates
    """

    # ── Step 1: Try to find an existing UNREAD duplicate ──────────────────────
    existing = None
    if ref_id is not None:
        # Only collapse if we have a ref_id to match on.
        # We look for a row that:
        #   • belongs to the same user
        #   • is the same event type
        #   • refers to the same object (same ref_id)
        #   • has NOT been read yet  ← already-read notifications are left alone
        existing = Notification.query.filter_by(
            user_id=user_id,
            type=notif_type,
            ref_id=ref_id,
            is_read=False,
        ).first()

    # ── Step 2a: Duplicate found → collapse (update in place) ─────────────────
    if existing:
        existing.message    = message          # refresh text (names may change)
        existing.count      = existing.count + 1
        existing.created_at = func.now()       # bubble it to top of the list
        db.session.commit()
        return existing

    # ── Step 2b: No duplicate → create a brand-new row ────────────────────────
    notif = Notification(
        user_id    = user_id,
        type       = notif_type,
        message    = message,
        link       = link,
        is_read    = False,
        ref_id     = ref_id,
        count      = 1,
    )
    db.session.add(notif)
    db.session.commit()
    return notif
