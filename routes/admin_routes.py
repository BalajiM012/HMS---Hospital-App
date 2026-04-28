from flask import Blueprint, render_template
from utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@role_required('admin')
def dashboard():
    return render_template('admin/dashboard.html')
