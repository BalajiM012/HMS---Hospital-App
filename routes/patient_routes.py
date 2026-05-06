from flask import Blueprint, render_template, request, session, redirect
from extensions.db import cursor, db
from utils.decorators import role_required

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/patient')
@role_required('patient')
def dashboard():
    cursor.execute("SELECT * FROM users WHERE role='doctor'")
    doctors = cursor.fetchall()
    return render_template('patient/dashboard.html', doctors=doctors)


@patient_bp.route('/book', methods=['POST'])
@role_required('patient')
def book():
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, date, time)
        VALUES (%s,%s,%s,%s)
    """, (
        session['user_id'],
        request.form['doctor_id'],
        request.form['date'],
        request.form['time']
    ))
    db.commit()

    return redirect('/patient')
