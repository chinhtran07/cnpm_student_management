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
    total_student = dao.get_student()
    return render_template("employee/employee.html", total_student=total_student)


@app.route('/employee/adjust_regulations')
def adjust_regulations():
    return render_template('employee/adjust_regulations.html')


@app.route('/employee/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        dob = request.form['dob']
        address = request.form['address']
        phone_number = request.form['phone_number']
        avatar = request.form['avatar']

        dao.add_student_info(first_name, last_name, gender, dob, address, phone_number, avatar)
        student_info = dao.get_student_info(phone_number)
        return render_template('employee/student_info.html', student_info=student_info)
    else:
        return render_template('employee/student_form.html')


@app.route('/teacher')
def teacher():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        from studentManagement import admin

        dao.init_policy()
        app.run(debug=True)
