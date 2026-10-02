from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, current_app, session)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
# import login and register child classes from form.py
from app.forms import RegisterForm, LoginForm
# import User table
from app.models import User
from app import db
from app.auth.oauth import oauth

# creating a blueprint for authentication (login and register)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates/auth')

# route for register page
@auth_bp.route("/register", methods=["GET","POST"])
def register():
    # here form is the object of RegisterForm class from forms.py
    form = RegisterForm()
    # to check if it is a POST request
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash(message='Email already registered.', category='danger')
            # return back to register
            return redirect(url_for('auth.register'))

        # create new user
        # create a hashed password for security
        hashed_password = generate_password_hash(form.password.data)

        # create a new user for the User table and insert the data from the form in the User table
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )

        # add the new user in the database session
        db.session.add(new_user)

        db.session.commit()

        # Auto login after registration
        login_user(new_user)
        flash(message='Welcome to SkillSwap! Complete your profile to get started.', category='success')
        return redirect(url_for('swap.home'))
    
    # return the register.html page
    return render_template('register.html', form=form)

# route for login page
@auth_bp.route("/login", methods=["GET","POST"])
def login():
    # here form is the object of LoginForm class from forms.py
    form = LoginForm()

    # to check if it is a POST request
    if form.validate_on_submit():
        # filtering the email in the database entered by the user
        user = User.query.filter_by(email=form.email.data).first()

        # Check email first
        if not user:
            flash(message='No account found with that email.', category='danger')
            return render_template('login.html', form=form)

        # Then check password
        if not check_password_hash(user.password, form.password.data):
            flash(message='Incorrect password.', category='danger')
            return render_template('login.html', form=form)

        # Check if account is banned
        if not user.is_active_account:
            flash(message='Your account has been suspended. Please contact support.', category='danger')
            return render_template('login.html', form=form)

        # All checks passed — log in and go to Home page
        login_user(user)
        flash(message='Logged in successfully!', category='success')
        return redirect(url_for('swap.home'))  # ← goes to Screen 1


    return render_template('login.html', form=form)

# route for logout (POST only — GET logout is a CSRF risk)
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash(message='You have been logged out.', category='info')
    # if user logsout, take it to login page
    return redirect(url_for('auth.login'))


# ── Google OAuth ───────────────────────────────────────────────────────────────

@auth_bp.route('/google/login')
def google_login():
    """Redirect the user to Google's OAuth consent screen."""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/google/callback')
def google_callback():
    """
    Google redirects here after the user approves.
    Three scenarios:
      1. oauth_id already linked  → log in directly
      2. Email matches existing user → link Google to their account, log in
      3. New user entirely → create account, redirect to complete profile
    """
    token = oauth.google.authorize_access_token()
    userinfo = token.get('userinfo') or oauth.google.userinfo()

    google_id    = userinfo['sub']
    email        = userinfo.get('email', '').lower().strip()
    name         = userinfo.get('name', email.split('@')[0])

    # Scenario 1 — already linked
    user = User.query.filter_by(oauth_id=google_id).first()

    if not user:
        # Scenario 2 — email matches an existing password account → link
        user = User.query.filter_by(email=email).first()
        if user:
            user.oauth_provider = 'google'
            user.oauth_id       = google_id
            db.session.commit()
        else:
            # Scenario 3 — brand new user
            user = User(
                name=name,
                email=email,
                password=None,
                oauth_provider='google',
                oauth_id=google_id,
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Welcome to SkillSwap! Please complete your profile.', 'success')
            return redirect(url_for('user.home'))

    # Check ban
    if not user.is_active_account:
        flash('Your account has been suspended. Please contact support.', 'danger')
        return redirect(url_for('auth.login'))

    login_user(user)
    flash('Logged in with Google!', 'success')
    return redirect(url_for('swap.home'))


# ── Forgot password ────────────────────────────────────────────────────────────

def _get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Show 'enter your email' form and send a reset link."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()

        # Always show the same message to prevent email enumeration
        if user:
            if user.oauth_provider:  # Google-only account — no password to reset
                flash(
                    'This account uses Google login. '
                    'Please click "Continue with Google" instead.',
                    'warning'
                )
                return redirect(url_for('auth.login'))

            # Generate a signed, time-limited token
            token = _get_serializer().dumps(email, salt='password-reset')

            # Send the reset email via Brevo API
            import requests
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            html_content = render_template('reset_email.html', name=user.name, reset_url=reset_url)
            
            brevo_api_key = current_app.config.get('BREVO_API_KEY')
            sender_email = current_app.config.get('MAIL_SENDER', 'noreply@skillswap.com')
            
            if not brevo_api_key:
                current_app.logger.error('[MAIL] BREVO_API_KEY not set.')
                flash('Email sending is currently disabled.', 'danger')
                return render_template('forgot_password.html')
                
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "accept": "application/json",
                "api-key": brevo_api_key,
                "content-type": "application/json"
            }
            payload = {
                "sender": {"email": sender_email, "name": "SkillSwap"},
                "to": [{"email": email, "name": user.name}],
                "subject": "SkillSwap — Reset your password",
                "htmlContent": html_content
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
            except Exception as e:
                current_app.logger.error(f'[MAIL] Failed to send reset email via Brevo: {e}')
                if 'response' in locals() and hasattr(response, 'text'):
                    current_app.logger.error(f'[MAIL] Brevo Response: {response.text}')
                flash('Could not send email. Please check your mail settings.', 'danger')
                return render_template('forgot_password.html')

        flash('If that email is registered you will receive a reset link shortly.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Verify the token and let the user set a new password."""
    try:
        email = _get_serializer().loads(token, salt='password-reset', max_age=3600)
    except SignatureExpired:
        flash('This reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    except BadSignature:
        flash('Invalid reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('reset_password.html', token=token)

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)

        user.password = generate_password_hash(password)
        db.session.commit()
        flash('Password updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)
