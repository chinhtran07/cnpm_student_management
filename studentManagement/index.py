import pdb

from flask import render_template, request, redirect, session
from flask_login import login_user, current_user, logout_user, login_required

from studentManagement import app, dao, login
from studentManagement.decorators import logged_in


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template("index.html")
    return redirect("/login")


@app.route("/login", methods=['get', 'post'])
@logged_in
def login_my_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

            next = request.args.get('next')
            url = "/" + role
            return redirect(next if next else url)
        else:
            err_msg = 'Username hoặc password không đúng!'

    return render_template('login.html', err_msg=err_msg)


@app.route("/admin-login", methods=['post'])
def process_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password)
    if u:
        login_user(user=u)

    return redirect('/admin')


@app.route('/logout', methods=['get'])
def logout_my_user():
    logout_user()
    return redirect("/login")


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/employee')
def employee():
    return render_template("index.html")


@app.route('/teacher')
def teacher():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        from studentManagement import admin
        dao.init_policy()
        app.run(debug=True)
