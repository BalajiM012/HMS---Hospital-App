hospital_mgmt/
├── app.py                  ← Flask entry point
├── config.py               ← DB config, secret key
├── requirements.txt
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/
│   ├── base.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   └── manage_doctors.html
│   ├── doctor/
│   │   ├── dashboard.html
│   │   └── appointments.html
│   └── patient/
│       ├── dashboard.html
│       └── book_appointment.html
├── routes/
│   ├── auth.py
│   ├── admin.py
│   ├── doctor.py
│   └── patient.py
└── db.sql                  ← All CREATE TABLE statements
