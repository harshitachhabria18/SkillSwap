from flask import Blueprint, render_template
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    return render_template('register.html', form=form)