import hashlib
from datetime import datetime

from sqlalchemy import desc, func

from studentManagement import db
from studentManagement.models import User, Student, Period, StudentClass, Policy, Class, Semester


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

    
def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


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
