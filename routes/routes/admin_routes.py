from flask import Blueprint, render_template, request, redirect
from extensions.db import cursor, db
from utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@role_required('admin')
def dashboard():
    cursor.execute("SELECT * FROM users WHERE role='doctor'")
    doctors = cursor.fetchall()

    cursor.execute("SELECT * FROM users WHERE role='patient'")
    patients = cursor.fetchall()

    return render_template('admin/dashboard.html', doctors=doctors, patients=patients)


@admin_bp.route('/add_doctor', methods=['POST'])
@role_required('admin')
def add_doctor():
    cursor.execute(
        "INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,'doctor')",
        (
            request.form['name'],
            request.form['email'],
            request.form['password']
        )
    )
    db.commit()

    return redirect('/admin')
