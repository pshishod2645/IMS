from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from flask import render_template, request, redirect, url_for, flash, Response
from models import * 
from wsgi import db, app

@app.route('/student/positions')
@login_required
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

    return render_template('Student/positions.j2', positions = positions)

@app.route('/student/apply_to_position/<int:pos_id>', methods = ["POST"])
@login_required
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

@app.route('/student/interviews')
@login_required
def studentInterviews(): 
    if current_user.user_type not in ['placecom', 'student', 'deprep'] : 
        return redirect('/')

    student = Student.query.get(current_user.username)
    all_interviews = Interview.query.filter_by(roll_no = student.roll_no).all()
    selections = Interview.query.filter((Position.pos_id == Interview.pos_id) & \
        (Position.num_rounds == Interview.round) & (Interview.roll_no == student.roll_no) & \
            (Interview.qualified == True) ) 
    
    if len(all_interviews) == 0 : 
        return render_template('Student/interviews.j2', interviews = [], selections = selections, max_rounds = 1, student = student)

    for interview in all_interviews: 
        interview.position = Position.query.get(interview.pos_id)
    
    for sel_interview in selections: 
        sel_interview.position = Position.query.get(sel_interview.pos_id)

    max_rounds = max([interview.round for interview in all_interviews])

    return render_template('Student/interviews.j2', interviews = all_interviews, selections = selections, max_rounds = max_rounds, student = student)

@app.route('/student/select/<int:pos_id>', methods = ['POST'])
@login_required
def selectPosition(pos_id): 
    if current_user.user_type not in ['student', 'placecom', 'deprep']: 
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
