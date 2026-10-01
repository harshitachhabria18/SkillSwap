from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, current_app, abort)
from flask_login import current_user
from app import db
from app.models import User, Skills, UserSkills, SwapRequest, Feedback
from app.admin.utils import admin_required

admin_bp = Blueprint('admin', __name__,
                     url_prefix='/admin',
                     template_folder='templates')

# ── Dashboard ──────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_required
def dashboard():
    """Show site-wide counts at a glance."""
    stats = {
        'total_users':     User.query.count(),
        'active_users':    User.query.filter_by(is_active_account=True).count(),
        'banned_users':    User.query.filter_by(is_active_account=False).count(),
        'total_swaps':     SwapRequest.query.count(),
        'pending_swaps':   SwapRequest.query.filter_by(status='Pending').count(),
        'accepted_swaps':  SwapRequest.query.filter_by(status='Accepted').count(),
        'completed_swaps': SwapRequest.query.filter_by(status='Completed').count(),
        'rejected_swaps':  SwapRequest.query.filter_by(status='Rejected').count(),
        'total_skills':    Skills.query.count(),
        'total_feedback':  Feedback.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)


# ── Users ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/users')
@admin_required
def users():
    """List all users with search and pagination."""
    q    = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = User.query
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(User.name.ilike(like), User.email.ilike(like))
        )

    pagination = query.order_by(User.id.asc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/users.html',
                           users=pagination.items,
                           pagination=pagination,
                           q=q)


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@admin_required
def ban_user(user_id):
    """Ban a user — sets is_active_account=False. Kicks them out immediately."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    if user.id == current_user.id:
        flash('You cannot ban yourself.', 'danger')
        return redirect(url_for('admin.users'))

    if user.is_admin:
        flash('You cannot ban another admin.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_active_account = False
    db.session.commit()
    current_app.logger.info(
        f'[ADMIN] {current_user.email} banned user id={user_id} ({user.email})'
    )
    flash(f'User "{user.name}" has been banned.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@admin_required
def unban_user(user_id):
    """Unban a user — sets is_active_account=True."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    user.is_active_account = True
    db.session.commit()
    current_app.logger.info(
        f'[ADMIN] {current_user.email} unbanned user id={user_id} ({user.email})'
    )
    flash(f'User "{user.name}" has been unbanned.', 'success')
    return redirect(url_for('admin.users'))


# ── Skills ─────────────────────────────────────────────────────────────────────

@admin_bp.route('/skills')
@admin_required
def skills():
    """List all skills with usage counts."""
    all_skills = Skills.query.order_by(Skills.name.asc()).all()

    # Count how many user_skills rows reference each skill
    from sqlalchemy import func
    usage_counts = dict(
        db.session.query(UserSkills.skills_id, func.count(UserSkills.id))
        .group_by(UserSkills.skills_id)
        .all()
    )
    # Count how many swap_requests reference each skill
    swap_offered = dict(
        db.session.query(SwapRequest.offered_skill_id, func.count(SwapRequest.id))
        .group_by(SwapRequest.offered_skill_id)
        .all()
    )
    swap_wanted = dict(
        db.session.query(SwapRequest.wanted_skill_id, func.count(SwapRequest.id))
        .group_by(SwapRequest.wanted_skill_id)
        .all()
    )

    return render_template('admin/skills.html',
                           skills=all_skills,
                           usage_counts=usage_counts,
                           swap_offered=swap_offered,
                           swap_wanted=swap_wanted)


@admin_bp.route('/skills/add', methods=['POST'])
@admin_required
def add_skill():
    """Add a new skill."""
    name = request.form.get('name', '').strip()
    if not name:
        flash('Skill name cannot be empty.', 'danger')
        return redirect(url_for('admin.skills'))

    if Skills.query.filter(Skills.name.ilike(name)).first():
        flash(f'Skill "{name}" already exists.', 'warning')
        return redirect(url_for('admin.skills'))

    skill = Skills(name=name)
    db.session.add(skill)
    db.session.commit()
    current_app.logger.info(f'[ADMIN] {current_user.email} added skill "{name}" id={skill.id}')
    flash(f'Skill "{name}" added.', 'success')
    return redirect(url_for('admin.skills'))


@admin_bp.route('/skills/<int:skill_id>/rename', methods=['POST'])
@admin_required
def rename_skill(skill_id):
    """Rename an existing skill."""
    skill = db.session.get(Skills, skill_id)
    if not skill:
        abort(404)

    new_name = request.form.get('new_name', '').strip()
    if not new_name:
        flash('New name cannot be empty.', 'danger')
        return redirect(url_for('admin.skills'))

    old_name = skill.name
    skill.name = new_name
    db.session.commit()
    current_app.logger.info(
        f'[ADMIN] {current_user.email} renamed skill id={skill_id} "{old_name}" → "{new_name}"'
    )
    flash(f'Skill renamed to "{new_name}".', 'success')
    return redirect(url_for('admin.skills'))


@admin_bp.route('/skills/<int:skill_id>/delete', methods=['POST'])
@admin_required
def delete_skill(skill_id):
    """
    Delete a skill — blocked if it is referenced in user_skills or swap_request.
    This prevents breaking existing user profiles and swap records.
    """
    skill = db.session.get(Skills, skill_id)
    if not skill:
        abort(404)

    # Check if any user has this skill
    if UserSkills.query.filter_by(skills_id=skill_id).first():
        flash(f'Cannot delete "{skill.name}" — it is used by one or more users.', 'danger')
        return redirect(url_for('admin.skills'))

    # Check if any swap references this skill
    if (SwapRequest.query.filter_by(offered_skill_id=skill_id).first() or
            SwapRequest.query.filter_by(wanted_skill_id=skill_id).first()):
        flash(f'Cannot delete "{skill.name}" — it is referenced in swap requests.', 'danger')
        return redirect(url_for('admin.skills'))

    current_app.logger.info(f'[ADMIN] {current_user.email} deleted skill id={skill_id} "{skill.name}"')
    db.session.delete(skill)
    db.session.commit()
    flash(f'Skill "{skill.name}" deleted.', 'success')
    return redirect(url_for('admin.skills'))


# ── Swap Requests (read-only) ──────────────────────────────────────────────────

@admin_bp.route('/swaps')
@admin_required
def swaps():
    """Read-only swap request list with status filter."""
    status = request.args.get('status', '').strip()
    page   = request.args.get('page', 1, type=int)

    query = SwapRequest.query
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(SwapRequest.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/swaps.html',
                           swaps=pagination.items,
                           pagination=pagination,
                           selected_status=status)


# ── Feedback ───────────────────────────────────────────────────────────────────

@admin_bp.route('/feedback')
@admin_required
def feedback():
    """List all feedback."""
    page = request.args.get('page', 1, type=int)
    pagination = Feedback.query.order_by(Feedback.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/feedback.html',
                           feedbacks=pagination.items,
                           pagination=pagination)


@admin_bp.route('/feedback/<int:fb_id>/delete', methods=['POST'])
@admin_required
def delete_feedback(fb_id):
    """Delete an inappropriate review."""
    fb = db.session.get(Feedback, fb_id)
    if not fb:
        abort(404)

    current_app.logger.info(
        f'[ADMIN] {current_user.email} deleted feedback id={fb_id} '
        f'(reviewer={fb.reviewer_id}, reviewee={fb.reviewee_id})'
    )
    db.session.delete(fb)
    db.session.commit()
    flash('Feedback deleted.', 'success')
    return redirect(url_for('admin.feedback'))
