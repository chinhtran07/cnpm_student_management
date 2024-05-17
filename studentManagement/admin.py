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
    column_list = ['id', 'username', 'first_name', 'last_name', 'user_role', 'is_active']
    column_searchable_list = ['id', 'username', 'first_name']
    column_filters = ['id', 'username', 'user_role']
    column_labels = {
        "first_name": "Tên",
        "last_name": "Họ và tên đệm",
        "user_role": "Vai trò",
        "is_active": "Trạng thái"
    }

    def on_model_change(self, form, model, is_created):
        if 'password' in form:
            raw_password = form.password.data
            if raw_password:
                hashed_password = hashlib.md5(raw_password.encode('utf-8')).hexdigest()
                if model.password != hashed_password:
                    model.password = hashed_password

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
    column_labels = {
        "content": "Nội dung",
        "data": "Dữ liệu"
    }


def combined_data(counts_students_of_classes, stats_with_avg):
    combined_data = {}

    # Combine counts_students_of_classes into the combined_data dictionary
    for c in counts_students_of_classes:
        combined_data[c[0]] = (c[0], c[1], c[2], None)

    # Update combined_data with the counts from stats_with_avg
    for s in stats_with_avg:
        if s[0] in combined_data:
            combined_data[s[0]] = (
                s[0], combined_data[s[0]][1], combined_data[s[0]][2], s[2], (s[2] / combined_data[s[0]][2]) * 100)

    # Convert the combined_data dictionary to a list of tuples
    combined_data_list = list(combined_data.items())

    return combined_data_list


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
        stats = combined_data(counts_students_of_classes=counts_students_of_classes, stats_with_avg=stats_with_avg)
        subject = dao.get_subject_by_id(subject_id=request.args.get('subjectId'))
        period = dao.get_period(semester=request.args.get('semester'), year=request.args.get('year'))
        return self.render('admin/stats.html', subjects=subjects, years=years,
                           stats=stats,
                           subject=subject, period=period)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


admin = Admin(app, index_view=HomeView(), name="Hệ thống quản trị học sinh", template_mode='bootstrap4')
admin.add_view(UserView(User, db.session, name='Quản lý người dùng'))
admin.add_view(MySubjectView(Subject, db.session, name='Quản lý môn học'))
admin.add_view(MyPolicyView(Policy, db.session, name='Chỉnh sửa quy định'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
