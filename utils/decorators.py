from functools import wraps
from flask import session, redirect

def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return redirect('/login')
            return f(*args, **kwargs)
        return decorated
    return wrapper
