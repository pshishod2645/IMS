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
        interview.student = Student.query.filter_by(roll_no = interview.roll_no)

    return render_template('Placecom/allInterviews.j2', interviews = interviews)