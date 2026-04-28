from flask import Blueprint, render_template, request, session, redirect, current_app
from utils.decorators import role_required
from services.email_service import send_email
from bson.objectid import ObjectId   # ✅ FIXED IMPORT

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/')
@role_required('patient')
def dashboard():
    return render_template('patient/dashboard.html')


@patient_bp.route('/book', methods=['POST'])
@role_required('patient')
def book():

    # ✅ Create appointment
    appointment = {
        "patient_id": session['user_id'],
        "doctor_id": request.form['doctor_id'],
        "date": request.form['date'],
        "time": request.form['time'],
        "status": "pending"
    }

    # ✅ Insert into DB
    current_app.db.appointments.insert_one(appointment)

    # ✅ Get doctor details
    doctor = current_app.db.users.find_one({
        "_id": ObjectId(request.form['doctor_id'])
    })

    # ✅ Send email safely
    if doctor:
        send_email(
            to=doctor['email'],
            subject="New Appointment",
            body=f"New appointment on {request.form['date']} at {request.form['time']}"
        )

    return redirect('/patient')
