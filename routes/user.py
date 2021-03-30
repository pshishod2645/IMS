from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from flask import render_template, request, redirect, url_for, flash, Response
from models import * 
from wsgi import db, app

@app.route('/login', methods = ['GET', 'POST'])
def login(): 
    next_url = request.args.get('next', default = '/')
    if current_user.is_authenticated: 
        return redirect(next_url)

    if request.method == 'POST' : 
        username, password = request.form.get('username'), request.form.get('password')
        user = User.query.filter( ((User.email == username) | (User.username == username) ) & (User.password == password) ).first()
        if user :
            login_user(user)
            return redirect(next_url)
        else:
            flash("Login failed. Please enter valid credentials and try again, or signup for a new account.", 'danger')
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

        try:
            db.session.add(user)
            db.session.flush()
            db.session.add(student)
            db.session.commit()
            flash('Account created successfully. Please login using the link.', 'success')
        except:
            db.session.rollback()
            flash('Signup failed. Ensure unique username, email address and roll number.', 'danger')
    return render_template('User/signup.j2', departments = Department.query.all())

@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect('/')

@app.route('/profile')
@login_required
def profile(): 
    person = None
    if current_user.user_type in ['student', 'deprep', 'placecom'] : 
        person = Student.query.get(current_user.username)
    else : 
        person = HR.query.get(current_user.username)
    return render_template('User/profile.j2', person = person)

@app.route('/changePassword', methods = ['POST'])
@login_required
def changePassword(): 
    user = User.query.get(current_user.username)
    new_password = request.form.get('new_password', type = str)
    if (not new_password) or (len(new_password) == 0) : 
        flash('New password Invalid! Password Not changed', 'danger')
        return redirect('/profile')
    user.password = new_password
    db.session.commit()

    flash('Password Changed!', 'success')
    return redirect('/profile')