from flask import render_template, request, redirect
from flask_login import login_user, current_user, logout_user
import math
import pdb


from studentManagement import app, dao, login
from studentManagement.decorators import logged_in
from studentManagement.models import UserRole


@app.route('/')
def index():
    return redirect("/login")


@app.route("/login", methods=['get', 'post'])
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
            err_msg = 'Tài khoản hoặc mật khẩu không đúng!'

    return render_template('login.html', err_msg=err_msg)


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
        return render_template('employee/add_student.html')


@app.route('/employee/subject_managements')
def get_subject():
    return render_template('employee/subject_managements.html', subjects=dao.get_subject())


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
