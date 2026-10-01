from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, abort)
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app import db
from app.models import SwapRequest, Message, Notification
from app.notifications import create_notification

messaging_bp = Blueprint('messaging', __name__,
                         url_prefix='/chat',
                         template_folder='templates')

# ── Access guard ───────────────────────────────────────────────────────────────

def _get_chat_or_abort(swap_id):
    """
    Shared access guard used by all three routes.

    Returns the SwapRequest object if the current user is allowed in.
    Aborts with 404 or 403 otherwise.

    Rules:
      1. Swap must exist.
      2. Current user must be the sender OR receiver of that swap.
      3. Swap status must be Accepted or Completed
         (Pending / Rejected swaps have no chat yet).
    """
    swap = db.session.get(SwapRequest, swap_id)
    if not swap:
        abort(404)

    # Rule 2 — only the two people in this swap can access the chat
    is_participant = (current_user.id == swap.sender_id or
                      current_user.id == swap.receiver_id)
    if not is_participant:
        abort(403)

    # Rule 3 — chat only available for active / completed swaps
    if swap.status not in ('Accepted', 'Completed'):
        flash('Chat is only available for Accepted or Completed swaps.', 'warning')
        abort(403)

    return swap


# ── Routes ─────────────────────────────────────────────────────────────────────

@messaging_bp.route('/<int:swap_id>')
@login_required
def chat(swap_id):
    """
    Main chat page.
    - Loads all messages for this swap in chronological order.
    - Marks every unread message (sent by the OTHER person) as read.
    - Clears the 'new_message' notification for this conversation.
    """
    swap = _get_chat_or_abort(swap_id)

    # Load all messages newest-last (chronological)
    messages = (Message.query
                .filter_by(swap_request_id=swap_id)
                .order_by(Message.created_at.asc())
                .all())

    # Mark unread messages from the OTHER person as read
    (Message.query
     .filter_by(swap_request_id=swap_id, is_read=False)
     .filter(Message.sender_id != current_user.id)
     .update({'is_read': True}))

    # Clear the 'new_message' notification for this conversation
    (Notification.query
     .filter_by(user_id=current_user.id,
                type='new_message',
                ref_id=swap_id,
                is_read=False)
     .update({'is_read': True}))

    db.session.commit()

    # Work out who the other person is for the page title
    other = swap.receiver if current_user.id == swap.sender_id else swap.sender

    return render_template(
        'messaging/chat.html',
        swap=swap,
        messages=messages,
        other=other,
    )


@messaging_bp.route('/<int:swap_id>/send', methods=['POST'])
@login_required
def send_message(swap_id):
    """
    Handle the message send form (standard POST, no AJAX).
    - Validates body length (1–1000 chars).
    - Saves the message.
    - Creates/collapses a notification for the recipient.
    - Redirects back to the chat page.
    """
    swap = _get_chat_or_abort(swap_id)

    body = request.form.get('body', '').strip()

    # Server-side length validation (client also enforces via maxlength)
    if not body:
        flash('Message cannot be empty.', 'warning')
        return redirect(url_for('messaging.chat', swap_id=swap_id))

    if len(body) > 1000:
        flash('Message too long — maximum 1000 characters.', 'warning')
        return redirect(url_for('messaging.chat', swap_id=swap_id))

    # Store body as-is — Jinja2 auto-escapes {{ msg.body }} on render,
    # and JS uses textContent (not innerHTML) so no XSS risk either.
    # (Previously used markupsafe.escape() here which caused double-escaping:
    #  what's → what&#39;s stored in DB → shown literally as what&#39;s in the chat)
    msg = Message(
        swap_request_id=swap_id,
        sender_id=current_user.id,
        body=body,
        is_read=False,
    )
    db.session.add(msg)
    db.session.commit()

    # Notify the OTHER participant via the collapsing helper.
    # All messages in the same chat share ref_id=swap_id + type='new_message',
    # so they collapse into ONE notification row with an incrementing count.
    recipient_id = (swap.receiver_id
                    if current_user.id == swap.sender_id
                    else swap.sender_id)

    # Count total unread messages from current user to recipient in this chat
    unread_count = Message.query.filter_by(
        swap_request_id=swap_id,
        is_read=False,
    ).filter(Message.sender_id != recipient_id).count()

    count_label = f'{unread_count} new message{"s" if unread_count != 1 else ""}'
    create_notification(
        user_id    = recipient_id,
        notif_type = 'new_message',
        message    = f'{count_label} from {current_user.name}',
        link       = f'/chat/{swap_id}',
        ref_id     = swap_id,
    )

    return redirect(url_for('messaging.chat', swap_id=swap_id))


@messaging_bp.route('/<int:swap_id>/poll')
@login_required
def poll(swap_id):
    """
    JSON polling endpoint — called by JS every 4 seconds.

    Query param: ?since=<ISO-8601 UTC timestamp>
    Returns: { messages: [ { id, sender_id, sender_name, body, created_at, is_mine }, ... ] }

    Also marks returned messages as read so the unread badge stays accurate.
    """
    swap = _get_chat_or_abort(swap_id)

    since_str = request.args.get('since', '')
    try:
        # Parse the ISO timestamp the JS sends back each time
        since_dt = datetime.fromisoformat(since_str)
    except (ValueError, TypeError):
        since_dt = datetime.min

    new_msgs = (Message.query
                .filter_by(swap_request_id=swap_id)
                .filter(Message.created_at > since_dt)
                .filter(Message.sender_id != current_user.id)
                .order_by(Message.created_at.asc())
                .all())

    # Mark them read since the user is actively looking at the chat
    if new_msgs:
        ids = [m.id for m in new_msgs]
        Message.query.filter(Message.id.in_(ids)).update({'is_read': True})
        # Also clear the notification for this chat
        Notification.query.filter_by(
            user_id=current_user.id,
            type='new_message',
            ref_id=swap_id,
            is_read=False,
        ).update({'is_read': True})
        db.session.commit()

    return jsonify({
        'messages': [
            {
                'id':          m.id,
                'sender_id':   m.sender_id,
                'sender_name': m.sender.name,
                'body':        m.body,          # already escaped on save
                'created_at':  m.created_at.isoformat() if m.created_at else '',
                'is_mine':     False,           # poll only returns OTHER person's messages
            }
            for m in new_msgs
        ]
    })
