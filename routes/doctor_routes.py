from flask import Blueprint, render_template, request, redirect, current_app
from utils.decorators import role_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/')
@role_required('doctor')
def dashboard():
    appointments = list(current_app.db.appointments.find())
    return render_template('doctor/dashboard.html', appointments=appointments)


@doctor_bp.route('/approve/<id>')
@role_required('doctor')
def approve(id):
    from bson.objectid import ObjectId

    current_app.db.appointments.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "approved"}}
    )

    return redirect('/doctor')


@doctor_bp.route('/reject/<id>')
@role_required('doctor')
def reject(id):
    from bson.objectid import ObjectId

    current_app.db.appointments.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "rejected"}}
    )

    return redirect('/doctor')
