from app import db, admin, ModelView, UserMixin
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
    '''username = db.Column(db.String(255), primary_key = True)
    password = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(320))
    full_name = db.Column(db.String(255))'''

# create table company(company_name varchar(255), primary key(company_name));

# create table pos(pos_id int AUTO_INCREMENT, role varchar(255) NOT NULL, description varchar(255), company_name varchar(255), cgpa_cutoff decimal(2,2), location varchar(255), primary key(pos_id), foreign key (company_name) references company(company_name));

# create table department(dep_code varchar(3), dep_name varchar(255) NOT NULL UNIQUE, students_shortlisted int, students_placed int, primary key(dep_code));
class Department(db.Model): 
    __table__ = db.Model.metadata.tables['department']
    '''dep_code = db.Column(db.String(3), primary_key = True)
    dep_name = db.Column(db.String(255), nullable = False, unique = True)
    students_shortlisted = db.Column(db.Integer)
    students_placed = db.Column(db.Integer)
    students = db.relationship('Student', backref = 'dep', lazy = True)'''

# create table student(username varchar(255), roll_no varchar(9) NOT NULL UNIQUE, cgpa decimal(2,2), dep_code varchar(3) NOT NULL, selected_pos_id int, primary key(username),foreign key(username) references user(username), foreign key(dep_code) references department(dep_code), foreign key(selected_pos_id) references pos(pos_id), unique(roll_no, dep_code)
class Student(db.Model):
    __table__ = db.Model.metadata.tables['student'] 
    '''username = db.Column(db.String(255), primary_key = True)
    roll_no = db.Column(db.String(9), nullable = False, unique = True)
    cgpa =  db.Column(db.Float)
    dep_code = db.Column(db.String(3), db.ForeignKey('department.dep_code'), nullable = False)'''

# create table applytoposition(pos_id int NOT NULL, roll_no varchar(9) NOT NULL, primary key(pos_id, roll_no), foreign key pid(pos_id) references pos(pos_id), foreign key roll(roll_no) references student(roll_no));

# create table placecom(roll_no varchar(9), primary key(roll_no), foreign key roll(roll_no) references student(roll_no));

# create table interview(pos_id int, round int, roll_no varchar(9) NOT NULL, status enum('pending', 'ongoing', 'done'), qualified boolean default(FALSE), final_round boolean default(FALSE), primary key(pos_id, round, roll_no), foreign key(pos_id) references pos(pos_id), foreign key(roll_no) references student(roll_no));

# create table departmentrep(roll_no varchar(9) NOT NULL, dep_code varchar(3) NOT NULL, primary key(roll_no, dep_code), foreign key(roll_no, dep_code) references student(roll_no, dep_code));

# create table hr(username varchar(255), company_name varchar(255), placecom_assgn_roll_no 

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Department, db.session))
admin.add_view(ModelView(Student, db.session))