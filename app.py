from flask import Flask
from config import Config
from pymongo import MongoClient
from flask_mail import Mail

# Blueprints
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.admin_routes import admin_bp

mail = Mail()
client = MongoClient()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    mail.init_app(app)

    global client
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client.hospital

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
@app.route('/test-db')
def test_db():
    cursor.execute("SELECT 1")
    return "DB Connected"

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
