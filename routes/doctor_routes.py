from flask import Blueprint, render_template, session, redirect
from extensions.db import cursor, db
from utils.decorators import role_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/doctor')
@role_required('doctor')
def dashboard():
    cursor.execute("""
        SELECT a.*, u.name AS patient_name
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE doctor_id=%s
    """, (session['user_id'],))

    data = cursor.fetchall()
    cursor.execute("""
    SELECT * FROM appointments
    WHERE doctor_id=%s AND date=%s AND time=%s
""", (doctor_id, date, time))

existing = cursor.fetchone()

if existing:
    return "Slot already booked!"
    return render_template('doctor/dashboard.html', data=data)


@doctor_bp.route('/update_status/<int:id>/<status>')
@role_required('doctor')
def update_status(id, status):
    cursor.execute("UPDATE appointments SET status=%s WHERE id=%s", (status, id))
    db.commit()
    return redirect('/doctor')
