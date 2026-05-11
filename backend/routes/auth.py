from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

from mongo import users, patients, doctors

auth_bp = Blueprint('auth', __name__)


# ================= LOGIN =================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '')

        user = users.find_one({
            "email": email,
            "role": role
        })

        if user and check_password_hash(user['password_hash'], password):

            session['user_id'] = str(user['_id'])
            session['name'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']

            # Patient Session
            if role == 'patient':

                patient = patients.find_one({
                    "user_id": str(user['_id'])
                })

                if patient:
                    session['patient_id'] = str(patient['_id'])

            # Doctor Session
            elif role == 'doctor':

                doctor = doctors.find_one({
                    "user_id": str(user['_id'])
                })

                if doctor:
                    session['doctor_id'] = str(doctor['_id'])

            flash(f"Welcome back, {user['name']}!", 'success')

            if role == 'admin':
                return redirect(url_for('admin.dashboard'))

            elif role == 'doctor':
                return redirect(url_for('doctor.dashboard'))

            elif role == 'patient':
                return redirect(url_for('patient.dashboard'))

        else:
            flash('Invalid credentials or role.', 'error')

    return render_template('auth/login.html')


# ================= PATIENT REGISTER =================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()

        dob = request.form.get('dob', '')
        gender = request.form.get('gender', '')
        blood = request.form.get('blood_group', '')
        address = request.form.get('address', '')
        emergency = request.form.get('emergency_contact', '')

        existing = users.find_one({
            "email": email
        })

        if existing:
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')

        hashed = generate_password_hash(password)

        user_result = users.insert_one({
            "name": name,
            "email": email,
            "password_hash": hashed,
            "role": "patient",
            "phone": phone
        })

        user_id = str(user_result.inserted_id)

        patients.insert_one({
            "user_id": user_id,
            "dob": dob,
            "gender": gender,
            "blood_group": blood,
            "address": address,
            "emergency_contact": emergency
        })

        flash('Registration successful! Please login.', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ================= ADMIN REGISTER =================
@auth_bp.route('/register-admin', methods=['GET', 'POST'])
def register_admin():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing = users.find_one({
            "email": email
        })

        if existing:
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register_admin'))

        hashed = generate_password_hash(password)

        users.insert_one({
            "name": name,
            "email": email,
            "password_hash": hashed,
            "role": "admin"
        })

        flash('Admin registered successfully', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/register_admin.html')


# ================= DOCTOR REGISTER =================
@auth_bp.route('/register-doctor', methods=['GET', 'POST'])
def register_doctor():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        specialty = request.form.get('specialty')
        experience = request.form.get('experience')

        existing = users.find_one({
            "email": email
        })

        if existing:
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register_doctor'))

        hashed = generate_password_hash(password)

        user_id = users.insert_one({
            "name": name,
            "email": email,
            "password_hash": hashed,
            "role": "doctor"
        }).inserted_id

        doctors.insert_one({
            "user_id": str(user_id),
            "specialty": specialty,
            "experience": experience,
            "available": True
        })

        flash('Doctor registered successfully', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/register_doctor.html')


# ================= LOGOUT =================
@auth_bp.route('/logout')
def logout():

    session.clear()

    flash('You have been logged out.', 'info')

    return redirect(url_for('auth.login'))
