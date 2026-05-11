from flask import Blueprint, render_template, session, redirect, url_for, flash
from functools import wraps
from bson.objectid import ObjectId

from mongo import (
    users,
    doctors,
    appointments,
    medical_records,
    payments
)

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

    patient_id = session.get('patient_id')

    # Recent Appointments
    appts = list(
        appointments.find({
            "patient_id": patient_id
        }).sort("appointment_date", -1).limit(5)
    )

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

    # Stats
    stats = {
        'total': appointments.count_documents({
            "patient_id": patient_id
        }),

        'pending': appointments.count_documents({
            "patient_id": patient_id,
            "status": "pending"
        }),

        'approved': appointments.count_documents({
            "patient_id": patient_id,
            "status": "approved"
        })
    }

    return render_template(
    'patient/dashboard.html',
    appointments=appts,
    stats=stats,
    now=datetime.now()
    )


@patient_bp.route('/doctors')
@patient_required
def doctors_page():

    docs = list(doctors.find({
        "available": True
    }))

    # Attach User Info
    for doc in docs:

        user = users.find_one({
            "_id": ObjectId(doc['user_id'])
        })

        if user:
            doc['name'] = user.get('name')
            doc['phone'] = user.get('phone')

    return render_template(
        'patient/doctors.html',
        doctors=docs
    )


@patient_bp.route('/medical-records')
@patient_required
def medical_records_page():

    patient_id = session.get('patient_id')

    records = list(
        medical_records.find({
            "patient_id": patient_id
        }).sort("created_at", -1)
    )

    # Attach Doctor + Appointment Info
    for record in records:

        doctor = doctors.find_one({
            "_id": ObjectId(record['doctor_id'])
        })

        if doctor:

            user = users.find_one({
                "_id": ObjectId(doctor['user_id'])
            })

            if user:
                record['doctor_name'] = user.get('name')

            record['specialty'] = doctor.get('specialty')

        appointment = appointments.find_one({
            "_id": ObjectId(record['appointment_id'])
        })

        if appointment:
            record['appointment_date'] = appointment.get(
                'appointment_date'
            )

    return render_template(
        'patient/medical_records.html',
        records=records
    )


@patient_bp.route('/payments')
@patient_required
def payments_page():

    patient_id = session.get('patient_id')

    pays = list(
        payments.find({
            "patient_id": patient_id
        }).sort("created_at", -1)
    )

    # Attach Doctor + Appointment Info
    for pay in pays:

        appointment = appointments.find_one({
            "_id": ObjectId(pay['appointment_id'])
        })

        if appointment:

            pay['appointment_date'] = appointment.get(
                'appointment_date'
            )

            doctor = doctors.find_one({
                "_id": ObjectId(appointment['doctor_id'])
            })

            if doctor:

                user = users.find_one({
                    "_id": ObjectId(doctor['user_id'])
                })

                if user:
                    pay['doctor_name'] = user.get('name')

    return render_template(
        'patient/payments.html',
        payments=pays
    )
