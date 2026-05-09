from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import query

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role     = request.form.get('role', '')

        user = query('SELECT * FROM users WHERE email=%s AND role=%s', (email, role), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['role']    = user['role']
            session['email']   = user['email']

            if role == 'patient':
                p = query('SELECT id FROM patients WHERE user_id=%s', (user['id'],), one=True)
                if p: session['patient_id'] = p['id']
            elif role == 'doctor':
                d = query('SELECT id FROM doctors WHERE user_id=%s', (user['id'],), one=True)
                if d: session['doctor_id'] = d['id']

            flash('Welcome back, ' + user['name'] + '!', 'success')
            if role == 'admin':   return redirect(url_for('admin.dashboard'))
            if role == 'doctor':  return redirect(url_for('doctor.dashboard'))
            if role == 'patient': return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid credentials or role.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone    = request.form.get('phone', '').strip()
        dob      = request.form.get('dob', '')
        gender   = request.form.get('gender', '')
        blood    = request.form.get('blood_group', '')
        address  = request.form.get('address', '')
        emergency= request.form.get('emergency_contact', '')

        existing = query('SELECT id FROM users WHERE email=%s', (email,), one=True)
        if existing:
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')

        hashed = generate_password_hash(password)
        uid = query(
            'INSERT INTO users (name, email, password_hash, role, phone) VALUES (%s,%s,%s,%s,%s)',
            (name, email, hashed, 'patient', phone), commit=True
        )
        query(
            'INSERT INTO patients (user_id, dob, gender, blood_group, address, emergency_contact) VALUES (%s,%s,%s,%s,%s,%s)',
            (uid, dob or None, gender, blood, address, emergency), commit=True
        )
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
