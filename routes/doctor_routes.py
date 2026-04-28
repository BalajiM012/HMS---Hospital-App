from flask import Blueprint, render_template, session, current_app, redirect
from utils.decorators import role_required
from bson.objectid import ObjectId

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/')
@role_required('doctor')
def dashboard():

    doctor_id = session['user_id']

    # ✅ Get only this doctor's appointments
    appointments = list(current_app.db.appointments.find({
        "doctor_id": doctor_id
    }))

    enriched_appointments = []

    # ✅ Add patient info
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
