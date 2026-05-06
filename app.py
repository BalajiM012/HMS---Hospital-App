from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions.db import cursor, db

app = Flask(__name__)
app.secret_key = "secret"

# ---------------- AUTH ---------------- #

@app.route('/')
def home():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cursor.execute(
            "INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,'patient')",
            (name, email, password)
        )
        db.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect('/admin')
            elif user['role'] == 'doctor':
                return redirect('/doctor')
            else:
                return redirect('/patient')

        return "Invalid login"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- DASHBOARDS ---------------- #

@app.route('/patient')
def patient():
    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM users WHERE role='doctor'")
    doctors = cursor.fetchall()

    return render_template('patient_dashboard.html', doctors=doctors)


@app.route('/doctor')
def doctor():
    if 'user_id' not in session:
        return redirect('/login')

    doctor_id = session['user_id']

    cursor.execute("""
        SELECT a.*, u.name AS patient_name
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE doctor_id=%s
    """, (doctor_id,))

    data = cursor.fetchall()

    return render_template('doctor_dashboard.html', data=data)


@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM users WHERE role='doctor'")
    doctors = cursor.fetchall()

    cursor.execute("SELECT * FROM users WHERE role='patient'")
    patients = cursor.fetchall()

    return render_template('admin_dashboard.html', doctors=doctors, patients=patients)


# ---------------- APPOINTMENT ---------------- #

@app.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, date, time, status)
        VALUES (%s,%s,%s,%s,'pending')
    """, (
        session['user_id'],
        request.form['doctor_id'],
        request.form['date'],
        request.form['time']
    ))

    db.commit()

    return redirect('/patient')


# ---------------- STATUS UPDATE ---------------- #

@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):
    cursor.execute("UPDATE appointments SET status=%s WHERE id=%s", (status, id))
    db.commit()

    return redirect('/doctor')


# ---------------- RUN ---------------- #

if __name__ == '__main__':
    app.run(debug=True)
