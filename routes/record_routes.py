from flask import Blueprint, request, redirect, session, render_template
from extensions.db import cursor, db
from utils.decorators import role_required

record_bp = Blueprint('record', __name__)

# Doctor adds record
@record_bp.route('/add_record/<int:appointment_id>', methods=['POST'])
@role_required('doctor')
def add_record(appointment_id):
    diagnosis = request.form['diagnosis']
    prescription = request.form['prescription']

    cursor.execute("""
        INSERT INTO records (appointment_id, diagnosis, prescription)
        VALUES (%s,%s,%s)
    """, (appointment_id, diagnosis, prescription))

    db.commit()
    return redirect('/doctor')


# Patient views records
@record_bp.route('/records')
@role_required('patient')
def view_records():
    cursor.execute("""
        SELECT r.*, u.name AS doctor_name, a.date
        FROM records r
        JOIN appointments a ON r.appointment_id = a.id
        JOIN users u ON a.doctor_id = u.id
        WHERE a.patient_id = %s
    """, (session['user_id'],))

    data = cursor.fetchall()
    return render_template('patient/records.html', data=data)
