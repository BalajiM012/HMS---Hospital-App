-- =====================================================
-- Hospital Management System - Railway MySQL Schema
-- Compatible with Railway + Flask + PyMySQL
-- =====================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- DROP TABLES (SAFE REDEPLOY ORDER)
-- =====================================================

DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS medical_records;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- USERS TABLE
-- =====================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    role ENUM('admin', 'doctor', 'patient') NOT NULL,

    phone VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
);

-- =====================================================
-- DOCTORS TABLE
-- =====================================================

CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL UNIQUE,

    specialty VARCHAR(100) NOT NULL,

    qualification VARCHAR(200),

    experience_years INT DEFAULT 0,

    available BOOLEAN DEFAULT TRUE,

    consultation_fee DECIMAL(10,2) DEFAULT 0.00,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_doctor_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_doctors_specialty (specialty),
    INDEX idx_doctors_available (available)
);

-- =====================================================
-- PATIENTS TABLE
-- =====================================================

CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL UNIQUE,

    dob DATE,

    gender ENUM('male', 'female', 'other'),

    blood_group VARCHAR(5),

    address TEXT,

    emergency_contact VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_patient_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =====================================================
-- APPOINTMENTS TABLE
-- =====================================================

CREATE TABLE appointments (
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

    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_appointment_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE CASCADE,

    INDEX idx_appointment_date (appointment_date),
    INDEX idx_appointment_status (status),
    INDEX idx_appointment_doctor (doctor_id),
    INDEX idx_appointment_patient (patient_id)
);

-- =====================================================
-- MEDICAL RECORDS TABLE
-- =====================================================

CREATE TABLE medical_records (
    id INT AUTO_INCREMENT PRIMARY KEY,

    appointment_id INT NOT NULL UNIQUE,

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

-- =====================================================
-- PAYMENTS TABLE
-- =====================================================

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,

    appointment_id INT NOT NULL UNIQUE,

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
        ON DELETE CASCADE,

    INDEX idx_payment_status (status)
);

-- =====================================================
-- DEFAULT ADMIN ACCOUNT
-- Email: admin@hospital.com
-- Password: admin123
-- =====================================================

INSERT INTO users (
    name,
    email,
    password_hash,
    role,
    phone
)
SELECT
    'Super Admin',
    'admin@hospital.com',
    'pbkdf2:sha256:600000$placeholder$hash',
    'admin',
    '0000000000'
WHERE NOT EXISTS (
    SELECT 1
    FROM users
    WHERE email = 'admin@hospital.com'
);

-- =====================================================
-- DONE
-- =====================================================
