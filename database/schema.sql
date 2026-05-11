-- Hospital Management System - MySQL Schema
-- Railway MySQL Compatible

-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'doctor', 'patient') NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- DOCTORS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    qualification VARCHAR(200),
    experience_years INT DEFAULT 0,
    available BOOLEAN DEFAULT TRUE,
    consultation_fee DECIMAL(10,2) DEFAULT 0.00,

    CONSTRAINT fk_doctor_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =========================
-- PATIENTS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    dob DATE,
    gender ENUM('male', 'female', 'other'),
    blood_group VARCHAR(5),
    address TEXT,
    emergency_contact VARCHAR(20),

    CONSTRAINT fk_patient_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =========================
-- APPOINTMENTS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,

    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,

    reason TEXT,

    status ENUM(
        'pending',
        'approved',
        'rejected',
        'completed'
    ) DEFAULT 'pending',

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_appt_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_appt_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE CASCADE
);

-- =========================
-- MEDICAL RECORDS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS medical_records (
    id INT AUTO_INCREMENT PRIMARY KEY,

    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,

    diagnosis TEXT,
    prescription TEXT,
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_record_appointment
        FOREIGN KEY (appointment_id)
        REFERENCES appointments(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_record_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_record_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE CASCADE
);

-- =========================
-- PAYMENTS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,

    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,

    amount DECIMAL(10,2) NOT NULL,

    status ENUM('unpaid', 'paid')
        DEFAULT 'unpaid',

    payment_date TIMESTAMP NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_payment_appointment
        FOREIGN KEY (appointment_id)
        REFERENCES appointments(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_payment_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE
);

-- =========================
-- DEFAULT ADMIN ACCOUNT
-- Password: admin123
-- =========================
INSERT IGNORE INTO users (
    name,
    email,
    password_hash,
    role,
    phone
)
VALUES (
    'Super Admin',
    'admin@hospital.com',
    'pbkdf2:sha256:600000$placeholder$hash',
    'admin',
    '0000000000'
);
