from flask import render_template, request, redirect
from flask_login import login_user, current_user, logout_user

from studentManagement import app, dao, login
from studentManagement.decorators import logged_in
from studentManagement.forms import StudentForm, ClassroomForm
from studentManagement.models import Student, Class


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


@app.route('/employee/students/', methods=['GET'])
def student_list():
    students = dao.get_all_student_info()
    return render_template('/employee/students.html', students=students)


@app.route('/employee/students/', methods=['POST'])
def add_or_update_student():
    form = StudentForm()
    if form.validate_on_submit():
        dao.create_or_update_student(id=form.id.data, first_name=form.first_name.data, last_name=form.last_name.data,
                                     gender=form.gender.data, admission_date=form.admission_date.data,
                                     dob=form.dob.data,
                                     address=form.address.data, email=form.email.data,
                                     phone_number=form.phone_number.data,
                                     is_active=form.is_active.data)

        return redirect('/employee/students')


@app.route('/employee/students/<int:id>', methods=['GET'])
def update_student(id):
    student = dao.get_student_by_id(id)
    form = StudentForm(obj=student)
    return render_template('employee/student_form.html', form=form)


@app.route('/employee/students/create', methods=['GET'])
def create_student():
    student = Student()
    form = StudentForm(request.form, obj=student)
    return render_template('employee/student_form.html', form=form)


@app.route('/employee/students/delete/<int:id>')
def delete_student(id):
    dao.delete_student(id)
    return redirect('/employee/students')


# ****************
@app.route('/employee/classrooms/', methods=['GET'])
def classroom_list():
    classrooms = dao.get_all_classroom_info()
    return render_template('/employee/classrooms.html', classrooms=classrooms)


@app.route('/employee/classrooms/', methods=['POST'])
def add_or_update_classroom():
    form = ClassroomForm()
    form.students.choices = [(s['id'], s['name']) for s in dao.get_all_student_info()]
    if form.validate_on_submit():
        dao.create_or_update_classroom(id=form.id.data, name=form.name.data,
                                       list_student_id=form.students.data)

        return redirect('/employee/classrooms')


@app.route('/employee/classrooms/<int:id>', methods=['GET'])
def update_classroom(id):
    classroom = dao.get_classroom_by_id(id)
    form = ClassroomForm(obj=classroom)
    form.students.choices = [(s['id'], s['name']) for s in dao.get_all_student_info()]
    form.students.data = [s.student_id for s in classroom.student_class]
    return render_template('employee/classroom_form.html', form=form)


@app.route('/employee/classrooms/create', methods=['GET'])
def create_classroom():
    classroom = Class()
    form = ClassroomForm(request.form, obj=classroom)
    return render_template('employee/classroom_form.html', form=form)


@app.route('/employee/classrooms/delete/<int:id>')
def delete_classroom(id):
    dao.delete_classroom(id)
    return redirect('/employee/classrooms')

@app.route('/teacher')
def teacher():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        dao.init_policy()
        app.run(debug=True)
        # app.run()
