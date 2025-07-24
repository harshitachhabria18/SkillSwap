from flask import Blueprint, render_template

swap_bp = Blueprint('swap', __name__, url_prefix='/swap', template_folder='templates')

@swap_bp.route('/')
def home():
    return render_template('swap/browse.html')  # ✅ Template inside app/swap/templates/swap
