import pdb
from functools import wraps
from flask import request, redirect, url_for
from flask_login import current_user


def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            next = request.url
            pdb.set_trace()
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function

