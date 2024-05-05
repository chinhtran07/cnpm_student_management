import pdb

from flask import render_template, request, redirect, session
from flask_login import login_user

from studentManagement import app, dao, login


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/admin-login", methods=['post'])
def process_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password)
    if u:
        login_user(user=u)

    return redirect('/admin')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        from studentManagement import admin
        app.run(debug=True)
