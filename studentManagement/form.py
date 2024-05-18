from datetime import datetime

from wtforms.fields.choices import SelectField, SelectMultipleField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, BooleanField
from wtforms.form import Form
from flask_wtf import FlaskForm
from wtforms.validators import Optional, DataRequired

from studentManagement.models import UserGender, Student, StudentGrade


class StudentForm(FlaskForm):
    id = IntegerField(render_kw={'hidden': True}, validators=[Optional()])
    first_name = StringField('Tên')
    last_name = StringField('Họ')
    gender = SelectField('Giới tính', choices=[(gender.name, gender.name) for gender in UserGender])
    admission_date = DateField('Ngày nhập học', validators=[Optional()])
    dob = DateField('Ngày sinh', validators=[Optional()])
    address = StringField('Địa chỉ')
    email = StringField('Email')
    phone_number = StringField('Số điện thoại')
    is_active = BooleanField('Kích hoạt')


class ClassroomForm(FlaskForm):
    id = IntegerField(render_kw={'hidden': True}, validators=[Optional()])
    name = StringField('Tên', validators=[DataRequired()])
    grade = SelectField('Khối', coerce=str, validators=[DataRequired()])
    students = SelectMultipleField('Học sinh', coerce=int, validators=[Optional()])
    teacher = SelectField('Giáo Viên', coerce=int, validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(ClassroomForm, self).__init__(*args, **kwargs)
        # Khởi tạo danh sách các lựa chọn cho trường "grade"
        self.grade.choices = [(choice.name, choice.value) for choice in StudentGrade]
