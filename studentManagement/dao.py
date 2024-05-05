import hashlib

from sqlalchemy import desc

from studentManagement import db
from studentManagement.models import User, Student, Period, StudentClass


def count_students_of_period(period_id):
    return StudentClass.query.filter_by(period_id=period_id).count()


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
