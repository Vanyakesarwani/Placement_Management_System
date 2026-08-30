from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =( 'mysql+pymysql://root:vanya7890@localhost/placement_db'
                                        '?unix_socket=/tmp/mysql.sock')
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
    return "Database connection successful!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist


    app.run(debug=True)