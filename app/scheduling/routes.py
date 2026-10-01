import secrets
from datetime import datetime
from urllib.parse import urlparse

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, abort)
from flask_login import login_required, current_user

from app import db
from app.models import SwapRequest, SwapSession
from app.notifications import create_notification

scheduling_bp = Blueprint('scheduling', __name__,
                           url_prefix='/session',
                           template_folder='templates')

# ── Access guard ───────────────────────────────────────────────────────────────

def _get_swap_or_abort(swap_id):
    """
    Shared access guard for all scheduling routes.

    Returns the SwapRequest if:
      1. It exists
      2. Current user is sender OR receiver
      3. Swap status is 'Accepted' (only active swaps can be scheduled)

    Aborts with 404 / 403 otherwise.
    """
    swap = db.session.get(SwapRequest, swap_id)
    if not swap:
        abort(404)

    is_participant = (current_user.id == swap.sender_id or
                      current_user.id == swap.receiver_id)
    if not is_participant:
        abort(403)

    if swap.status != 'Accepted':
        flash('Session scheduling is only available for Accepted swaps.', 'warning')
        return redirect(url_for('swap.swap_requests'))

    return swap


def _active_session(swap_id):
    """
    Return the current active (Proposed or Confirmed) session for a swap,
    or None if there isn't one.
    """
    return SwapSession.query.filter(
        SwapSession.swap_request_id == swap_id,
        SwapSession.status.in_(['Proposed', 'Confirmed'])
    ).order_by(SwapSession.created_at.desc()).first()


def _fmt_time(dt):
    """Format a UTC datetime as a short readable string for notifications."""
    if not dt:
        return ''
    return dt.strftime('%a %d %b at %I:%M %p UTC')


# ── Routes ─────────────────────────────────────────────────────────────────────

@scheduling_bp.route('/<int:swap_id>')
@login_required
def view_session(swap_id):
    """
    Main scheduling page.
    Shows either:
      - The 'Propose a time' form  (no active session)
      - The current session card   (Proposed / Confirmed / Declined / Cancelled)
    """
    result = _get_swap_or_abort(swap_id)
    # If _get_swap_or_abort returned a redirect, pass it through
    if not isinstance(result, SwapRequest):
        return result
    swap = result

    session = _active_session(swap_id)

    # Also grab the most recent declined/cancelled session for context
    last_session = None
    if not session:
        last_session = SwapSession.query.filter_by(
            swap_request_id=swap_id
        ).order_by(SwapSession.created_at.desc()).first()

    other = swap.receiver if current_user.id == swap.sender_id else swap.sender

    return render_template(
        'scheduling/session.html',
        swap=swap,
        session=session,
        last_session=last_session,
        other=other,
        is_proposer=(session and session.proposed_by_id == current_user.id),
    )


@scheduling_bp.route('/generate-link')
@login_required
def generate_link():
    """
    JSON endpoint called by the 'Generate Jitsi link' button in the form.
    Returns { link: 'https://meet.jit.si/SkillSwap-<random>' }
    Uses Python's built-in secrets module — no new dependencies.
    """
    token = secrets.token_urlsafe(9)   # 9 random bytes → 12 URL-safe chars
    link  = f'https://meet.jit.si/SkillSwap-{token}'
    return jsonify({'link': link})


@scheduling_bp.route('/<int:swap_id>/propose', methods=['POST'])
@login_required
def propose(swap_id):
    """
    Submit the 'Propose a time' form.

    Validates:
      - No active session already exists
      - start_time is provided and in the future
      - meeting_link (if given) starts with http:// or https://
      - duration is a positive integer
    """
    result = _get_swap_or_abort(swap_id)
    if not isinstance(result, SwapRequest):
        return result
    swap = result

    # Block if an active session already exists
    if _active_session(swap_id):
        flash('A session is already Proposed or Confirmed. Cancel it first to propose a new time.', 'warning')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    # ── Read and validate form fields ─────────────────────────────────────────
    start_str  = request.form.get('start_time', '').strip()
    duration   = request.form.get('duration_minutes', '60').strip()
    link       = request.form.get('meeting_link', '').strip()
    notes      = request.form.get('notes', '').strip()[:500]

    if not start_str:
        flash('Please select a date and time.', 'danger')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    try:
        # datetime-local input gives "YYYY-MM-DDTHH:MM" — treat as UTC
        start_dt = datetime.fromisoformat(start_str)
    except ValueError:
        flash('Invalid date/time format.', 'danger')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    if start_dt < datetime.utcnow():
        flash('Session time must be in the future.', 'danger')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    try:
        duration_int = int(duration)
        if duration_int < 15 or duration_int > 480:
            raise ValueError
    except ValueError:
        flash('Duration must be between 15 and 480 minutes.', 'danger')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    # Validate meeting link if provided
    if link:
        parsed = urlparse(link)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            flash('Meeting link must start with http:// or https://', 'danger')
            return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    # ── Save session ──────────────────────────────────────────────────────────
    session = SwapSession(
        swap_request_id  = swap_id,
        proposed_by_id   = current_user.id,
        start_time       = start_dt,
        duration_minutes = duration_int,
        meeting_link     = link or None,
        notes            = notes or None,
        status           = 'Proposed',
    )
    db.session.add(session)
    db.session.commit()

    # Notify the other participant
    other_id = swap.receiver_id if current_user.id == swap.sender_id else swap.sender_id
    create_notification(
        user_id    = other_id,
        notif_type = 'session_proposed',
        message    = f'{current_user.name} proposed a session for {_fmt_time(start_dt)}',
        link       = f'/session/{swap_id}',
        ref_id     = session.id,
    )

    flash('Session proposed! Waiting for the other person to confirm.', 'success')
    return redirect(url_for('scheduling.view_session', swap_id=swap_id))


@scheduling_bp.route('/<int:swap_id>/confirm', methods=['POST'])
@login_required
def confirm(swap_id):
    """Only the NON-proposer can confirm."""
    result = _get_swap_or_abort(swap_id)
    if not isinstance(result, SwapRequest):
        return result
    swap = result

    session = _active_session(swap_id)
    if not session or session.status != 'Proposed':
        flash('No pending session to confirm.', 'warning')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    if session.proposed_by_id == current_user.id:
        flash('You cannot confirm your own proposal — wait for the other person.', 'warning')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    session.status = 'Confirmed'
    db.session.commit()

    # Notify the proposer
    create_notification(
        user_id    = session.proposed_by_id,
        notif_type = 'session_confirmed',
        message    = f'{current_user.name} confirmed your session for {_fmt_time(session.start_time)}',
        link       = f'/session/{swap_id}',
        ref_id     = session.id,
    )

    flash('Session confirmed! ✅ You can now join the meeting at the scheduled time.', 'success')
    return redirect(url_for('scheduling.view_session', swap_id=swap_id))


@scheduling_bp.route('/<int:swap_id>/decline', methods=['POST'])
@login_required
def decline(swap_id):
    """Only the NON-proposer can decline."""
    result = _get_swap_or_abort(swap_id)
    if not isinstance(result, SwapRequest):
        return result
    swap = result

    session = _active_session(swap_id)
    if not session or session.status != 'Proposed':
        flash('No pending session to decline.', 'warning')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    if session.proposed_by_id == current_user.id:
        flash('You cannot decline your own proposal — use Cancel instead.', 'warning')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    session.status = 'Declined'
    db.session.commit()

    # Notify the proposer
    create_notification(
        user_id    = session.proposed_by_id,
        notif_type = 'session_declined',
        message    = f'{current_user.name} declined your proposed session. You can propose a new time.',
        link       = f'/session/{swap_id}',
        ref_id     = session.id,
    )

    flash('Session declined. The other person can propose a new time.', 'info')
    return redirect(url_for('scheduling.view_session', swap_id=swap_id))


@scheduling_bp.route('/<int:swap_id>/cancel', methods=['POST'])
@login_required
def cancel(swap_id):
    """Either participant can cancel a Proposed or Confirmed session."""
    result = _get_swap_or_abort(swap_id)
    if not isinstance(result, SwapRequest):
        return result
    swap = result

    session = _active_session(swap_id)
    if not session:
        flash('No active session to cancel.', 'warning')
        return redirect(url_for('scheduling.view_session', swap_id=swap_id))

    session.status = 'Cancelled'
    db.session.commit()

    # Notify the other participant
    other_id = swap.receiver_id if current_user.id == swap.sender_id else swap.sender_id
    create_notification(
        user_id    = other_id,
        notif_type = 'session_cancelled',
        message    = f'{current_user.name} cancelled the session for {_fmt_time(session.start_time)}',
        link       = f'/session/{swap_id}',
        ref_id     = session.id,
    )

    flash('Session cancelled. Either person can now propose a new time.', 'info')
    return redirect(url_for('scheduling.view_session', swap_id=swap_id))
