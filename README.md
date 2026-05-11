# 🏥 MediCare — Hospital Management System

A full-stack hospital management system built using Flask + MySQL with role-based access for Admins, Doctors, and Patients.

🚀 Live Demo: https://hms-hospital-app.onrender.com


# 🏥 MediCare — Hospital Management System

A full-stack hospital management web app built with **Flask + MySQL**, deployable on **Render (backend) + Railway (MySQL)**.

---

## 🚀 Features

| Module | Features |
|--------|----------|
| **Auth** | Register/Login with role-based access (Admin, Doctor, Patient) |
| **Patient** | Book appointments, view doctors, medical records, payment history |
| **Doctor** | Dashboard, approve/reject appointments, add medical records, toggle availability |
| **Admin** | Add/remove doctors, view all patients, manage payments |
| **Appointments** | Book, view, approve/reject with conflict detection |
| **Medical Records** | Diagnosis + Prescription per appointment |
| **Payments** | Auto-created on approval, mark as paid |

---

## 🗂️ Project Structure

```
hospital-management/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── db.py                   # DB connection helper
│   ├── requirements.txt
│   ├── gunicorn.conf.py        # Render production server
│   ├── .env.example            # Copy to .env
│   ├── routes/
│   │   ├── auth.py             # Login / Register / Logout
│   │   ├── patient.py          # Patient pages
│   │   ├── doctor.py           # Doctor pages
│   │   ├── admin.py            # Admin pages
│   │   ├── appointments.py     # Book & list appointments
│   │   └── payments.py         # Payment views
│   └── templates/
│       ├── base.html           # Sidebar layout
│       ├── auth/               # Login & Register
│       ├── patient/            # Dashboard, doctors, records, payments
│       ├── doctor/             # Dashboard, add record
│       ├── admin/              # Dashboard, doctors, patients, payments
│       └── appointments/       # Book, list
├── database/
│   └── schema.sql              # Full MySQL schema
├── render.yaml                 # Render deployment config
└── .gitignore
```

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+ (local) OR Railway (cloud)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/hospital-management.git
cd hospital-management/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# 5. Create database + tables
mysql -u root -p < ../database/schema.sql

# 6. Create admin account
python -c "
from werkzeug.security import generate_password_hash
print(generate_password_hash('admin123'))
"
# Then run this SQL with that hash:
# UPDATE users SET password_hash='PASTE_HASH' WHERE email='admin@hospital.com';

# 7. Run the app
python app.py
# Open: http://localhost:5000
```

---

## ☁️ Cloud Deployment

### Step 1 — Railway MySQL

1. Go to [railway.app](https://railway.app) → New Project → **Add MySQL Plugin**
2. Open the MySQL plugin → **Variables** tab
3. Copy these values (you'll need them for Render):
   - `MYSQLHOST` → your `MYSQL_HOST`
   - `MYSQLPORT` → `MYSQL_PORT`
   - `MYSQLUSER` → `MYSQL_USER`
   - `MYSQLPASSWORD` → `MYSQL_PASSWORD`
   - `MYSQL_DATABASE` → usually `railway`
4. Click **Connect** → use the connection string in MySQL Workbench or any client
5. Run `database/schema.sql` to create tables
6. Set admin password hash (see Local Setup step 6)

---

### Step 2 — Push to GitHub

```bash
# In the project root
git init
git add .
git commit -m "Initial commit — Hospital Management System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hospital-management.git
git push -u origin main
```

---

### Step 3 — Render Backend

1. Go to [render.com](https://render.com) → New → **Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app -c gunicorn.conf.py`
   - **Runtime**: Python 3
4. Add **Environment Variables**:
   ```
   SECRET_KEY        = (generate a random 32-char string)
   MYSQL_HOST        = (from Railway)
   MYSQL_PORT        = 3306
   MYSQL_USER        = (from Railway)
   MYSQL_PASSWORD    = (from Railway)
   MYSQL_DATABASE    = railway
   ```
5. Click **Create Web Service** → wait ~3 mins for deploy
6. Your app is live at `https://YOUR-APP.onrender.com`

---

## 👥 Default Accounts

After running the SQL schema:

| Role | Email | Password | Notes |
|------|-------|----------|-------|
| Admin | admin@hospital.com | (set manually) | See setup step 6 |
| Doctor | (add via admin panel) | (set by admin) | |
| Patient | (register via /auth/register) | (self-set) | |

---

## 🔐 Role-Based Access

| Page | Admin | Doctor | Patient |
|------|-------|--------|---------|
| `/admin/dashboard` | ✅ | ❌ | ❌ |
| `/doctor/dashboard` | ❌ | ✅ | ❌ |
| `/patient/dashboard` | ❌ | ❌ | ✅ |
| `/appointments/book` | ❌ | ❌ | ✅ |
| `/appointments/my` | ❌ | ✅ | ✅ |

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS (custom), JavaScript |
| Backend | Python, Flask, Blueprints |
| Database | MySQL (PyMySQL driver) |
| Auth | Werkzeug password hashing, Flask sessions |
| Deployment | Render (backend), Railway (MySQL) |

---

## 🗃️ Database Schema

```
users ──────────────┐
  ├── patients       │ (user_id FK)
  └── doctors        │ (user_id FK)
                     │
appointments ────────┤ (patient_id, doctor_id FK)
  ├── medical_records│ (appointment_id FK)
  └── payments       │ (appointment_id FK)
```

---

## 📝 Notes

- Sessions expire on browser close (configurable in `app.py`)
- Consultation fee is auto-billed when doctor approves appointment
- Doctor availability can be toggled from doctor dashboard
- Admin must manually set their password hash after schema import
