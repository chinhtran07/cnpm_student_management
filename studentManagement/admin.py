import hashlib
import pdb
from datetime import datetime

from flask import redirect, request
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from wtforms import validators
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField

from studentManagement import app, db, dao
from studentManagement.models import Subject, Policy, UserRole, User, Teacher, Employee, Period, Semester


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        amount_of_students_by_period = dao.stats_amount_of_students_by_period(
            semester=request.args.get('semester', Semester.SEMESTER_1.name),
            year=request.args.get('year', datetime.now().year))
        return self.render('admin/index.html', amount_of_students_by_period=amount_of_students_by_period)

    def is_accessible(self):
        return True


class UserView(AuthenticatedView):
    column_list = ['id', 'username', 'first_name', 'user_role', 'is_active']
    column_searchable_list = ['id', 'username', 'first_name']
    column_filters = ['id', 'username', 'first_name']

    def on_model_change(self, form, model, is_created):
        if 'password' in form:
            raw_password = form.password.data
            if raw_password:
                model.password = hashlib.md5(raw_password.encode('utf-8')).hexdigest()

        super().on_model_change(form, model, is_created)


class MySubjectView(AuthenticatedView):
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


class MyPolicyView(AuthenticatedView):
    column_list = ['id', 'content', 'data']


class PeriodView(AuthenticatedView):
    column_list = ['id', 'semester', 'year']
    column_filters = ['year']
    column_sortable_list = ['year']
    column_labels = {
        'semester': 'Học kỳ',
        'year': 'Năm học'
    }


class StatsView(BaseView):
    @expose('/')
    def index(self):
        subjects = dao.get_subjects()
        years = dao.get_years()
        counts_students_of_classes = dao.count_students_of_classes_by_subject_and_period(
            subject_id=request.args.get('subjectId'),
            semester=request.args.get('semester'),
            year=request.args.get('year'))
        stats_with_avg = dao.count_students_of_classes_by_subject_and_period(subject_id=request.args.get('subjectId'),
                                                                             semester=request.args.get('semester'),
                                                                             year=request.args.get('year'),
                                                                             avg_gt_or_equal_to=5)
        combine = counts_students_of_classes + stats_with_avg
        return self.render('admin/stats.html', subjects=subjects, years=years, stats=combine)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app, index_view=HomeView(), name="Hệ thống quản trị học sinh", template_mode='bootstrap4')
admin.add_view(UserView(User, db.session))
admin.add_view(MySubjectView(Subject, db.session))
admin.add_view(MyPolicyView(Policy, db.session))
admin.add_view(PeriodView(Period, db.session))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
