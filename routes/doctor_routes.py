from flask import Blueprint, render_template, session, current_app, redirect
from utils.decorators import role_required
from bson.objectid import ObjectId
from services.email_service import send_email

doctor_bp = Blueprint('doctor', __name__)

# ---------------- DASHBOARD ---------------- #

@doctor_bp.route('/')
@role_required('doctor')
def dashboard():

    doctor_id = session['user_id']

    # ✅ Only this doctor's appointments
    appointments = list(current_app.db.appointments.find({
        "doctor_id": doctor_id
    }))

    enriched_appointments = []

    for a in appointments:
        patient = current_app.db.users.find_one({
            "_id": ObjectId(a['patient_id'])
        })

        enriched_appointments.append({
            "_id": a['_id'],
            "date": a['date'],
            "time": a['time'],
            "status": a['status'],
            "patient_name": patient['name'] if patient else "Unknown",
            "patient_email": patient['email'] if patient else "N/A"
        })

    return render_template(
        'doctor/dashboard.html',
        appointments=enriched_appointments
    )


# ---------------- APPROVE ---------------- #

@doctor_bp.route('/approve/<id>')
@role_required('doctor')
def approve(id):

    doctor_id = session['user_id']

    # ✅ SECURITY FIX (important)
    appointment = current_app.db.appointments.find_one({
        "_id": ObjectId(id),
        "doctor_id": doctor_id
    })

    if not appointment:
        return "Unauthorized or not found"

    # ✅ Update
    current_app.db.appointments.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "approved"}}
    )

    # ✅ Get patient
    patient = current_app.db.users.find_one({
        "_id": ObjectId(appointment['patient_id'])
    })

    # ✅ Email
    if patient:
        try:
            send_email(
                to=patient['email'],
                subject="Appointment Approved",
                body=f"Your appointment on {appointment['date']} at {appointment['time']} is APPROVED"
            )
        except Exception as e:
            print("Email error:", e)

    return redirect('/doctor')


# ---------------- REJECT ---------------- #

@doctor_bp.route('/reject/<id>')
@role_required('doctor')
def reject(id):

    doctor_id = session['user_id']

    # ✅ SECURITY FIX
    appointment = current_app.db.appointments.find_one({
        "_id": ObjectId(id),
        "doctor_id": doctor_id
    })

    if not appointment:
        return "Unauthorized or not found"

    # ✅ Update
    current_app.db.appointments.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "rejected"}}
    )

    # ✅ Get patient
    patient = current_app.db.users.find_one({
        "_id": ObjectId(appointment['patient_id'])
    })

    # ✅ Email
    if patient:
        try:
            send_email(
                to=patient['email'],
                subject="Appointment Rejected",
                body=f"Your appointment on {appointment['date']} at {appointment['time']} was REJECTED"
            )
        except Exception as e:
            print("Email error:", e)

    return redirect('/doctor')
