from flask import Blueprint, render_template, request, redirect, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return redirect('/login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = {
            "name": request.form['name'],
            "email": request.form['email'],
            "password": generate_password_hash(request.form['password']),
            "role": "patient"
        }
        current_app.db.users.insert_one(user)
        return redirect('/login')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = current_app.db.users.find_one({"email": request.form['email']})

        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect('/admin')
            elif user['role'] == 'doctor':
                return redirect('/doctor')
            else:
                return redirect('/patient')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
