import hashlib

from sqlalchemy import desc

from studentManagement import db
from studentManagement.models import *

import datetime


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


def get_all_student_info():
    return [{'id': student.id, 'name': student.last_name + ' ' + student.first_name,
             'gender': student.gender.name, 'admission_date': student.admission_date if student.admission_date else '',
             'dob': student.dob if student.dob else ''} for student in Student.query.all()]


def get_student_by_id(id):
    return Student.query.get(id)


def create_or_update_student(id, first_name, last_name, gender, admission_date, dob, address, email, phone_number,
                             is_active):
    #try:
        if id:
            (Student.query.filter_by(id=id).update({
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'admission_date': admission_date,
                'dob': dob,
                'address': address,
                'email': email,
                'phone_number': phone_number,
                'is_active': is_active
            }))
        else:
            db.session.add(Student(first_name=first_name, last_name=last_name, gender=gender,
                                   admission_date=admission_date, dob=dob, address=address,
                                   email=email, phone_number=phone_number, is_active=is_active))

        db.session.commit()

    #   student_age = datetime.now().year - dob.year
    #     if 15 <= student_age <= 20:
    #         db.session.commit()
    #     else:
    #         db.session.rollback()
    #
    # except Exception as e:
    #     db.session.rollback()
    #     return "Lỗi" + str(e)
    # return None


def delete_student(id):
    Student.query.filter_by(id=id).delete()
    db.session.commit()


def get_subject():
    all_subject = Subject.query.all()
    return all_subject


def get_all_classroom_info():
    return [{'id': c.id, 'name': c.name,
             'student_count': db.session.query(func.count(Student.id))
             .join(StudentClass)
             .filter(StudentClass.class_id == c.id).scalar()}
            for c in Class.query.all()]


def get_classroom_by_id(id):
    return Class.query.get(id)


# def delete_classroom(id):
#     Class.query.filter_by(id=id).delete()
#     db.session.commit()

def delete_classroom(id):
    try:
        # Xóa các tham chiếu từ bảng Teach và FormTeacher
        Teach.query.filter_by(class_id=id).delete()
        FormTeacher.query.filter_by(class_id=id).delete()

        # Xóa lớp
        class_to_delete = Class.query.get(id)
        db.session.delete(class_to_delete)
        db.session.commit()
        print("Classroom deleted successfully.")
    except Exception as e:
        db.session.rollback()
        print("Error:", e)


def create_or_update_classroom(id, name, list_student_id):
    if id:
        classroom = Class.query.get(id)
    else:
        classroom = Class()

    student_class_list = [StudentClass(student_id=student_id,
                                       class_id=classroom.id)
                          for student_id in list_student_id]
    classroom.student_class = student_class_list

    classroom.name = name
    if not id:
        db.session.add(classroom)
    db.session.commit()
