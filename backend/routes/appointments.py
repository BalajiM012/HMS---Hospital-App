from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from db import query
from functools import wraps

appt_bp = Blueprint('appointments', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@appt_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if session.get('role') != 'patient':
        flash('Only patients can book appointments.', 'error')
        return redirect(url_for('auth.login'))

    doctors = query('''
        SELECT d.id, u.name, d.specialty, d.consultation_fee, d.experience_years
        FROM doctors d JOIN users u ON d.user_id = u.id
        WHERE d.available = 1
    ''')

    if request.method == 'POST':
        pid     = session.get('patient_id')
        did     = request.form.get('doctor_id')
        date    = request.form.get('appointment_date')
        time    = request.form.get('appointment_time')
        reason  = request.form.get('reason', '')

        # Check for conflicts
        conflict = query('''
            SELECT id FROM appointments
            WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s
            AND status IN ('pending','approved')
        ''', (did, date, time), one=True)

        if conflict:
            flash('That time slot is already taken. Please choose another.', 'error')
            return render_template('appointments/book.html', doctors=doctors)

        query('''
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason)
            VALUES (%s,%s,%s,%s,%s)
        ''', (pid, did, date, time, reason), commit=True)
        flash('Appointment booked successfully! Waiting for doctor approval.', 'success')
        return redirect(url_for('patient.dashboard'))

    return render_template('appointments/book.html', doctors=doctors)

@appt_bp.route('/my')
@login_required
def my_appointments():
    role = session.get('role')
    if role == 'patient':
        pid = session.get('patient_id')
        appts = query('''
            SELECT a.*, u.name as doctor_name, d.specialty
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC
        ''', (pid,))
    elif role == 'doctor':
        did = session.get('doctor_id')
        appts = query('''
            SELECT a.*, u.name as patient_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN users u ON p.user_id = u.id
            WHERE a.doctor_id = %s
            ORDER BY a.appointment_date DESC
        ''', (did,))
    else:
        return redirect(url_for('admin.dashboard'))

    return render_template('appointments/list.html', appointments=appts, role=role)
