import os
from urllib.parse import quote_plus

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

mysql_user = os.getenv("MYSQL_USER", "root")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST", "localhost")
mysql_port = os.getenv("MYSQL_PORT", "3306")

if mysql_password:
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{mysql_user}:{quote_plus(mysql_password)}"
        f"@{mysql_host}:{mysql_port}/placement_db"
        "?unix_socket=/tmp/mysql.sock"
    )
else:
    base_dir = os.path.abspath(os.path.dirname(__file__))
    sqlite_path = os.path.join(base_dir, "instance", "placement.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your_secret_key_here"

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("student", "admin"), nullable=False)


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    backlogs = db.Column(db.Integer)
    skills = db.Column(db.String(500))


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150))


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            session["role"] = user.role

            if user.role == "student":
                return redirect(url_for("student"))
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

        return "Invalid email or password!"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        roll_number = request.form["roll_number"]
        branch = request.form["branch"]
        cgpa = request.form["cgpa"]
        backlogs = request.form["backlogs"]
        skills = request.form["skills"]

        if password != confirm_password:
            return "Passwords do not match!"

        user = User(name=name, email=email, password=password, role="student")
        student = Student(
            name=name,
            email=email,
            roll_number=roll_number,
            branch=branch,
            cgpa=float(cgpa),
            backlogs=int(backlogs),
            skills=skills,
        )
        db.session.add_all([user, student])
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/student")
def student():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("student.html", user_name=session.get("user_name"))


@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    if user is None:
        session.clear()
        return redirect(url_for("login"))
    if user.role != "student":
        return redirect(url_for("login"))

    student = Student.query.filter_by(email=user.email).first()
    if student is None:
        student = Student(
            name=user.name,
            email=user.email,
            roll_number=f"TEMP_{user.id}",
            branch="",
            cgpa=None,
            backlogs=0,
            skills="",
        )
        db.session.add(student)
        db.session.commit()

    if request.method == "POST":
        try:
            cgpa = float(request.form["cgpa"])
            backlogs = int(request.form["backlogs"])
        except (ValueError, TypeError):
            return render_template(
                "profile.html",
                student=student,
                user=user,
                error="CGPA and backlogs must be valid numbers.",
            )

        student.name = user.name
        student.roll_number = request.form["roll_number"]
        student.branch = request.form["branch"]
        student.cgpa = cgpa
        student.backlogs = backlogs
        student.skills = request.form["skills"]
        db.session.commit()
        return redirect(url_for("student_profile"))

    return render_template("profile.html", student=student, user=user)


@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin_dash.html")


@app.route("/admin/companies", methods=["GET", "POST"])
def companies():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        company = Company(
            name=request.form["name"],
            location=request.form["location"],
        )
        db.session.add(company)
        db.session.commit()

    return render_template(
        "companies.html",
        companies=Company.query.order_by(Company.id).all(),
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
