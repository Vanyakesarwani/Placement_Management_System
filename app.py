import os
from urllib.parse import quote_plus

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_port = os.getenv('MYSQL_PORT', '3306')

if not mysql_password:
    raise RuntimeError(
        'MYSQL_PASSWORD is not set. Start the app with: '
        'export MYSQL_PASSWORD="your MySQL password"'
    )

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{mysql_user}:{quote_plus(mysql_password)}'
    f'@{mysql_host}:{mysql_port}/placement_db'
    '?unix_socket=/tmp/mysql.sock'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    branch = db.Column(db.String(50))
    password = db.Column(db.String(100))
    roll_number = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    backlogs = db.Column(db.Integer)
    skills = db.Column(db.String(500))

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('student', 'admin'), nullable=False)

@app.route("/")
def home():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            if user.role == 'student':
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                return redirect(url_for('student'))
            return "Login Successful!"

        return "Invalid email or password!"
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        roll_number = request.form['roll_number']
        branch = request.form['branch']
        cgpa = request.form['cgpa']
        backlogs = request.form['backlogs']
        skills = request.form['skills']

        if password != confirm_password:
            return "Passwords do not match!"

        # Create user
        user = User(
            name=name,
            email=email,
            password=password,
            role='student'
        )

        db.session.add(user)
        db.session.flush()

        student = Student(
            name=name,
            email=email,
            password=password,
            roll_number=roll_number,
            branch=branch,
            cgpa=float(cgpa),
            backlogs=int(backlogs),
            skills=skills
        )
        db.session.add(student)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/student')
def student():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('student.html', user_name=session.get('user_name'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)