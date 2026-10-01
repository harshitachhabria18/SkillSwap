from app import db
from flask_login import UserMixin

# db.Model is the base class and User is the name of the child class (here User table)
class User(db.Model, UserMixin):
    # all the below are the fields or columns for the User table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(200))
    profile_photo = db.Column(db.String(255)) # storage of file name
    availability = db.Column(db.String(100))
    session_duration = db.Column(db.String(50))
    profile_visibility = db.Column(db.String(50))

    # this line user_skills
    # user = User.query.get(1)
    # skills = user.user_skills.all()  # returns all skills offered/wanted by user 1
    user_skills = db.relationship('UserSkills', backref='user', lazy='dynamic')

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    skill_users = db.relationship('UserSkills', backref='skill', lazy='dynamic')


class UserSkills(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    skills_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False, index=True)
    skill_type = db.Column(db.String(20),nullable=False) # offered and wanted 

class SwapRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    offered_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    wanted_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending', index=True)  # Pending, Accepted, Rejected
    timestamp = db.Column(db.DateTime, default=db.func.now())

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')
    offered_skill = db.relationship('Skills', foreign_keys=[offered_skill_id])
    wanted_skill = db.relationship('Skills', foreign_keys=[wanted_skill_id])


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    swap_request_id = db.Column(db.Integer, db.ForeignKey('swap_request.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviews_given')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref='reviews_received')
    swap_request = db.relationship('SwapRequest', backref='feedbacks')


class Notification(db.Model):
    """
    One row = one notification for one user.

    - type     : short code for the event, e.g. 'swap_received', 'swap_accepted'
    - ref_id   : the related object's id (e.g. swap_request.id) used for collapsing
    - count    : how many times this notification was collapsed (starts at 1)
    - is_read  : False until the user clicks it or hits "mark all read"
    - created_at: refreshed whenever the notification is collapsed/updated

    Composite index on (user_id, is_read) keeps the unread-count query fast.
    """
    __tablename__ = 'notification'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type       = db.Column(db.String(50), nullable=False)
    message    = db.Column(db.String(300), nullable=False)
    link       = db.Column(db.String(200), nullable=False, default='/notifications/')
    is_read    = db.Column(db.Boolean, default=False, nullable=False)
    ref_id     = db.Column(db.Integer, nullable=True)   # e.g. swap_request_id
    count      = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User', backref='notifications')

    # Composite index — fast lookup for the unread-count badge and collapse check
    __table_args__ = (
        db.Index('ix_notification_user_is_read', 'user_id', 'is_read'),
    )