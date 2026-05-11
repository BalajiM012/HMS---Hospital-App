from flask import Blueprint, render_template, session, redirect, url_for, flash
from functools import wraps
from bson.objectid import ObjectId
from datetime import datetime

from mongo import (
    payments,
    appointments,
    doctors,
    users
)

payment_bp = Blueprint('payments', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated


@payment_bp.route('/')
@login_required
def index():

    role = session.get('role')

    # Patient Payments
    if role == 'patient':

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

                    pay['specialty'] = doctor.get('specialty')

        return render_template(
            'patient/payments.html',
            payments=pays
        )

    # Admin Redirect
    return redirect(url_for('admin.payments_page'))


@payment_bp.route('/<payment_id>/mark-paid', methods=['POST'])
@login_required
def mark_paid(payment_id):

    if session.get('role') != 'admin':

        flash('Admin access required.', 'error')

        return redirect(url_for('auth.login'))

    payments.update_one(
        {
            "_id": ObjectId(payment_id)
        },
        {
            "$set": {
                "status": "paid",
                "payment_date": datetime.utcnow()
            }
        }
    )

    flash('Payment marked as paid.', 'success')

    return redirect(url_for('admin.payments_page'))
