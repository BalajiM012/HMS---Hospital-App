from flask import Flask, redirect
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.admin_routes import admin_bp
from routes.record_routes import record_bp
app.register_blueprint(record_bp)
app = Flask(__name__)
app.secret_key = "secret"

app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def home():
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)
