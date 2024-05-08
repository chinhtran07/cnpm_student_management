import hashlib
from datetime import datetime

from sqlalchemy import desc, func, select

from studentManagement import db, app
from studentManagement.models import User, Student, Period, StudentClass, Policy, Class, Semester, Teach, Teacher



def get_period(semester, year):
    return db.session.query(Period).filter_by(semester=semester, year=year).first()


def stats_amount_of_students_by_period(semester=Semester.SEMESTER_1, year=datetime.now().year):
    period = get_period(semester, year)
    query = (db.session.query(Class.name, func.count(StudentClass.student_id))
             .join(StudentClass)
             .filter(StudentClass.period_id == period.id)
             .group_by(Class.name)
             )

    return query.all()


def get_user_by_id(id):
    return User.query.get(id)


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()


def auth_user(username, password, role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(role)).first()


def init_policy():
    existing_policies = Policy.query.all()
    if existing_policies:
        return

    # Create default policies
    default_policies = [
        {"content": "Số tuổi tối thiểu nhập học", "data": 15},
        {"content": "Số tuổi tối đa nhập học", "data": 20},
        {"content": "Sĩ số tối đa của 1 lớp", "data": 40},
        # Add more default policies as needed
    ]

    # Insert default policies into the database
    for policy_data in default_policies:
        policy = Policy(**policy_data)
        db.session.add(policy)

    # Commit changes to the database
    db.session.commit()


########### Teacher function

# lấy danh sách lớp
def load_class(grade=None, page=None, class_name=None):
    query = Class.query

    if grade:
        if grade == "10":
            query = query.filter(Class.grade.__eq__('GRADE_10TH')).order_by('name')
        elif grade == "11":
            query = query.filter(Class.grade.__eq__('GRADE_11ST')).order_by('name')
        else:
            query = query.filter(Class.grade.__eq__('GRADE_12ND')).order_by('name')

    if page:
        page_size = 4
        start = (int(page) - 1) * page_size
        return query.order_by('name').slice(start, start + page_size).all()

    if class_name:
        query = query.filter(Class.name.contains(class_name))

    return query.order_by('name').all()


# đếm số lớp
def count_class():
    return Class.query.count()


# đếm tổng số học sinh của 1 lớp
def count_total(class_id=None):
    counter = StudentClass.query

    if class_id:
        counter = counter.filter(StudentClass.class_id.__eq__(class_id))

    return counter.count()


# lấy danh sách học sinh của một lớp
def get_list_student(class_id=None):
    query = StudentClass.query.join(Student, StudentClass.student_id == Student.id).add_columns(Student.first_name,
                                                                                                Student.id,
                                                                                                Student.last_name,
                                                                                                Student.gender,
                                                                                                Student.address)

    if class_id:
        query = query.filter(StudentClass.class_id.__eq__(class_id))

    return query.all()


# Lấy id những lớp có dạy
def get_teach_class(teacher_id=None):
    query = Teach.query.join(Period, Teach.period_id == Period.id).add_columns(Period.semester)

    if teacher_id:
        query = query.filter(Teach.teacher_id.__eq__(teacher_id))

    return query.all()


# get teacher by user_id
def get_teacher_id(user_id=None):
    query = Teacher.query
    if user_id:
        query = query.filter(Teacher.user_id.__eq__(user_id))
    return query.all()


if __name__ == '__main__':
    with app.app_context():
        test = get_teacher_id(user_id=3)
        for t in test:
            print(t.id)
