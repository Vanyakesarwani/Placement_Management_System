from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://root@localhost/placement_db'
    '?unix_socket=/tmp/mysql.sock'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            return "Login Successful!"

        elif user.role == 'student':
            return redirect(url_for('dashboard'))

        return "Invalid email or password!"
    return render_template('login.html')


@app.route("/register", methods=["GET", "POST"])
def register():

    # When user opens /register
    if request.method == "GET":
        return render_template("register.html")

    # When user submits the form
    name = request.form["name"]
    email = request.form["email"]
    branch = request.form["branch"]

    # Create student object
    student = Student(
        name=name,
        email=email,
        branch=branch
    )

    # Insert into database
    db.session.add(student)
    db.session.commit()

    return "Registration successful!"

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)