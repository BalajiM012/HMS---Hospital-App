from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash
from db import query
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'doctors':      query('SELECT COUNT(*) as c FROM doctors', one=True)['c'],
        'patients':     query('SELECT COUNT(*) as c FROM patients', one=True)['c'],
        'appointments': query('SELECT COUNT(*) as c FROM appointments', one=True)['c'],
        'pending':      query("SELECT COUNT(*) as c FROM appointments WHERE status='pending'", one=True)['c'],
        'revenue':      query("SELECT COALESCE(SUM(amount),0) as c FROM payments WHERE status='paid'", one=True)['c'],
    }
    recent_appts = query('''
        SELECT a.*, u_p.name as patient_name, u_d.name as doctor_name, d.specialty
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u_p ON p.user_id = u_p.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u_d ON d.user_id = u_d.id
        ORDER BY a.created_at DESC LIMIT 10
    ''')
    return render_template('admin/dashboard.html', stats=stats, recent_appts=recent_appts)

@admin_bp.route('/doctors')
@admin_required
def doctors():
    docs = query('''
        SELECT d.*, u.name, u.email, u.phone, u.created_at as joined
        FROM doctors d JOIN users u ON d.user_id = u.id
        ORDER BY u.created_at DESC
    ''')
    return render_template('admin/doctors.html', doctors=docs)

@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@admin_required
def add_doctor():
    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        email       = request.form.get('email', '').strip()
        password    = request.form.get('password', '')
        phone       = request.form.get('phone', '')
        specialty   = request.form.get('specialty', '')
        qual        = request.form.get('qualification', '')
        exp         = request.form.get('experience_years', 0)
        fee         = request.form.get('consultation_fee', 0)

        existing = query('SELECT id FROM users WHERE email=%s', (email,), one=True)
        if existing:
            flash('Email already exists.', 'error')
            return render_template('admin/add_doctor.html')

        hashed = generate_password_hash(password)
        uid = query(
            'INSERT INTO users (name, email, password_hash, role, phone) VALUES (%s,%s,%s,%s,%s)',
            (name, email, hashed, 'doctor', phone), commit=True
        )
        query(
            'INSERT INTO doctors (user_id, specialty, qualification, experience_years, consultation_fee) VALUES (%s,%s,%s,%s,%s)',
            (uid, specialty, qual, exp, fee), commit=True
        )
        flash(f'Doctor {name} added successfully.', 'success')
        return redirect(url_for('admin.doctors'))

    return render_template('admin/add_doctor.html')

@admin_bp.route('/doctors/<int:doc_id>/delete', methods=['POST'])
@admin_required
def delete_doctor(doc_id):
    doc = query('SELECT user_id FROM doctors WHERE id=%s', (doc_id,), one=True)
    if doc:
        query('DELETE FROM users WHERE id=%s', (doc['user_id'],), commit=True)
        flash('Doctor removed.', 'success')
    return redirect(url_for('admin.doctors'))

@admin_bp.route('/patients')
@admin_required
def patients():
    pats = query('''
        SELECT p.*, u.name, u.email, u.phone, u.created_at as joined
        FROM patients p JOIN users u ON p.user_id = u.id
        ORDER BY u.created_at DESC
    ''')
    return render_template('admin/patients.html', patients=pats)

@admin_bp.route('/payments')
@admin_required
def payments():
    pays = query('''
        SELECT pay.*, u_p.name as patient_name, u_d.name as doctor_name
        FROM payments pay
        JOIN patients p ON pay.patient_id = p.id
        JOIN users u_p ON p.user_id = u_p.id
        JOIN appointments a ON pay.appointment_id = a.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u_d ON d.user_id = u_d.id
        ORDER BY pay.created_at DESC
    ''')
    return render_template('admin/payments.html', payments=pays)

@admin_bp.route('/payments/<int:pay_id>/mark-paid', methods=['POST'])
@admin_required
def mark_paid(pay_id):
    query("UPDATE payments SET status='paid', payment_date=NOW() WHERE id=%s", (pay_id,), commit=True)
    flash('Payment marked as paid.', 'success')
    return redirect(url_for('admin.payments'))
