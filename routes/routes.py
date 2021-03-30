from flask import render_template, request, redirect, url_for, flash, Response
from models import * 
from wsgi import db, app
from .user import * 
from .student import * 
from .hr import * 
from .placecom import * 
from .deprep import * 

@app.route('/')
def home(): 
    return render_template('home.j2', title = 'Home')

