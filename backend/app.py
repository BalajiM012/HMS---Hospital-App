import os
from flask import Flask, session, redirect, url_for
from dotenv import load_dotenv

from routes.auth import auth_bp
from routes.patient import patient_bp
from routes.doctor import doctor_bp
from routes.admin import admin_bp
from routes.appointments import appt_bp
from routes.payments import payment_bp

# MongoDB connection
from mongo import client

load_dotenv()


def create_app():
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='../frontend'
    )

    # Secret key
    app.secret_key = os.environ.get(
        'JWT_SECRET',
        'hospital-secret-2024-change-this'
    )

    app.config['SESSION_TYPE'] = 'filesystem'

    # MongoDB URI
    app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI')

    # Test MongoDB connection
    try:
        client.admin.command('ping')
        print("✅ MongoDB Connected Successfully")
    except Exception as e:
        print("❌ MongoDB Connection Failed:", e)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(appt_bp, url_prefix='/appointments')
    app.register_blueprint(payment_bp, url_prefix='/payments')

    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('role')

            if role == 'admin':
                return redirect(url_for('admin.dashboard'))

            if role == 'doctor':
                return redirect(url_for('doctor.dashboard'))

            if role == 'patient':
                return redirect(url_for('patient.dashboard'))

        return redirect(url_for('auth.login'))

    return app


app = create_app()

if __name__ == '__main__':
    app.run(
        debug=False,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
