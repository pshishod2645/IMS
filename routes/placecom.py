from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from flask import render_template, request, redirect, url_for, flash, Response
from models import * 
from wsgi import db, app

@app.route('/allInterviews')
@login_required
def allInterviews(): 
    if current_user.user_type not in ['placecom']: 
        return redirect('/')
    
    interviews = Interview.query.all()
    for interview in interviews: 
        interview.student = Student.query.filter_by(roll_no = interview.roll_no).first()
        interview.position = Position.query.get(interview.pos_id)

    selections = Interview.query.filter((Position.pos_id == Interview.pos_id) & \
        (Position.num_rounds == Interview.round) & \
            (Interview.qualified == True) )
    
    for sel_interview in selections: 
        sel_interview.student = Student.query.filter_by(roll_no = sel_interview.roll_no).first()
        sel_interview.position = Position.query.get(sel_interview.pos_id)
        
    if not interviews:
        max_rounds = 1
    else:
        max_rounds = max([interview.round for interview in interviews])

    return render_template('Placecom/allInterviews.j2', interviews = interviews, max_rounds = max_rounds, selections = selections)

@app.route('/addHR', methods = ['GET', 'POST'])
@login_required
def addHR(): 
    if current_user.user_type not in ['placecom', 'hr'] : 
        redirect('/')
    
    companies = []
    if current_user.user_type == 'hr': 
        companies = [HR.query.get(current_user.username).company_name]
    else : 
        companies = [c.company_name for c in Company.query.all()]


    if request.method == 'POST' : 
        placecom = Student.query.get(current_user.username)
        form = request.form
        placecom_assgn_roll_no = None

        if current_user.user_type == 'hr' : 
            placecom_assgn_roll_no = HR.query.get(current_user.username).placecom_assgn_roll_no
        else : 
            placecom_assgn_roll_no = Student.query.get(current_user.username).roll_no

        print(form)
        if form.get('company_name') not  in companies : 
            return Response(status = 201)

        user, hr = User(), HR()
        # username, company_name, placecom_assgn_roll_no, password, email, full_name 
        user.username = form.get('username', type = str)
        user.password = form.get('password', type = str)
        user.email = form.get('email', type = str)
        user.full_name = form.get('full_name', type = str)
        user.user_type = 'hr'

        hr.username = user.username 
        hr.company_name = form.get('company_name', type = str)
        hr.placecom_assgn_roll_no = placecom_assgn_roll_no

        try:
            db.session.add(user)
            db.session.flush()
            db.session.add(hr)
            db.session.commit()
            flash('Account added.', 'success')
        except:
            db.session.rollback()
            flash('Account creation failed. Ensure unique username and email address.', 'danger')

    return render_template('Placecom/addHr.j2', companies = companies)
