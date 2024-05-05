from flask import redirect
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules
from flask_admin.model import InlineFormAdmin
from flask_login import current_user, logout_user
from wtforms import validators
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField

from studentManagement import app, db, dao
from studentManagement.models import Subject, Policy, UserRole, User, Teacher, Employee, Period


class IsAuthenticatedView(ModelView):
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView
from studentManagement.models import UserRole
from studentManagement import app, db
from flask_login import logout_user, current_user
from flask import redirect


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        period = dao.get_most_recent_period()
        amount_students = dao.count_students_of_period(period.id)
        return self.render('admin/index.html', amount_students=amount_students, period=period)

    def is_accessible(self):
        return True


class UserView(IsAuthenticatedView):
    column_list = ['id', 'username', 'first_name', 'user_role', 'is_active']
    column_searchable_list = ['id', 'username', 'first_name']
    column_filters = ['id', 'username', 'first_name']

    form_extra_fields = {
        'user_ref': StringField('User Reference'),
    }


class MySubjectView(IsAuthenticatedView):
    column_list = ['id', 'name', 'grade', 'exam_15mins', 'exam_45mins']
    column_searchable_list = ['id', 'name']
    column_filters = ['id', 'name', 'grade']
    column_labels = {
        'name': 'Tên môn',
        'grade': 'Khối',
        'exam_15mins': 'Số bài kiểm tra 15 phút',
        'exam_45mins': 'Số bài kiểm tra 45 phút'
    }
    form_extra_fields = {
        'exam_15mins': IntegerField('Số bài kiểm tra 15 phút', validators=[validators.NumberRange(min=1, max=5)]),
        'exam_45mins': IntegerField('Số bài kiểm tra 45 phút', validators=[validators.NumberRange(min=1, max=3)])

    }


class MyPolicyView(IsAuthenticatedView):
    column_list = ['id', 'content', 'data']


class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app, index_view=HomeView(), name="Student Management System", template_mode='bootstrap4')
admin.add_view(UserView(User, db.session))
admin.add_view(MySubjectView(Subject, db.session))
admin.add_view(MyPolicyView(Policy, db.session))
admin.add_view(StatsView(name='Statistics'))
admin.add_view(LogoutView(name='Log out'))
