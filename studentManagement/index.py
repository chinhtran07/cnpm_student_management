import math
import pdb

from flask import render_template, request, redirect, session
from flask_login import login_user, current_user, logout_user, login_required

from studentManagement import app, dao, login
from studentManagement.decorators import logged_in
from studentManagement.models import UserRole


@app.route('/')
def index():
    return redirect("/login")


@app.route("/login", methods=['get', 'post'])
@logged_in
def login_my_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user = dao.auth_user(username=username, password=password, role=role)
        if user:
            login_user(user)

            next = request.args.get('next')
            url = "/" + role.lower()
            return redirect(next if next else url)
        else:
            err_msg = 'Username hoặc password không đúng!'

    return render_template('login.html', err_msg=err_msg)


@app.route("/admin-login", methods=['post'])
def process_admin_login():
    err_msg = ''
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
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
    grade = request.args.get('grade')
    page = request.args.get("page")
    class_name = request.args.get('class_name')

    classes = dao.load_class(grade=grade, page=page, class_name=class_name)
    total_class = dao.count_class()

    teacher = dao.get_teacher_id(current_user.id)
    for t in teacher:
        id = t.id
        teach_class = dao.get_teach_class(teacher_id=id)

    return render_template('teacher.html', classes=classes,
                           pages=math.ceil(total_class / 4), teach_class=teach_class)


@app.route('/teacher/scoreManagement')
def score_management():
    return render_template('scoreManagement.html')


@app.route('/teacher/list_student')
def list_student():
    class_id = request.args.get('class_id')

    students = dao.get_list_student(class_id=class_id)

    return render_template('listStudent.html', students=students)


if __name__ == '__main__':
    with app.app_context():
        from studentManagement import admin

        dao.init_policy()
        app.run(debug=True)
