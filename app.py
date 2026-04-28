from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

client = MongoClient(app.config["MONGO_URI"])
db = client.hospital

# ---------------- AUTH ---------------- #

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = {
            "name": request.form['name'],
            "email": request.form['email'],
            "password": generate_password_hash(request.form['password']),
            "role": "patient"
        }
        db.users.insert_one(user)
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = db.users.find_one({"email": request.form['email']})

        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect('/admin')
            elif user['role'] == 'doctor':
                return redirect('/doctor')
            else:
                return redirect('/patient')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- DASHBOARDS ---------------- #

@app.route('/patient')
def patient():
    return render_template('patient_dashboard.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor_dashboard.html')

@app.route('/admin')
def admin():
    return render_template('admin_dashboard.html')

# ---------------- APPOINTMENT ---------------- #

@app.route('/book', methods=['POST'])
def book():
    appointment = {
        "patient_id": session['user_id'],
        "doctor_id": request.form['doctor_id'],
        "date": request.form['date'],
        "time": request.form['time'],
        "status": "pending"
    }

    db.appointments.insert_one(appointment)

    # EMAIL TRIGGER
    from services.email_service import send_email
    send_email("doctor@email.com", "New Appointment", "New booking received")

    return redirect('/patient')

# ---------------- RUN ---------------- #

if __name__ == '__main__':
    app.run(debug=True)
