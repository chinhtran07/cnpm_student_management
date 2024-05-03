from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from studentManagement import db, app
from flask_login import UserMixin
from enum import Enum as AttrEnum
from datetime import datetime


class UserGender(AttrEnum):
    MALE = 1
    FEMALE = 2


class UserRole(AttrEnum):
    ADMIN = 1
    TEACHER = 2
    STAFF = 3


class StudentGrade(AttrEnum):
    GRADE_10TH = 1
    GRADE_11ST = 2
    GRADE_12ND = 3


class ScoreType(AttrEnum):
    EXAM_15MINS = 1
    EXAM_45MINS = 2
    EXAM_FINAL = 3


class Semester(AttrEnum):
    SEMESTER_1 = 1
    SEMESTER_2 = 2


class Base(db.Model):

    __abstract__ = True
    id = Column(Integer, autoincrement=True, primary_key=True)


class Information(Base):

    __abstract__ = True

    first_name = Column(String(20))
    last_name = Column(String(50))
    gender = Column(Enum(UserGender))
    dob = Column(DateTime)
    address = Column(String(100))
    phone_number = Column(String(11))
    email = Column(String(30), unique=True)
    avatar = Column(String(255))
    is_active = Column(Boolean, default=True)


class User(Information, UserMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(255))
    user_role = Column(Enum(UserRole), default=UserRole.TEACHER)
    is_supervisor = Column(Boolean, nullable=False, default=False)

    admin = relationship('Admin', backref='user', uselist=False)
    teacher = relationship('Teacher', backref='user', uselist=False)
    employee = relationship('Employee', backref='user', uselist=False)


class Student(Information):
    admission_date = Column(DateTime)

    student_class = relationship('StudentClass', backref='student', lazy=True)


class Admin(Base):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)


class Teacher(Base):
    qualification = Column(String(20))

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)

    teach = relationship('Teach', backref='teacher', lazy=True)
    form_teacher = relationship('FormTeacher', backref='teacher', uselist=False, lazy=True)


class Employee(Base):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)


class Period(Base):
    semester = Column(Enum(Semester))
    year = Column(String(4))
    teach = relationship('Teach', backref='period', lazy=True)
    form_teacher = relationship('FormTeacher', backref='period', uselist=False, lazy=True)
    student_class = relationship('StudentClass', backref='period', lazy=True)


class Class(Base):
    name = Column(String(10), nullable=False)
    grade = Column(Enum(StudentGrade))
    teach = relationship('Teach', backref='class', lazy=True)
    form_teacher = relationship('FormTeacher', backref='class', uselist=False, lazy=True)
    student_class = relationship('StudentClass', backref='class', lazy=True)


class ScoreDetail(Base):
    score = Column(Float)
    type = Column(Enum(ScoreType))
    created_date = Column(DateTime)


class Subject(Base):
    name = Column(String(20))
    teach = relationship('Teach', backref='subjects', lazy=True)


class Teach(Base):
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    period_id = Column(Integer, ForeignKey(Period.id), nullable=False)


class FormTeacher(Base):
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    period_id = Column(Integer, ForeignKey(Period.id), nullable=False)


class Score(Base):
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    score_detail_id = Column(Integer, ForeignKey(ScoreDetail.id), nullable=False)


class Policy(Base):
    content = Column(String(255))
    data = Column(Integer)
    created_date = Column(DateTime)
    updated_date = Column(DateTime)


class StudentClass(Base):

    student_id = Column(Integer, ForeignKey(Student.id))
    class_id = Column(Integer, ForeignKey(Class.id))
    period_id = Column(Integer, ForeignKey(Period.id), nullable=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        import hashlib
        u = User(first_name='admin', username='admin',
                 password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                 user_role=UserRole.ADMIN, is_supervisor=True)
        db.session.add(u)
        db.session.commit()
