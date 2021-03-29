from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from flask import render_template, request, redirect, url_for, flash, Response
from models import * 
from wsgi import db, app

@app.route('/login', methods = ['GET', 'POST'])
def login(): 
    if current_user.is_authenticated: 
        return redirect('/')

    if request.method == 'POST' : 
        username, password = request.form.get('username'), request.form.get('password')
        user = User.query.filter( ((User.email == username) | (User.username == username) ) & (User.password == password) ).first()
        # print(user)
        if user : 
            print(user)
            login_user(user)
            return redirect('/')
    return render_template('User/login.j2')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if current_user.is_authenticated: 
        return redirect('/')

    if request.method == 'GET':
        return render_template('User/signup.j2', departments = Department.query.all())

    if request.method == 'POST':        # only for students
        form = request.form
        user = User()
        user.username = form.get('username'),
        user.email = form.get('email'), 
        user.password = form.get('password'), 
        user.full_name = form.get('fullname'), 
        user.user_type = 'student' 

        student = Student()
        student.username = form.get('username'), 
        student.roll_no = form.get('rollno'), 
        student.cgpa = form.get('cgpa'), 
        student.dep_code = form.get('dep_code') 

        db.session.add(user), db.session.commit()
        db.session.add(student), db.session.commit()

        login_user(user)
        return redirect('/')
    return render_template('User/signup.j2')

@login_required
@app.route('/logout')
def logout(): 
    logout_user()
    return redirect('/')

@login_required
@app.route('/profile')
def profile(): 
    person = None
    if current_user.user_type in ['student', 'deprep', 'placecom'] : 
        person = Student.query.get(current_user.username)
    else : 
        person = HR.query.get(current_user.username)
    return render_template('User/profile.j2', person = person)