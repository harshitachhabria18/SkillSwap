from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.models import User, UserSkills, Skills, SwapRequest, Feedback
from sqlalchemy import or_

swap_bp = Blueprint('swap', __name__, url_prefix='/swap', template_folder='templates')

@swap_bp.route('/')
def home():
    availability = request.args.get('availability', '').strip()
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)

    users_query = User.query.filter_by(profile_visibility='Public')

    if availability:
        users_query = users_query.filter(User.availability.ilike(availability))

    if search:
        skill_user_ids = db.session.query(UserSkills.user_id)\
                            .join(Skills, Skills.id == UserSkills.skills_id)\
                            .filter(Skills.name.ilike(f'%{search}%'))\
                            .subquery()

        users_query = users_query.filter(
            or_(
                User.name.ilike(f'%{search}%'),
                User.id.in_(skill_user_ids)
            )
        )

    pagination = users_query.paginate(page=page, per_page=4, error_out=False)

    user_data = []
    for user in pagination.items:
        offered = UserSkills.query.filter_by(user_id=user.id, skill_type='offered').all()
        wanted = UserSkills.query.filter_by(user_id=user.id, skill_type='wanted').all()

        # Calculate BEFORE append
        feedbacks = Feedback.query.filter_by(reviewee_id=user.id).all()
        avg_rating = None
        if feedbacks:
            avg_rating = round(sum(f.rating for f in feedbacks) / len(feedbacks), 1)

        user_data.append({
            'user': user,
            'skills_offered': [us.skill.name for us in offered],
            'skills_wanted': [us.skill.name for us in wanted],
            'avg_rating': avg_rating,
            'review_count': len(feedbacks)
        })



    return render_template(
        'swap/browse.html',
        user_data=user_data,
        pagination=pagination,
        current_user=current_user,
        selected_availability=availability,
        search=search
    )


@swap_bp.route('/user/<int:user_id>')
def view_profile(user_id):
    user = User.query.get_or_404(user_id)

    if user.profile_visibility != 'Public':
        return render_template('swap/private_profile.html'), 403

    offered = UserSkills.query.filter_by(user_id=user.id, skill_type='offered').all()
    wanted = UserSkills.query.filter_by(user_id=user.id, skill_type='wanted').all()

    # Fetch real feedbacks
    feedbacks = Feedback.query.filter_by(reviewee_id=user.id)\
                              .order_by(Feedback.timestamp.desc()).all()
    
    avg_rating = None
    if feedbacks:
        avg_rating = round(sum(f.rating for f in feedbacks) / len(feedbacks), 1)


    return render_template(
        'swap/view_profile.html',
        profile_user=user,
        skills_offered=[us.skill.name for us in offered],
        skills_wanted=[us.skill.name for us in wanted],
        feedbacks=feedbacks,
        avg_rating=avg_rating,
        current_user=current_user
    )

@swap_bp.route('/request/<int:user_id>', methods=['GET', 'POST'])
@login_required
def request_swap(user_id):
    receiver = User.query.get_or_404(user_id)

    # Prevent requesting yourself
    if receiver.id == current_user.id:
        flash('You cannot send a swap request to yourself.', 'warning')
        return redirect(url_for('swap.home'))

    # Get current user's offered skills (what they can offer)
    my_offered = UserSkills.query.filter_by(
        user_id=current_user.id, skill_type='offered'
    ).all()

    # Get receiver's wanted skills (what they want to learn)
    their_wanted = UserSkills.query.filter_by(
        user_id=receiver.id, skill_type='wanted'
    ).all()

    if request.method == 'POST':
        offered_skill_id = request.form.get('offered_skill_id')
        wanted_skill_id = request.form.get('wanted_skill_id')
        message = request.form.get('message', '').strip()

        if not offered_skill_id or not wanted_skill_id:
            flash('Please select both skills.', 'danger')
            return redirect(url_for('swap.request_swap', user_id=user_id))

        # Check if request already exists
        existing = SwapRequest.query.filter_by(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            status='Pending'
        ).first()

        if existing:
            flash('You already have a pending request with this user.', 'warning')
            return redirect(url_for('swap.view_profile', user_id=user_id))

        swap_req = SwapRequest(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            offered_skill_id=int(offered_skill_id),
            wanted_skill_id=int(wanted_skill_id),
            message=message,
            status='Pending'
        )
        db.session.add(swap_req)
        db.session.commit()

        flash('Swap request sent successfully!', 'success')
        return redirect(url_for('swap.view_profile', user_id=user_id))

    return render_template(
        'swap/request_swap.html',
        receiver=receiver,
        my_offered=my_offered,
        their_wanted=their_wanted
    )

@swap_bp.route('/requests', methods=['GET'])
@login_required
def swap_requests():
    status_filter = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    # Received requests (others sent to you)
    received_query = SwapRequest.query.filter_by(receiver_id=current_user.id)
    if status_filter:
        received_query = received_query.filter_by(status=status_filter)
    received_pagination = received_query.order_by(SwapRequest.timestamp.desc())\
                                        .paginate(page=page, per_page=4, error_out=False)

    # Sent requests (you sent to others)
    sent_query = SwapRequest.query.filter_by(sender_id=current_user.id)
    if status_filter:
        sent_query = sent_query.filter_by(status=status_filter)
    sent_pagination = sent_query.order_by(SwapRequest.timestamp.desc())\
                                .paginate(page=page, per_page=4, error_out=False)

    return render_template(
        'swap/swap_requests.html',
        received=received_pagination.items,
        sent=sent_pagination.items,
        received_pagination=received_pagination,
        sent_pagination=sent_pagination,
        selected_status=status_filter
    )


@swap_bp.route('/request/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    swap_req = SwapRequest.query.get_or_404(request_id)
    if swap_req.receiver_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('swap.swap_requests'))
    swap_req.status = 'Accepted'
    db.session.commit()
    flash('Request accepted!', 'success')
    return redirect(url_for('swap.swap_requests'))


@swap_bp.route('/request/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_request(request_id):
    swap_req = SwapRequest.query.get_or_404(request_id)
    if swap_req.receiver_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('swap.swap_requests'))
    swap_req.status = 'Rejected'
    db.session.commit()
    flash('Request rejected.', 'info')
    return redirect(url_for('swap.swap_requests'))


@swap_bp.route('/request/<int:request_id>/complete', methods=['POST'])
@login_required
def complete_request(request_id):
    swap_req = SwapRequest.query.get_or_404(request_id)
    if swap_req.receiver_id != current_user.id and swap_req.sender_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('swap.swap_requests'))
    swap_req.status = 'Completed'
    db.session.commit()
    flash('Swap marked as completed!', 'success')
    return redirect(url_for('swap.swap_requests'))


@swap_bp.route('/request/<int:request_id>/feedback', methods=['GET', 'POST'])
@login_required
def leave_feedback(request_id):
    swap_req = SwapRequest.query.get_or_404(request_id)

    # Only sender or receiver can leave feedback
    if current_user.id not in [swap_req.sender_id, swap_req.receiver_id]:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('swap.swap_requests'))

    # Only allow feedback if swap is Completed
    if swap_req.status != 'Completed':
        flash('You can only leave feedback after swap is completed.', 'warning')
        return redirect(url_for('swap.swap_requests'))

    # Check if current user already left feedback for this swap
    existing = Feedback.query.filter_by(
        swap_request_id=request_id,
        reviewer_id=current_user.id
    ).first()

    if existing:
        flash('You have already left feedback for this swap.', 'warning')
        return redirect(url_for('swap.swap_requests'))

    # The person being reviewed is the other person in the swap
    if current_user.id == swap_req.sender_id:
        reviewee = swap_req.receiver
    else:
        reviewee = swap_req.sender

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()

        if not rating:
            flash('Please select a rating.', 'danger')
            return redirect(url_for('swap.leave_feedback', request_id=request_id))

        feedback = Feedback(
            swap_request_id=request_id,
            reviewer_id=current_user.id,
            reviewee_id=reviewee.id,
            rating=int(rating),
            comment=comment
        )
        db.session.add(feedback)
        db.session.commit()

        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('swap.swap_requests'))

    return render_template(
        'swap/leave_feedback.html',
        swap_req=swap_req,
        reviewee=reviewee
    )