@admin_bp.route('/reports')
@role_required('admin')
def reports():
    cursor.execute("SELECT COUNT(*) AS total_patients FROM users WHERE role='patient'")
    patients = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) AS total_doctors FROM users WHERE role='doctor'")
    doctors = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) AS total_appointments FROM appointments")
    appointments = cursor.fetchone()

    return render_template('admin/reports.html',
                           patients=patients,
                           doctors=doctors,
                           appointments=appointments)
