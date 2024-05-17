import warnings

from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from wtforms import ValidationError
from wtforms.fields.simple import HiddenField

from studentManagement import app, db, admin
from studentManagement.models import *
from flask_login import current_user, logout_user
from flask import redirect, request


class AuthenticationEmployee(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.EMPLOYEE

class Classroom
