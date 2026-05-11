from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash
from functools import wraps
from bson.objectid import ObjectId
from datetime import datetime

from mongo import (
    users,
    doctors,
    patients,
    appointments,
    payments
)

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
        'doctors': doctors.count_documents({}),
        'patients': patients.count_documents({}),
        'appointments': appointments.count_documents({}),
        'pending': appointments.count_documents({"status": "pending"}),
        'revenue': 0
    }

    # Calculate Revenue
    paid_payments = payments.find({"status": "paid"})

    revenue = 0

    for pay in paid_payments:
        revenue += float(pay.get('amount', 0))

    stats['revenue'] = revenue

    # Recent Appointments
    recent_appts = list(
        appointments.find().sort("created_at", -1).limit(10)
    )

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_appts=recent_appts
    )


@admin_bp.route('/doctors')
@admin_required
def doctors_page():

    docs = list(doctors.find())

    for doc in docs:

        user = users.find_one({
            "_id": ObjectId(doc['user_id'])
        })

        if user:
            doc['name'] = user.get('name')
            doc['email'] = user.get('email')
            doc['phone'] = user.get('phone')

    return render_template(
        'admin/doctors.html',
        doctors=docs
    )


@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@admin_required
def add_doctor():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '')

        specialty = request.form.get('specialty', '')
        qualification = request.form.get('qualification', '')
        experience = request.form.get('experience_years', 0)
        fee = request.form.get('consultation_fee', 0)

        existing = users.find_one({
            "email": email
        })

        if existing:
            flash('Email already exists.', 'error')
            return render_template('admin/add_doctor.html')

        hashed = generate_password_hash(password)

        # Create User
        user_result = users.insert_one({
            "name": name,
            "email": email,
            "password_hash": hashed,
            "role": "doctor",
            "phone": phone,
            "created_at": datetime.utcnow()
        })

        user_id = str(user_result.inserted_id)

        # Create Doctor
        doctors.insert_one({
            "user_id": user_id,
            "specialty": specialty,
            "qualification": qualification,
            "experience_years": int(experience),
            "consultation_fee": float(fee),
            "available": True,
            "created_at": datetime.utcnow()
        })

        flash(f'Doctor {name} added successfully.', 'success')

        return redirect(url_for('admin.doctors_page'))

    return render_template('admin/add_doctor.html')


@admin_bp.route('/doctors/<doc_id>/delete', methods=['POST'])
@admin_required
def delete_doctor(doc_id):

    doctor = doctors.find_one({
        "_id": ObjectId(doc_id)
    })

    if doctor:

        users.delete_one({
            "_id": ObjectId(doctor['user_id'])
        })

        doctors.delete_one({
            "_id": ObjectId(doc_id)
        })

        flash('Doctor removed.', 'success')

    return redirect(url_for('admin.doctors_page'))


@admin_bp.route('/patients')
@admin_required
def patients_page():

    pats = list(patients.find())

    for patient in pats:

        user = users.find_one({
            "_id": ObjectId(patient['user_id'])
        })

        if user:
            patient['name'] = user.get('name')
            patient['email'] = user.get('email')
            patient['phone'] = user.get('phone')

    return render_template(
        'admin/patients.html',
        patients=pats
    )



@admin_bp.route('/payments')
@admin_required
def payments_page():

    pays = list(payments.find().sort("created_at", -1))

    return render_template(
        'admin/payments.html',
        payments=pays
    )


@admin_bp.route('/payments/<pay_id>/mark-paid', methods=['POST'])
@admin_required
def mark_paid(pay_id):

    payments.update_one(
        {"_id": ObjectId(pay_id)},
        {
            "$set": {
                "status": "paid",
                "payment_date": datetime.utcnow()
            }
        }
    )

    flash('Payment marked as paid.', 'success')

    return redirect(url_for('admin.payments_page'))
