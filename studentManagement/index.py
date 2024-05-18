import random

from flask import redirect, request, render_template, session, jsonify, make_response
from flask_login import login_user, current_user, logout_user
import math
import pdb
from studentManagement import app, dao, login
#from weasyprint import HTML

from studentManagement.ClassroomForm import ClassroomForm, StudentForm
from studentManagement.models import Class, Student


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


##############################Employee
@app.route('/employee')
def employee():
    return render_template("employee/employee.html")


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
def show_classrooms():
    grade = request.args.get('grade')
    period_id = request.args.get('period_id')
    classrooms = dao.load_class(grade, period_id)
    # Thêm thông tin số lượng học sinh vào mỗi lớp học
    for classroom in classrooms:
        classroom.student_count = dao.count_total(class_id=classroom.id)
    periods = dao.load_periods()
    return render_template('/employee/classrooms.html', classrooms=classrooms, periods=periods)


@app.route('/employee/classroom_form/', methods=['POST'])
def add_or_update_classroom():
    form = ClassroomForm()
    # Load danh sách học sinh vào SelectMultipleField students
    form.students.choices = [(student.id, student.name) for student in dao.get_all_student_info()]
    # Load danh sách giáo viên vào SelectMultipleField teachers
    form.teachers.choices = [(teacher.id, teacher.name) for teacher in dao.get_all_teachers_info()]

    if request.method == 'POST' and form.validate():
        # Gọi hàm create_or_update_classroom với dữ liệu từ form
        dao.create_or_update_classroom(name=form.name.data,
                                       student_ids=form.students.data,
                                       teacher_ids=form.teachers.data)
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


# ****************


@app.route('/teacher', methods=['get', 'post'])
def teacher():
    grade = request.args.get('grade')
    page = request.args.get("page")
    class_name = request.args.get('class_name')

    classes = dao.load_class(grade=grade, page=page, class_name=class_name)
    total_class = dao.count_class()

    teach_class = dao.get_teach_class(teacher_id=dao.get_teacher_id(current_user.id).id)
    teach_subject = dao.get_teach_subject(teacher_id=dao.get_teacher_id(current_user.id).id)

    return render_template('teacher/teacher.html', classes=classes,
                           pages=math.ceil(total_class / 4), teach_class=teach_class, teach_subject=teach_subject)


@app.route('/teacher/score_management')
def score_management():
    class_name = request.args.get('class_name')

    teach_class = dao.get_teach_class(teacher_id=dao.get_teacher_id(current_user.id).id, class_name=class_name)

    return render_template('teacher/score_management.html', teach_class=teach_class)


@app.route('/teacher/list_student')
def list_student():
    class_id = request.args.get('class_id')

    students1 = dao.get_list_student(class_id=class_id, period_id=1)
    students2 = dao.get_list_student(class_id=class_id, period_id=2)

    return render_template('teacher/list_student.html', students1=students1, students2=students2)


@app.route('/teacher/score_input')
def score_input():
    class_obj = dao.load_class(class_id=request.args.get('class_id'))
    subject = dao.get_subject_by_subject_id(subject_id=request.args.get('subject_id'))
    period = dao.get_period_by_id(period_id=request.args.get('period'))
    students = dao.get_list_student(class_id=class_obj.id, period_id=request.args.get('period'))

    scores = dao.get_score(period_id=period.id, class_id=class_obj.id, subject_id=subject.id)

    return render_template(template_name_or_list='teacher/score_input.html', class_obj=class_obj,
                           subject=subject, period=period, students=students, scores=scores)


@app.route('/teacher/score_table')
def score_table():
    class_obj = dao.load_class(class_id=request.args.get('class_id'))
    subject = dao.get_subject_by_subject_id(subject_id=request.args.get('subject_id'))
    period = dao.get_period_by_id(period_id=request.args.get('period'))
    students = dao.get_list_student(class_id=class_obj.id, period_id=request.args.get('period'))

    scores = dao.get_score(period_id=period.id, class_id=class_obj.id, subject_id=subject.id)
    total_score = dao.count_scores(subject_id=subject.id, class_id=class_obj.id, period_id=period.id)
    total_score_input = dao.count_total(class_id=class_obj.id, period_id=period.id) * (
            subject.exam_15mins + subject.exam_45mins + 1)
    list_avr = []
    if total_score >= total_score_input:
        for student in students:
            list_avr.append(
                dao.get_average_scores(student_id=student.id, subject_id=subject.id, period_id=period.id,
                                       class_id=class_obj.id))
    return render_template(template_name_or_list='teacher/score_table.html', class_obj=class_obj,
                           subject=subject, period=period, students=students, scores=scores, total_score=total_score,
                           total_score_input=total_score_input, list_avr=list_avr)


@app.route('/api/teacher/scores', methods=['post'])
def add_to_scores():
    scores = session.get('scores')
    if not scores:  # nếu ko có cái giỏ thì tạo cái giỏ rỗng
        scores = {}


    id = str(random.randint(0, 100))

    sd_id = request.json.get('student_id')
    sd_scr = request.json.get("score")
    scr_type = request.json.get("type")

    class_id = request.json.get('class_id')
    subject_id = request.json.get('subject_id')
    period_id = request.json.get('period_id')

    subject = dao.get_subject_by_subject_id(subject_id=subject_id)

    counter = dao.count_scores(student_id=sd_id, class_id=class_id, subject_id=subject_id, score_type=scr_type,
                               period_id=period_id)
    counter_sess = dao.count_scores_in_session(scores, type=scr_type, student_id=sd_id)
    print(counter)
    print(counter_sess)
    if scr_type == 'ScoreType.EXAM_15MINS':

        if counter + counter_sess >= subject.exam_15mins:
            return jsonify({'id': 1, 'message': "Đã đủ điểm cột 15 phút", 'status': 500})

    elif scr_type == 'ScoreType.EXAM_45MINS':

        if counter + counter_sess >= subject.exam_45mins:
            return jsonify({'id': 2, 'message': "Đã đủ điểm cột 45 phút", 'status': 500})

    elif scr_type == 'ScoreType.EXAM_FINAL':

        if counter + counter_sess >= 1:
            return jsonify({'id': 3, 'message': "Đã đủ điểm cột điểm thi", 'status': 500})

    scores[id] = {
        "student_id": sd_id,
        "score": sd_scr,
        "type": scr_type,
    }
    session['scores'] = scores

    print("session['scores'] ")
    print(session['scores'])
    return jsonify({'id': 4, 'message': "Thêm thành công", 'status': 200})


@app.route('/api/teacher/save_scores', methods=['post'])
def save_scores():
    subject_id = request.args.get('subject_id')
    period_id = request.args.get('period_id')
    scores = session.get('scores')
    if scores:
        try:
            dao.create_score(scores=scores, subject_id=subject_id, period_id=period_id)
        except Exception as ex:
            print(ex)
            del session['scores']
            return jsonify({'status': 500})
        else:
            del session['scores']
            return jsonify({'status': 200})

    return jsonify({'status': 500})


# Update score function
@app.route('/api/teacher/update_score/<score_id>', methods=['put'])
def update_score(score_id):
    value = request.json['value']
    try:
        dao.update_score(score_id=score_id, value=value)
    except Exception as ex:
        print(ex)
        return jsonify({'status': 500})
    return jsonify({'status': 200})


# Export pdf
@app.route('/teacher/download_pdf', methods=['post'])
def download_pdf():
    class_obj = dao.load_class(class_id=request.json.get('class_id'))
    subject = dao.get_subject_by_subject_id(subject_id=request.json.get('subject_id'))
    period = dao.get_period_by_id(period_id=request.json.get('period_id'))
    students = dao.get_list_student(class_id=class_obj.id, period_id=request.args.get('period'))
    scores = dao.get_score(period_id=period.id, class_id=class_obj.id, subject_id=subject.id)
    total_score = dao.count_scores(subject_id=subject.id, class_id=class_obj.id, period_id=period.id)
    total_score_input = dao.count_total(class_id=class_obj.id) * (
            subject.exam_15mins + subject.exam_45mins + 1)
    list_avr = []
    if total_score >= total_score_input:
        for student in students:
            list_avr.append(
                dao.get_average_scores(student_id=student.id, subject_id=subject.id, period_id=period.id,
                                       class_id=class_obj.id))

    rendered_html = render_template(template_name_or_list='teacher/score_table.html', class_obj=class_obj,
                                    subject=subject, period=period, students=students, scores=scores,
                                    total_score=total_score,
                                    total_score_input=total_score_input, list_avr=list_avr)

    # Tạo PDF từ HTML

    pdf = HTML(string=rendered_html).write_pdf()

    # Tạo response cho file PDF
    response = make_response(pdf)
    print(response)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=bangDiem.pdf'
    print(response.headers)
    return response


# teacher process



if __name__ == '__main__':
    with app.app_context():
        from studentManagement import admin

        dao.init_policy()
        app.run(debug=True)
