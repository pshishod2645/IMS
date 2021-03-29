from flask_login import current_user, login_user, logout_user, login_required, UserMixin
from flask import render_template, request, redirect, url_for, flash, Response
from models import * 
from wsgi import db, app

def getShortlistedAndPlaced(dep_code): 
    placed = Student.query.filter((Student.dep_code == dep_code) & (selected_pos_id != None )).all().length
    shortlisted = Student.query.filter(Student.dep_code == dep_code).\
        filter((Interview.roll_no == Student.roll_no) & (Interview.pos_id == Student.pos_id) &\
            (Interview.round == Position.num_rounds)).all().length
    return (placed, shortlisted)

@login_required
@app.route('/dep_statistics') 
def depStatistics(): 
    if current_user.user_type not in ['deprep'] : 
        return redirect('/')

    dep = Department.query.filter((Student.username == current_user.username) & (Student.dep_code == Department.dep_code) ).first()
    try: 
        assert dep is not None
        dep.placed, dep.shortlisted = getShortlistedAndPlaced(dep.dep_code)
        db.session.commit()
    except: 
        return 'No Department found! Inconsistencies in Database'
    return render_template('Deprep/dep_statistics.j2', dep = dep)