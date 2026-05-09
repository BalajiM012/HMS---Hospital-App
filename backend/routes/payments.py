from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import query
from functools import wraps

payment_bp = Blueprint('payments', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@payment_bp.route('/')
@login_required
def index():
    role = session.get('role')
    if role == 'patient':
        pid = session.get('patient_id')
        pays = query('''
            SELECT p.*, u.name as doctor_name, a.appointment_date, d.specialty
            FROM payments p
            JOIN appointments a ON p.appointment_id = a.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            WHERE p.patient_id = %s
            ORDER BY p.created_at DESC
        ''', (pid,))
        return render_template('patient/payments.html', payments=pays)
    return redirect(url_for('admin.payments'))
