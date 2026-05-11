from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from functools import wraps
from bson.objectid import ObjectId
from datetime import datetime

from mongo import (
    users,
    doctors,
    patients,
    appointments
)

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

    # Get Available Doctors
    doctor_list = list(doctors.find({
        "available": True
    }))

    # Attach User Info
    for doctor in doctor_list:

        user = users.find_one({
            "_id": ObjectId(doctor['user_id'])
        })

        if user:
            doctor['name'] = user.get('name')

    if request.method == 'POST':

        patient_id = session.get('patient_id')

        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')

        reason = request.form.get('reason', '')

        # Check Conflict
        conflict = appointments.find_one({
            "doctor_id": doctor_id,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": {
                "$in": ["pending", "approved"]
            }
        })

        if conflict:
            flash(
                'That time slot is already taken. Please choose another.',
                'error'
            )

            return render_template(
                'appointments/book.html',
                doctors=doctor_list
            )

        # Insert Appointment
        appointments.insert_one({
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "reason": reason,
            "status": "pending",
            "created_at": datetime.utcnow()
        })

        flash(
            'Appointment booked successfully! Waiting for doctor approval.',
            'success'
        )

        return redirect(url_for('patient.dashboard'))

    return render_template(
        'appointments/book.html',
        doctors=doctor_list
    )


@appt_bp.route('/my')
@login_required
def my_appointments():

    role = session.get('role')

    # Patient Appointments
    if role == 'patient':

        patient_id = session.get('patient_id')

        appts = list(appointments.find({
            "patient_id": patient_id
        }).sort("appointment_date", -1))

        # Attach Doctor Info
        for appt in appts:

            doctor = doctors.find_one({
                "_id": ObjectId(appt['doctor_id'])
            })

            if doctor:

                user = users.find_one({
                    "_id": ObjectId(doctor['user_id'])
                })

                if user:
                    appt['doctor_name'] = user.get('name')

                appt['specialty'] = doctor.get('specialty')

    # Doctor Appointments
    elif role == 'doctor':

        doctor_id = session.get('doctor_id')

        appts = list(appointments.find({
            "doctor_id": doctor_id
        }).sort("appointment_date", -1))

        # Attach Patient Info
        for appt in appts:

            patient = patients.find_one({
                "_id": ObjectId(appt['patient_id'])
            })

            if patient:

                user = users.find_one({
                    "_id": ObjectId(patient['user_id'])
                })

                if user:
                    appt['patient_name'] = user.get('name')

    else:
        return redirect(url_for('admin.dashboard'))

    return render_template(
        'appointments/list.html',
        appointments=appts,
        role=role
    )
