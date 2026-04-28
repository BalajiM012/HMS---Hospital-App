hospital_app/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
│
├── extensions/
│   ├── db.py              # MongoDB connection
│   └── mail.py            # Flask-Mail setup
│
├── routes/
│   ├── auth_routes.py
│   ├── patient_routes.py
│   ├── doctor_routes.py
│   ├── admin_routes.py
│   ├── appointment_routes.py
│   ├── record_routes.py
│   ├── pharmacy_routes.py
│   └── payment_routes.py
│
├── models/
│   ├── user_model.py
│   ├── appointment_model.py
│   ├── availability_model.py
│   ├── record_model.py
│   ├── pharmacy_model.py
│   └── payment_model.py
│
├── services/
│   ├── email_service.py
│   ├── appointment_service.py
│   ├── record_service.py
│   ├── pharmacy_service.py
│   └── payment_service.py
│
├── utils/
│   ├── decorators.py      # role_required
│   ├── security.py        # hashing
│   ├── validators.py
│   └── helpers.py
│
├── templates/
│   ├── base.html
│   │
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   │
│   ├── patient/
│   │   ├── dashboard.html
│   │   ├── appointments.html
│   │   ├── records.html
│   │   ├── pharmacy.html
│   │   └── payments.html
│   │
│   ├── doctor/
│   │   ├── dashboard.html
│   │   ├── availability.html
│   │   ├── add_record.html
│   │   └── patients.html
│   │
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── reports.html
│   │   └── doctors.html
│   │
│   └── shared/
│       ├── navbar.html
│       └── alerts.html
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/           # reports / prescriptions
│
└── instance/
    └── logs/
