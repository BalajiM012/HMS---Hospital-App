from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from functools import wraps
from bson.objectid import ObjectId
from datetime import datetime

from mongo import (
    users,
    doctors,
    patients,
    appointments,
    payments,
    medical_records
)

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

    doctor_id = session.get('doctor_id')

    # Recent Appointments
    appts = list(
        appointments.find({
            "doctor_id": doctor_id
        }).sort("appointment_date", -1).limit(10)
    )

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

            appt['blood_group'] = patient.get('blood_group')

    # Stats
    stats = {
        'total': appointments.count_documents({
            "doctor_id": doctor_id
        }),

        'pending': appointments.count_documents({
            "doctor_id": doctor_id,
            "status": "pending"
        }),

        'today': appointments.count_documents({
            "doctor_id": doctor_id,
            "appointment_date": datetime.utcnow().strftime('%Y-%m-%d')
        })
    }

    return render_template(
        'doctor/dashboard.html',
        appointments=appts,
        stats=stats
    )


@doctor_bp.route('/appointment/<appt_id>/action', methods=['POST'])
@doctor_required
def appointment_action(appt_id):

    action = request.form.get('action')
    notes = request.form.get('notes', '')

    doctor_id = session.get('doctor_id')

    appt = appointments.find_one({
        "_id": ObjectId(appt_id),
        "doctor_id": doctor_id
    })

    if not appt:
        flash('Appointment not found.', 'error')
        return redirect(url_for('doctor.dashboard'))

    if action in ['approved', 'rejected', 'completed']:

        appointments.update_one(
            {"_id": ObjectId(appt_id)},
            {
                "$set": {
                    "status": action,
                    "notes": notes
                }
            }
        )

        # Auto Create Payment
        if action == 'approved':

            doctor = doctors.find_one({
                "_id": ObjectId(doctor_id)
            })

            existing_payment = payments.find_one({
                "appointment_id": appt_id
            })

            if not existing_payment:

                payments.insert_one({
                    "appointment_id": appt_id,
                    "patient_id": appt['patient_id'],
                    "amount": doctor.get('consultation_fee', 0),
                    "status": "pending",
                    "created_at": datetime.utcnow()
                })

        flash(f'Appointment {action}.', 'success')

    return redirect(url_for('doctor.dashboard'))


@doctor_bp.route('/appointment/<appt_id>/record', methods=['GET', 'POST'])
@doctor_required
def add_record(appt_id):

    doctor_id = session.get('doctor_id')

    appt = appointments.find_one({
        "_id": ObjectId(appt_id),
        "doctor_id": doctor_id
    })

    if not appt:
        flash('Appointment not found.', 'error')
        return redirect(url_for('doctor.dashboard'))

    # Patient Info
    patient = patients.find_one({
        "_id": ObjectId(appt['patient_id'])
    })

    patient_name = ""

    if patient:

        user = users.find_one({
            "_id": ObjectId(patient['user_id'])
        })

        if user:
            patient_name = user.get('name')

    appt['patient_name'] = patient_name

    if request.method == 'POST':

        diagnosis = request.form.get('diagnosis', '')
        prescription = request.form.get('prescription', '')
        notes = request.form.get('notes', '')

        existing = medical_records.find_one({
            "appointment_id": appt_id
        })

        if existing:

            medical_records.update_one(
                {"appointment_id": appt_id},
                {
                    "$set": {
                        "diagnosis": diagnosis,
                        "prescription": prescription,
                        "notes": notes
                    }
                }
            )

        else:

            medical_records.insert_one({
                "appointment_id": appt_id,
                "patient_id": appt['patient_id'],
                "doctor_id": doctor_id,
                "diagnosis": diagnosis,
                "prescription": prescription,
                "notes": notes,
                "created_at": datetime.utcnow()
            })

        appointments.update_one(
            {"_id": ObjectId(appt_id)},
            {
                "$set": {
                    "status": "completed"
                }
            }
        )

        flash('Medical record saved.', 'success')

        return redirect(url_for('doctor.dashboard'))

    existing_record = medical_records.find_one({
        "appointment_id": appt_id
    })

    return render_template(
        'doctor/add_record.html',
        appointment=appt,
        record=existing_record
    )


@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def toggle_availability():

    doctor_id = session.get('doctor_id')

    doctor = doctors.find_one({
        "_id": ObjectId(doctor_id)
    })

    if doctor:

        new_value = not doctor.get('available', True)

        doctors.update_one(
            {"_id": ObjectId(doctor_id)},
            {
                "$set": {
                    "available": new_value
                }
            }
        )

    flash('Availability updated.', 'success')

    return redirect(url_for('doctor.dashboard'))
