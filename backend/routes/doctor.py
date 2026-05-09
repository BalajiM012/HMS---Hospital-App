from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from db import query
from functools import wraps

doctor_bp = Blueprint('doctor', __name__)

def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'doctor':
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    did = session.get('doctor_id')
    appointments = query('''
        SELECT a.*, u.name as patient_name, p.blood_group
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date DESC LIMIT 10
    ''', (did,))
    stats = {
        'total':    query('SELECT COUNT(*) as c FROM appointments WHERE doctor_id=%s', (did,), one=True)['c'],
        'pending':  query("SELECT COUNT(*) as c FROM appointments WHERE doctor_id=%s AND status='pending'", (did,), one=True)['c'],
        'today':    query("SELECT COUNT(*) as c FROM appointments WHERE doctor_id=%s AND appointment_date=CURDATE()", (did,), one=True)['c'],
    }
    return render_template('doctor/dashboard.html', appointments=appointments, stats=stats)

@doctor_bp.route('/appointment/<int:appt_id>/action', methods=['POST'])
@doctor_required
def appointment_action(appt_id):
    action = request.form.get('action')
    notes  = request.form.get('notes', '')
    did = session.get('doctor_id')

    appt = query('SELECT * FROM appointments WHERE id=%s AND doctor_id=%s', (appt_id, did), one=True)
    if not appt:
        flash('Appointment not found.', 'error')
        return redirect(url_for('doctor.dashboard'))

    if action in ('approved', 'rejected', 'completed'):
        query('UPDATE appointments SET status=%s, notes=%s WHERE id=%s', (action, notes, appt_id), commit=True)
        if action == 'approved':
            doc = query('SELECT consultation_fee FROM doctors WHERE id=%s', (did,), one=True)
            existing = query('SELECT id FROM payments WHERE appointment_id=%s', (appt_id,), one=True)
            if not existing:
                query('INSERT INTO payments (appointment_id, patient_id, amount) VALUES (%s,%s,%s)',
                      (appt_id, appt['patient_id'], doc['consultation_fee']), commit=True)
        flash(f'Appointment {action}.', 'success')
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/appointment/<int:appt_id>/record', methods=['GET', 'POST'])
@doctor_required
def add_record(appt_id):
    did = session.get('doctor_id')
    appt = query('''
        SELECT a.*, u.name as patient_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE a.id=%s AND a.doctor_id=%s
    ''', (appt_id, did), one=True)

    if not appt:
        flash('Not found.', 'error')
        return redirect(url_for('doctor.dashboard'))

    if request.method == 'POST':
        diagnosis    = request.form.get('diagnosis', '')
        prescription = request.form.get('prescription', '')
        notes        = request.form.get('notes', '')
        existing = query('SELECT id FROM medical_records WHERE appointment_id=%s', (appt_id,), one=True)
        if existing:
            query('UPDATE medical_records SET diagnosis=%s, prescription=%s, notes=%s WHERE appointment_id=%s',
                  (diagnosis, prescription, notes, appt_id), commit=True)
        else:
            query('INSERT INTO medical_records (appointment_id, patient_id, doctor_id, diagnosis, prescription, notes) VALUES (%s,%s,%s,%s,%s,%s)',
                  (appt_id, appt['patient_id'], did, diagnosis, prescription, notes), commit=True)
        query("UPDATE appointments SET status='completed' WHERE id=%s", (appt_id,), commit=True)
        flash('Medical record saved.', 'success')
        return redirect(url_for('doctor.dashboard'))

    existing_record = query('SELECT * FROM medical_records WHERE appointment_id=%s', (appt_id,), one=True)
    return render_template('doctor/add_record.html', appointment=appt, record=existing_record)

@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def toggle_availability():
    did = session.get('doctor_id')
    current = query('SELECT available FROM doctors WHERE id=%s', (did,), one=True)
    new_val = 0 if current['available'] else 1
    query('UPDATE doctors SET available=%s WHERE id=%s', (new_val, did), commit=True)
    flash('Availability updated.', 'success')
    return redirect(url_for('doctor.dashboard'))
