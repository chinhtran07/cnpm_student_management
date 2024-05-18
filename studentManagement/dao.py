import hashlib
import pdb
from datetime import datetime

from sqlalchemy import desc, func, select, case
from sqlalchemy.orm import aliased


from studentManagement import db, app
from studentManagement.models import User, Student, Period, StudentClass, Policy, Class, Semester, Teach, Teacher, \
    Subject, Score, ScoreDetail, ScoreType, Information


def get_period(semester, year):
    return db.session.query(Period).filter_by(semester=semester, year=year).first()


def stats_amount_of_students_by_period(semester=Semester.SEMESTER_1.name, year=datetime.now().year.__str__()):
    period = get_period(semester, year)
    if period:
        query = (db.session.query(Class.name, func.count(StudentClass.student_id))
                 .join(StudentClass)
                 .filter(StudentClass.period_id == period.id)
                 .group_by(Class.name)
                 )
        return query.all()
    else:
        return []


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
########### Teacher function
# lấy danh sách lớp
def load_class(grade=None, page=None, class_name=None, class_id=None):
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
    if class_id:
        return query.filter(Class.id.__eq__(class_id)).first()

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
                                                                                                Student.address,
                                                                                                )

    if class_id:
        query = query.filter(StudentClass.class_id.__eq__(class_id))

    return query.all()


# Lấy  những lớp có dạy
def get_teach_class(teacher_id=None, class_name=None):
    query = (Teach.query.join(Period, Teach.period_id == Period.id).
             join(Class, Teach.class_id == Class.id).
             join(Subject, Teach.subject_id == Subject.id).
             add_columns(Period.semester, Period.year, Class.name, Class.id, Subject.name, Subject.id, Period.id, ))

    if teacher_id:
        query = query.filter(Teach.teacher_id.__eq__(teacher_id))

    if class_name:
        query = query.filter(Class.name.contains(class_name))

    query = query.filter(Period.year.__eq__(datetime.now().year))

    return query.order_by('name').all()


# get teacher by user_id
def get_teacher_id(user_id=None):
    query = Teacher.query
    if user_id:
        query = query.filter(Teacher.user_id.__eq__(user_id))
    return query.one()


# get Subject by subject_id
def get_subject(subject_id=None):
    query = Subject.query
    if subject_id:
        query = query.filter(Subject.id.__eq__(subject_id))

    return query.first()


# get Period by period_id
def get_period(period_id=None):
    query = Period.query
    if period_id:
        query = query.filter(Period.id.__eq__(period_id))
    return query.first()


# Hàm chuyển đổi từ chuỗi sang enum
def str_to_enum(s):
    if s == 'ScoreType.EXAM_15MINS':
        return ScoreType.EXAM_15MINS
    elif s == 'ScoreType.EXAM_45MINS':
        return ScoreType.EXAM_45MINS
    elif s == 'ScoreType.EXAM_FINAL':
        return ScoreType.EXAM_FINAL
    else:
        raise ValueError(f"Invalid ScoreType: {s}")


# lấy điểm theo subject_id, period_id, class_id
def get_score(student_id=None, subject_id=None, period_id=None, class_id=None, score_type=None):
    query = (Score.query.join(ScoreDetail, Score.score_detail_id == ScoreDetail.id).
             join(StudentClass, Score.student_id == StudentClass.student_id).
             add_columns(ScoreDetail.score, ScoreDetail.type, Score.student_id, ScoreDetail.id))

    if student_id:
        query = query.filter(Score.student_id.__eq__(student_id))
    if subject_id:
        query = query.filter(Score.subject_id.__eq__(subject_id))
    if period_id:
        query = query.filter(Score.period_id.__eq__(period_id))
    if class_id:
        query = query.filter(StudentClass.class_id.__eq__(class_id))
    if score_type:
        query = query.filter(ScoreDetail.type.__eq__(str_to_enum(score_type)))

    return query.order_by('type', 'student_id').all()


def get_id_score_detail(scores):
    listId = []

    for s in scores.values():
        sd = ScoreDetail(score=s['score'], type=str_to_enum(s['type']))
        db.session.add(sd)
        db.session.commit()
        listId.append(sd.id)

    return listId


def create_score(scores, subject_id, period_id):
    sd_id = get_id_score_detail(scores=scores)

    if scores:
        for i, s in enumerate(scores.values()):
            score = Score(student_id=s['student_id'], subject_id=subject_id, score_detail_id=sd_id[i],
                          period_id=period_id)
            db.session.add(score)
            db.session.commit()


def count_scores(student_id=None, subject_id=None, period_id=None, class_id=None, score_type=None):
    query = (Score.query.join(StudentClass, Score.student_id == StudentClass.student_id).
             join(ScoreDetail, Score.score_detail_id == ScoreDetail.id))

    if student_id:
        query = query.filter(Score.student_id.__eq__(student_id))
    if subject_id:
        query = query.filter(Score.subject_id.__eq__(subject_id))
    if class_id:
        query = query.filter(StudentClass.class_id.__eq__(class_id))
    if period_id:
        query = query.filter(Score.period_id.__eq__(period_id))
    if score_type:
        query = query.filter(ScoreDetail.type.__eq__(str_to_enum(score_type)))

    return query.count()


def count_scores_in_session(scores, type, student_id):
    count = 0
    if scores:
        for i in scores.values():
            if i['type'] == type and i['student_id'] == student_id:
                count = count + 1
    return count


def get_average_scores(student_id=None, subject_id=None, period_id=None, class_id=None):
    avr_scr = 0
    count = 0

    score15 = get_score(student_id=student_id, subject_id=subject_id, period_id=period_id, class_id=class_id,
                        score_type='ScoreType.EXAM_15MINS')
    score45 = get_score(student_id=student_id, subject_id=subject_id, period_id=period_id, class_id=class_id,
                        score_type='ScoreType.EXAM_45MINS')
    score_final = get_score(student_id=student_id, subject_id=subject_id, period_id=period_id, class_id=class_id,
                            score_type='ScoreType.EXAM_FINAL')

    for s in score15:
        avr_scr = avr_scr + s[1]
        count = count + 1
    for s in score45:
        avr_scr = avr_scr + (s[1] * 2)
        count = count + 2
    for s in score_final:
        avr_scr = avr_scr + (s[1] * 2)
        count = count + 2

    return avr_scr / count


def get_teach_subject(teacher_id):
    query = Subject.query.join(Teach, Teach.subject_id == Subject.id).filter(Teach.teacher_id.__eq__(teacher_id))
    return query.all()


def update_score (score_id, value = None):
    query = ScoreDetail.query.get(score_id)

    if value:
        query.score = value

    db.session.commit()


def get_subjects():
    return db.session.query(Subject).all()


def get_years():
    query = db.session.query(Period.year).all()
    years = {year[0] for year in query}
    return years


def count_students_of_classes_by_subject_and_period(subject_id, semester, year, avg_gt_or_equal_to=None):
    period = get_period(semester=semester, year=year)
    if not period:
        return []

    StudentAlias = aliased(Student)

    weighted_scores_subquery = (
        db.session.query(
            StudentAlias.id.label('student_id'),
            func.avg(
                case(
                    (ScoreDetail.type == 'EXAM_15MINS', ScoreDetail.score * 1),
                    (ScoreDetail.type == 'EXAM_45MINS', ScoreDetail.score * 2),
                    (ScoreDetail.type == 'EXAM_FINAL', ScoreDetail.score * 2),
                    else_=0
                )
            ).label('avg_weighted_score')
        )
        .join(Score, StudentAlias.id == Score.student_id)
        .join(ScoreDetail, Score.score_detail_id == ScoreDetail.id)
        .filter(Score.subject_id == subject_id)
        .group_by(StudentAlias.id)
    ).subquery()

    # Base query to retrieve classes and count of students
    base_query = (
        db.session.query(Class.id, Class.name, func.count(Student.id))
        .join(Teach)
        .join(Period)
        .join(StudentClass, Class.id == StudentClass.class_id, isouter=True)
        .join(Student, isouter=True)
        .filter(Teach.subject_id == subject_id, Period.id == period.id)
        .group_by(Class.id)
    )

    # If average score condition is provided, add it to the query
    if avg_gt_or_equal_to is not None:
        base_query = (
            base_query
            .join(weighted_scores_subquery, Student.id == weighted_scores_subquery.c.student_id)
            .filter(weighted_scores_subquery.c.avg_weighted_score >= avg_gt_or_equal_to)
        )

    return base_query.all()


def get_subject_by_id(subject_id):
    return Subject.query.get(subject_id)


if __name__ == '__main__':
    with app.app_context():
        pass
        # subjects = get_subjects()
        # for subject in subjects:
        #     print(subject.name)

        # years = get_years()
        # for year in years:
        #     print(year)
