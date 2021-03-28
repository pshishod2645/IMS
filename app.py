import os
from flask import Flask 
from flask import render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from models import * 
from flask_admin.contrib.sqla import ModelView

#Configurations
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@localhost/dbms'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)
admin = Admin(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id): 
    return User.query.filter(User.username == user_id).first()

#Configuration ends here 

#Routes 
@app.route('/')
def home(): 
    return render_template('home.j2', title = 'Home')

@app.route('/login', methods = ['GET', 'POST'])
def login(): 
    if current_user.is_authenticated: 
        return redirect('/')

    if request.method == 'POST' : 
        username, password = request.form.get('username'), request.form.get('password')
        user = User.query.filter((User.email == username or User.username == username) and User.password == password).first()
        # print(user)
        if user : 
            login_user(user)
            return redirect('/')
    return render_template('login.j2')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if current_user.is_authenticated: 
        return redirect('/')

    if request.method == 'GET':
        departments = Department.query.all()
        departments = [d.dep_code for d in departments]
        return render_template('signup.j2', depcodes = departments)

    if request.method == 'POST':        # only for students
        print(requests.form)
    return render_template('signup.j2')

def logout(): 
    logout_user()
    return redirect('/')


if __name__ == '__main__' : 
    app.secret_key = os.urandom(12)
    app.run(debug = True)