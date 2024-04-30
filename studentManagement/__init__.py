from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)

app.secret_key = 'K$2a9Bp@Lq#4rT5cG6d%I7eF8s*J9t&U0iH!oP1uY2wX3y@Z4vQ5n^M6xO7'
app.config["SQLALCHEMY_DATABASE_URI"] = ("mysql+pymysql://root:%s@localhost/students_management?charset=utf8mb4"
                                         % quote('admin@123'))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 6

db = SQLAlchemy(app)
# login = LoginManager(app)

# cloudinary.config(cloud_name='',
#                   api_key='',
#                   api_secret='')