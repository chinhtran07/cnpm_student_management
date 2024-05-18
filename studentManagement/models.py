from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum, Boolean, DateTime, event, func, \
    UniqueConstraint
from sqlalchemy.orm import relationship, validates
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
    EMPLOYEE = 3


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
    avatar = Column(String(255), default="https://th.bing.com/th/id/R.dbc8e6138b38860cee6899eabc67df45?rik=hZCUMR4xQ%2btlBA&pid=ImgRaw&r=0")
    is_active = Column(Boolean, default=True)


class User(Information, UserMixin):
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(255))
    user_role = Column(Enum(UserRole), default=UserRole.TEACHER)
    is_supervisor = Column(Boolean, nullable=False, default=False)

    admin = relationship('Admin', backref='user', uselist=False)
    teacher = relationship('Teacher', backref='user', uselist=False)
    employee = relationship('Employee', backref='user', uselist=False)


class Student(Information):
    admission_date = Column(DateTime, default=datetime.now())
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
    semester = Column(Enum(Semester),)
    year = Column(String(4))
    teach = relationship('Teach', backref='period', lazy=True)
    scores = relationship('Score', backref='period', lazy=True)
    form_teacher = relationship('FormTeacher', backref='period', uselist=False, lazy=True)
    student_class = relationship('StudentClass', backref='period', lazy=True)

    __table_args__ = (
        UniqueConstraint('semester', 'year', name='unique_semester_year'),
    )

    def __str__(self):
        return f'{"Học kì 1" if self.semester == Semester.SEMESTER_1 else "Học kì 2"} {self.year}'


class Class(Base):
    name = Column(String(10), nullable=False)
    grade = Column(Enum(StudentGrade))
    teach = relationship('Teach', backref='class', lazy=True)
    form_teacher = relationship('FormTeacher', backref='class', uselist=False, lazy=True)
    student_class = relationship('StudentClass', backref='class', lazy=True)

    def __str__(self):
        return self.name


class ScoreDetail(Base):
    score = Column(Float)
    type = Column(Enum(ScoreType))
    created_date = Column(DateTime, default=datetime.now())


class Subject(Base):
    name = Column(String(20))
    grade = Column(Enum(StudentGrade))
    teach = relationship('Teach', backref='subjects', lazy=True)
    exam_15mins = Column(Integer)
    exam_45mins = Column(Integer)


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
    period_id = Column(Integer, ForeignKey(Period.id), nullable=False)


class Policy(Base):
    content = Column(String(255))
    data = Column(Integer)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())


class StudentClass(Base):
    student_id = Column(Integer, ForeignKey(Student.id))
    class_id = Column(Integer, ForeignKey(Class.id))
    period_id = Column(Integer, ForeignKey(Period.id))


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        #
        # import json
        #
        # with open('data/student.json', encoding="utf-8") as f:
        #     students = json.load(f)
        #     for s in students:
        #         stud = Student(first_name=s['first_name'], last_name=s['last_name'], gender=s['gender'],
        #                        address=s['address'],
        #                        phone_number=s['phone_number'], email=s['email'], avatar=s['avatar'])
        #         db.session.add(stud)
        #     db.session.commit()
        #
        import hashlib
        # u = User(first_name='', username='admin1',
        #          password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
        #          user_role=UserRole.ADMIN, is_supervisor=True)
        # db.session.add(u)

        # u2 = User(username='kiet', user_role=UserRole.TEACHER, is_supervisor=False, first_name='Kiet',
        #           last_name='Nguyen',
        #           gender=UserGender.MALE, address='HCM', phone_number='0923740834', email='kiet@gmail.com',
        #           avatar='https://res-console.cloudinary.com/dwdvnztnn/thumbnails/v1/image/upload/v1715050270/c3Vwcl9jYXRfZ3l0eGR5/drilldown',
        #           password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
        #
        # db.session.add(u2)
        # db.session.commit()
        # admin = Admin(user_id=1)
        #
        # teacher = Teacher(qualification="Tiến sĩ", user_id=2)
        # db.session.add_all([admin, teacher])
        # db.session.commit()
        # c1 = Class(name='10A2', grade=StudentGrade.GRADE_10TH)
        # c2 = Class(name='10B1', grade=StudentGrade.GRADE_10TH)
        # c3 = Class(name='10C1', grade=StudentGrade.GRADE_10TH)
        # c4 = Class(name='11A2', grade=StudentGrade.GRADE_11ST)
        # c5 = Class(name='11B3', grade=StudentGrade.GRADE_11ST)
        # c6 = Class(name='11C1', grade=StudentGrade.GRADE_11ST)
        # c7 = Class(name='12A2', grade=StudentGrade.GRADE_12ND)
        # c8 = Class(name='12B3', grade=StudentGrade.GRADE_12ND)
        # c9 = Class(name='12C2', grade=StudentGrade.GRADE_12ND)
        #
        # db.session.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9])
        # db.session.commit()
        #
        #
        # subj1 = Subject(name='Toán 10', grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=1)
        # subj2 = Subject(name='Toán 11', grade=StudentGrade.GRADE_11ST, exam_15mins=2, exam_45mins=1)
        # subj3 = Subject(name='Toán 12', grade=StudentGrade.GRADE_12ND, exam_15mins=2, exam_45mins=1)
        #
        # subj4 = Subject(name='Sinh 10', grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=1)
        # subj5 = Subject(name='Sinh 11', grade=StudentGrade.GRADE_11ST, exam_15mins=2, exam_45mins=1)
        # subj6 = Subject(name='Sinh 12', grade=StudentGrade.GRADE_12ND, exam_15mins=2, exam_45mins=1)
        #
        # subj7 = Subject(name='Văn 10', grade=StudentGrade.GRADE_10TH, exam_15mins=2, exam_45mins=1)
        # subj8 = Subject(name='Văn 11', grade=StudentGrade.GRADE_11ST, exam_15mins=2, exam_45mins=1)
        # subj9 = Subject(name='Văn 12', grade=StudentGrade.GRADE_12ND, exam_15mins=2, exam_45mins=1)
        # db.session.add_all([subj1, subj2, subj3, subj4, subj5, subj6, subj7, subj8, subj9])
        # db.session.commit()
        #
        # p1 = Period(semester=Semester.SEMESTER_1, year='2024')
        # p2 = Period(semester=Semester.SEMESTER_2, year='2024')
        # db.session.add_all([p1,p2])
        # db.session.commit()
        #
        # ft = FormTeacher(teacher_id=1, class_id=1, period_id=1)
        # ft1 = FormTeacher(teacher_id=1, class_id=1, period_id=2)
        # db.session.add_all([ft, ft1])
        # db.session.commit()
        #
        # #thêm học sinh vào lớp
        # sc = StudentClass(student_id=3, class_id=1)
        # sc1 = StudentClass(student_id=4, class_id=1)
        # sc2 = StudentClass(student_id=5, class_id=1)
        # sc3 = StudentClass(student_id=6, class_id=1)
        # sc4 = StudentClass(student_id=7, class_id=1)
        # sc5 = StudentClass(student_id=8, class_id=1)
        # sc6 = StudentClass(student_id=9, class_id=1)
        # sc7 = StudentClass(student_id=10, class_id=1)
        # sc8 = StudentClass(student_id=11, class_id=1)
        # sc9 = StudentClass(student_id=12, class_id=1)
        # #
        # db.session.add_all([sc, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8, sc9])
        # db.session.commit()
        #
        # sc = StudentClass(student_id=13, class_id=2)
        # sc1 = StudentClass(student_id=14, class_id=2)
        # sc2 = StudentClass(student_id=15, class_id=2)
        # sc3 = StudentClass(student_id=16, class_id=2)
        # sc4 = StudentClass(student_id=17, class_id=2)
        # sc5 = StudentClass(student_id=18, class_id=2)
        # sc6 = StudentClass(student_id=19, class_id=2)
        # sc7 = StudentClass(student_id=20, class_id=2)
        # sc8 = StudentClass(student_id=21, class_id=2)
        # sc9 = StudentClass(student_id=22, class_id=2)
        #
        # db.session.add_all([sc, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8, sc9])
        # db.session.commit()
        #
        # #thêm dữ liệu lớp teach
        # t = Teach(teacher_id=1, subject_id=1, class_id=1, period_id=1)
        # t1 = Teach(teacher_id=1, subject_id=1, class_id=1, period_id=2)
        # t2 = Teach(teacher_id=1, subject_id=1, class_id=4, period_id=1)
        # t3 = Teach(teacher_id=1, subject_id=1, class_id=4, period_id=2)
        # db.session.add_all([t, t1, t2, t3])
        # db.session.commit()

        # db.session.commit()


