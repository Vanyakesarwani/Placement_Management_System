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


@app.route("/")
def home():
    return "Placement Management System Backend is Running!"


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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)