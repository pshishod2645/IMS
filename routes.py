from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from models import * 
from wsgi import db, app

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