from flask import render_template, request, redirect, url_for, flash, Response
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
        user = User.query.filter( ((User.email == username) | (User.username == username) ) & (User.password == password) ).first()
        # print(user)
        if user : 
            print(user)
            login_user(user)
            return redirect('/')
    return render_template('login.j2')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if current_user.is_authenticated: 
        return redirect('/')

    if request.method == 'GET':
        return render_template('signup.j2', departments = Department.query.all())

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
    return render_template('signup.j2')

@login_required
@app.route('/logout')
def logout(): 
    logout_user()
    return redirect('/')

@login_required
@app.route('/student/positions')
def studentPositions(): 
    if current_user.user_type not in ['student', 'placecom', 'deprep']:
        return redirect('/')

    student = Student.query.filter_by(username = current_user.username).first()
    appliedPositions = Interview.query.filter_by(roll_no = student.roll_no, round = 1).all()
    appliedPositions = [a2P.pos_id for a2P in appliedPositions]
    assert student is not None

    positions = Position.query.filter(student.cgpa >= Position.cgpa_cutoff).all()
    for position in positions: 
        position.applied = (position.pos_id in appliedPositions)

    return render_template('student_positions.j2', positions = positions)

@login_required
@app.route('/student/apply_to_position/<int:pos_id>', methods = ["POST"])
def applyToPosition(pos_id): 
    if current_user.user_type not in ['student', 'placecom', 'deprep']: 
        return flask.Response(status = 201)
    
    try : 
        student = Student.query.filter_by(username = current_user.username).first()
        interview = Interview()
        interview.roll_no = student.roll_no
        interview.pos_id = pos_id
        interview.round = 1
        interview.status = 'pending'
        db.session.add(interview), db.session.commit()
    except:
        print('Database fuckedup or invalid data') 
        return Response(status = 201)
    return Response(status = 200)

@login_required
@app.route('/dep_statistics') 
def depStatistics(): 
    if current_user.user_type not in ['dep'] : 
        return redirect('/')

    dep = Department.query.filter((Student.username == current_user.username) & (Student.dep_code == Department.dep_code) ).first()
    try: 
        assert dep is not None
    except: 
        return 'No Department found! Inconsistencies in Database'
    return render_template('dep_statistics.j2', dep = dep)

@login_required
@app.route('/hr/positions')
def hrPositions():
    if current_user.user_type not in ['hr']: 
        return redirect('/')

    positions = Position.query.filter( (Position.company_name == HR.company_name) & (HR.username == current_user.username)).all()

    return render_template('hr_positions.j2', positions = positions, company_name = "amazon")

@app.route('/hr/position/<int:pos_id>')
@login_required
def hrInterview(pos_id): 
    position = Position.query.get(pos_id)
    all_interviews = Interview.query.filter_by(pos_id = pos_id).all()
    for interview in all_interviews: 
        interview.student = Student.query.filter_by(roll_no = interview.roll_no).first()

    position.interviews = all_interviews
    qualified = [inter for inter in interviews if (inter.qualified == True) and (inter.round == position.num_rounds)]

    return render_template('hr_interview.j2', position = positions, qualified = qualified) 

@app.route('/hr/<int:pos_id>/<string:roll_no>/<int:round>/modify', methods = ['POST'])
def approveOrRejectForPosition(pos_id, roll_no, round): 
    if current_user.user_type not in ['hr'] : 
        return Response(status = 201)
    
    status = request.args.get('status')
    qualified = request.args.get('qualified', type = bool)

    position = Position.query.filter_by(pos_id = pos_id).first()
    interview = Interview.query.filter_by(pos_id = pos_id, roll_no = roll_no, round = round).first()
    assert (position is not None) and (interview is not None)

    options = ['pending', 'scheduled', 'ongoing', 'done']
    if (status is not None) and (status in options) : 
        # can only move status forward
        if options.index(status) <= options.index(interview.status):
            print('Cant change status from {interview.status} to {status}') 
            return Response(status = 201)
        interview.status = status
        db.session.commit()
        return Response(status = 200)
    
    if (qualified is not None): 
        if interview.qualified == True : 
            print('Cant change qualified status from {interview.qualified} to {qualified}')
            return Response(status = 201)

        interview.qualified = qualified 
        db.session.add(interview)

        if interview.round != position.num_rounds : 
            next_interview = Interview()
            next_interview.round = interview.round + 1 
            next_interview.pos_id, next_interview.roll_no = interview.pos_id, interview.roll_no
            db.session.add(next_interview)
        db.session.commit()
        return Response(status = 200) 
    print('Nothing to change') 
    return Response(status = 201)

@login_required
@app.route('/student/interviews')
def studentInterviews(): 
    if current_user.user_type not in ['placecom', 'student', 'deprep'] : 
        return redirect('/')

    student = Student.query.get(current_user.username)
    all_interviews = Interview.query.filter_by(roll_no = student.roll_no).all()
    selections = Interview.query.filter((Position.pos_id == Interview.pos_id) & \
        (Position.num_rounds == Interview.round) & (Interview.roll_no == student.roll_no) & \
            (Interview.qualified == True) ) 
    
    if len(all_interviews) == 0 : 
        return render_template('student_interviews.j2', interviews = [])

    for interview in all_interviews: 
        interview.position = Position.query.get(interview.pos_id)
    
    max_rounds = max([interview.round for interview in all_interviews])

    return render_template('student_interviews.j2', interviews = interviews, selections = selections, max_rounds = max_rounds)

@login_required
@app.route('/student/select/<int:pos_id>', methods = ['POST'])
def selectPosition(pos_id): 
    if current_user not in ['student', 'placecom', 'deprep']: 
        return Response(status = 201)
    
    student = Student.query.get(current_user.username)
    if student.selected_pos_id : 
        return Response(status = 201)
    try : 
        student.selected_pos_id = pos_id
        db.session.add(student)
        db.session.commit()
    except: 
        print('Database fucked up or Invalid Data')
        return Response(status = 201)
    return Response(status = 200)
