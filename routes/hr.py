from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from flask import render_template, request, redirect, url_for, flash, Response
from models import * 
from wsgi import db, app

@app.route('/hr/positions')
@login_required
def hrPositions():
    if current_user.user_type not in ['hr']: 
        return redirect('/')

    positions = Position.query.filter( (Position.company_name == HR.company_name) & (HR.username == current_user.username)).all()
    hr = HR.query.get(current_user.username)

    return render_template('HR/positions.j2', positions = positions, company_name = hr.company_name)

@app.route('/hr/position/<int:pos_id>')
@login_required
def hrInterview(pos_id): 
    position = Position.query.get(pos_id)
    all_interviews = Interview.query.filter_by(pos_id = pos_id).all()
    for interview in all_interviews: 
        interview.student = Student.query.filter_by(roll_no = interview.roll_no).first()

    position.interviews = all_interviews

    qualified = [inter for inter in all_interviews if (inter.qualified == True) and (inter.round == position.num_rounds)]
    for qual_interview in qualified: 
        qual_interview.student = Student.query.filter_by(roll_no = qual_interview.roll_no).first()
    
    if not all_interviews:
        max_rounds = 1
    else:
        max_rounds = max([interview.round for interview in all_interviews])

    return render_template('HR/interview.j2', position = position, qualified = qualified, max_rounds = max_rounds) 

@app.route('/hr/<int:pos_id>/<string:roll_no>/<int:round>/modify', methods = ['POST'])
@login_required
def approveOrRejectForPosition(pos_id, roll_no, round): 
    if current_user.user_type not in ['hr'] : 
        return Response(status = 201)
    
    status = request.args.get('status')
    qualified = request.args.get('qualified')

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
            next_interview.status = 'pending'
            db.session.add(next_interview)
        db.session.commit()
        return Response(status = 200) 
    print('Nothing to change') 
    return Response(status = 201)

@app.route('/hr/createPosition', methods = ['GET', 'POST'])
@login_required
def createPosition(): 
    if current_user.user_type not in ['hr']: 
        return Response(status = 201)
    # role, description, company_name, cgpa_cutoff, location, num_rounds
    if request.method == 'POST' : 
        form = request.form
        hr = HR.query.get(current_user.username) 

        pos = Position()
        pos.role = form.get('role', type = str)
        pos.description = form.get('description', type = str)
        pos.cgpa_cutoff = form.get('cgpa_cutoff', type = float)
        pos.location = form.get('location', type = str)
        pos.num_rounds = form.get('num_rounds', type = int)
        pos.company_name = hr.company_name

        db.session.add(pos)
        db.session.commit()

        return redirect('/hr/positions')
    return render_template('HR/positions.j2')
