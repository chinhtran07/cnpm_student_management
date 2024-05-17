import hashlib

from sqlalchemy import desc

from studentManagement import db
from studentManagement.models import *


def get_most_recent_period():
    return Period.query.order_by(desc(Period.id)).first()


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


########Staff function

def add_student_info(first_name, last_name, gender, dob, address, phone_number, avatar):
    new_student = Information(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        dob=dob,
        address=address,
        phone_number=phone_number,
        avatar=avatar
    )
    db.session.add(new_student)
    db.session.commit()


def get_student():
    total_student = Student.query.count()
    return total_student


def get_student_info(phone_number):
    return Information.query.filter_by(phone_number=phone_number).first()

def get_subject():
    all_subject = Subject.query.all()
    return all_subject