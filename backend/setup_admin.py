"""
Run this script once after importing schema.sql
to set the admin password.

Usage: python setup_admin.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

from werkzeug.security import generate_password_hash
import pymysql

ADMIN_EMAIL    = "admin@hospital.com"
ADMIN_NAME     = "Super Admin"
ADMIN_PASSWORD = input("Enter admin password: ").strip()

if len(ADMIN_PASSWORD) < 6:
    print("Password too short (min 6 chars)")
    exit(1)

hashed = generate_password_hash(ADMIN_PASSWORD)

conn = pymysql.connect(
    host=os.environ.get('MYSQL_HOST', 'localhost'),
    port=int(os.environ.get('MYSQL_PORT', 3306)),
    user=os.environ.get('MYSQL_USER', 'root'),
    password=os.environ.get('MYSQL_PASSWORD', ''),
    database=os.environ.get('MYSQL_DATABASE', 'hospital_db'),
)
cur = conn.cursor()
cur.execute("SELECT id FROM users WHERE email=%s AND role='admin'", (ADMIN_EMAIL,))
existing = cur.fetchone()

if existing:
    cur.execute("UPDATE users SET password_hash=%s WHERE email=%s", (hashed, ADMIN_EMAIL))
    conn.commit()
    print(f"✅ Admin password updated for {ADMIN_EMAIL}")
else:
    cur.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (%s,%s,%s,'admin')",
        (ADMIN_NAME, ADMIN_EMAIL, hashed)
    )
    conn.commit()
    print(f"✅ Admin account created: {ADMIN_EMAIL}")

conn.close()
