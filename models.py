from wsgi import db, admin, login_manager
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin

# create table user(username varchar(255), password varchar(255) NOT NULL, email varchar(320), full_name varchar(255), primary key(username));
class User(db.Model, UserMixin) :
    __table__ = db.Model.metadata.tables['user']
    
    def get_id(self):
           return (self.username)
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id): 
    return User.query.filter(User.username == user_id).first()

# create table company(company_name varchar(255), primary key(company_name));
class Company(db.Model): 
    __table__ = db.Model.metadata.tables['company']

# create table pos(pos_id int AUTO_INCREMENT, role varchar(255) NOT NULL, description varchar(255), company_name varchar(255), cgpa_cutoff decimal(2,2), location varchar(255), primary key(pos_id), foreign key (company_name) references company(company_name));
class Position(db.Model): 
    __table__ = db.Model.metadata.tables['pos']
# create table department(dep_code varchar(3), dep_name varchar(255) NOT NULL UNIQUE, students_shortlisted int, students_placed int, primary key(dep_code));

class Department(db.Model): 
    __table__ = db.Model.metadata.tables['department']

# create table student(username varchar(255), roll_no varchar(9) NOT NULL UNIQUE, cgpa decimal(2,2), dep_code varchar(3) NOT NULL, selected_pos_id int, primary key(username),foreign key(username) references user(username), foreign key(dep_code) references department(dep_code), foreign key(selected_pos_id) references pos(pos_id), unique(roll_no, dep_code)
class Student(db.Model):
    __table__ = db.Model.metadata.tables['student'] 

# create table placecom(roll_no varchar(9), primary key(roll_no), foreign key roll(roll_no) references student(roll_no));
class Placecom(db.Model): 
    __table__ = db.Model.metadata.tables['placecom']

# create table interview(pos_id int, round int, roll_no varchar(9) NOT NULL, status enum('pending', 'ongoing', 'done'), qualified boolean default(FALSE), final_round boolean default(FALSE), primary key(pos_id, round, roll_no), foreign key(pos_id) references pos(pos_id), foreign key(roll_no) references student(roll_no));
class Interview(db.Model): 
    __table__ = db.Model.metadata.tables['interview']

# create table departmentrep(roll_no varchar(9) NOT NULL, dep_code varchar(3) NOT NULL, primary key(roll_no, dep_code), foreign key(roll_no, dep_code) references student(roll_no, dep_code));
class DepartmentRep(db.Model): 
    __table__ = db.Model.metadata.tables['departmentrep']

# create table hr(username varchar(255), company_name varchar(255), placecom_assgn_roll_no 
class HR(db.Model): 
    __table__ = db.Model.metadata.tables['hr']

all_models = [User, Company, Position, Department, Student, \
    Placecom, Interview, DepartmentRep, HR]
for model in all_models: 
    admin.add_view(ModelView(model, db.session))