from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import query
from functools import wraps

patient_bp = Blueprint('patient', __name__)

def patient_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'patient':
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@patient_bp.route('/dashboard')
@patient_required
def dashboard():
    pid = session.get('patient_id')
    appointments = query('''
        SELECT a.*, u.name as doctor_name, d.specialty
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC LIMIT 5
    ''', (pid,))
    stats = {
        'total': query('SELECT COUNT(*) as c FROM appointments WHERE patient_id=%s', (pid,), one=True)['c'],
        'pending': query("SELECT COUNT(*) as c FROM appointments WHERE patient_id=%s AND status='pending'", (pid,), one=True)['c'],
        'approved': query("SELECT COUNT(*) as c FROM appointments WHERE patient_id=%s AND status='approved'", (pid,), one=True)['c'],
    }
    return render_template('patient/dashboard.html', appointments=appointments, stats=stats)

@patient_bp.route('/doctors')
@patient_required
def doctors():
    docs = query('''
        SELECT d.id, u.name, u.phone, d.specialty, d.qualification, 
               d.experience_years, d.available, d.consultation_fee
        FROM doctors d JOIN users u ON d.user_id = u.id
        WHERE d.available = 1
    ''')
    return render_template('patient/doctors.html', doctors=docs)

@patient_bp.route('/medical-records')
@patient_required
def medical_records():
    pid = session.get('patient_id')
    records = query('''
        SELECT mr.*, u.name as doctor_name, d.specialty,
               a.appointment_date
        FROM medical_records mr
        JOIN doctors d ON mr.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        JOIN appointments a ON mr.appointment_id = a.id
        WHERE mr.patient_id = %s
        ORDER BY mr.created_at DESC
    ''', (pid,))
    return render_template('patient/medical_records.html', records=records)

@patient_bp.route('/payments')
@patient_required
def payments():
    pid = session.get('patient_id')
    pays = query('''
        SELECT p.*, u.name as doctor_name, a.appointment_date
        FROM payments p
        JOIN appointments a ON p.appointment_id = a.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE p.patient_id = %s
        ORDER BY p.created_at DESC
    ''', (pid,))
    return render_template('patient/payments.html', payments=pays)
