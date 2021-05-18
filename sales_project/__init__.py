from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from decouple import config


app = Flask(__name__)

app.config["SECRET_KEY"] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from sales_project import routes
