from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from flask import render_template, request, redirect, url_for, flash, Response
from models import * 
from wsgi import db, app

@login_required
@app.route('/allInterviews')
def allInterviews(): 
    if current_user.user_type not in ['placecom']: 
        return redirect('/')
    
    interviews = Interview.query.all()
    for interview in interviews: 
        interview.student = Student.query.filter_by(roll_no = interview.roll_no).first()
        interview.position = Position.query.get(interview.pos_id)

    if not interviews:
        max_rounds = 1
    else:
        max_rounds = max([interview.round for interview in interviews])

    return render_template('Placecom/allInterviews.j2', interviews = interviews, max_rounds = max_rounds)