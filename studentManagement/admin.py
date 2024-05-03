from flask import redirect
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user

from studentManagement import app, db
from studentManagement.models import Subject, Policy


class IsAuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class MySubjectView(IsAuthenticatedView):
    column_list = ['id', 'name', ]
    column_searchable_list = ['id', 'name']
    column_filters = ['id', 'name']
    column_labels = {
        'name': 'Subject name'
    }


class MyPolicyView(IsAuthenticatedView):
    column_list = ['id', 'content', 'data']


class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')

    # def is_accessible(self):
    #     return current_user.is_authenticated


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    # def is_accessible(self):
    #     return current_user.is_authenticated


admin = Admin(app, name="Student Management System", template_mode='bootstrap4')
admin.add_view(MySubjectView(Subject, db.session))
admin.add_view(MyPolicyView(Policy, db.session))
admin.add_view(StatsView(name='Statistics'))
admin.add_view(LogoutView(name='Log out'))
