from flask import Blueprint, render_template
from utils.decorators import role_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/')
@role_required('doctor')
def dashboard():
    return render_template('doctor/dashboard.html')
