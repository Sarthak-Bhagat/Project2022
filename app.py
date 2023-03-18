# importing the required libraries
# import time
# from flask import send_from_directory
import os
from os.path import isabs
import secrets
from pathlib import Path

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_file, session, url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_user,
                         logout_user)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from convert import ocr, text_to_speech

UPLOAD_FOLDER = os.path.join("uploads/")
AUDIO_FOLDER = os.path.join("conversions/")
ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".doc",
    ".docx",
    ".odt",
}
filename = ""

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["AUDIO_FOLDER"] = AUDIO_FOLDER
app.config["SECRET_KEY"] = "NotASecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aural_mate.db'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager(app)
login_manager.init_app(app)

with app.app_context():
    SQLAlchemy_Session = sessionmaker(bind=db.engine)
    sqla_session = SQLAlchemy_Session()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    lines_converted = db.Column(db.Integer, default=0)
    documents_uploaded = db.Column(db.Integer, default=0)
    token = db.Column(db.String(32), unique=True, nullable=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def generate_token(self):
        self.token = secrets.token_hex(16)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

@app.before_first_request
def create_table():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return "." in filename and Path(filename).suffix in ALLOWED_EXTENSIONS



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact-us")
def contact():
    return render_template("contact-us.html")


@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            user.generate_token()
            login_user(user)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error=True)
    else:
        return render_template('login.html')

def confirm(output):
    return render_template("confirm.html", output=output)


@app.route("/about-us")
def about():
    return render_template("about-us.html")


def download(filename, high_qual):
    fname = f"{Path(filename).stem}.mp3"
    text = request.form["confirm"]
    print(f"high_qual = {high_qual}")
    text_to_speech(text, fname, high_qual)
    file_size = os.path.getsize(os.path.join(app.config["AUDIO_FOLDER"], fname))
    if current_user.is_authenticated:
        current_user.file_size = file_size
        current_user.lines_converted = len(text.splitlines())
        current_user.documents_uploaded += 1
        db.session.commit()


    return send_file(
        os.path.join(app.config["AUDIO_FOLDER"], fname),
        as_attachment=True,
        download_name=fname,
        mimetype="audio/mp3",
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get registration form data
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if the username or email already exists in the database
        if (
            User.query.filter_by(username=username).first()
            or User.query.filter_by(email=email).first()
        ):
            return "Username or email already exists"

        # Create a new user object with the form data
        user = User(username=username, email=email, password=password)

        # Add the new user object to the database
        db.session.add(user)
        db.session.commit()

        # Redirect the user to the login page
        return redirect("/login")
    else:
        # Show the registration form
        return render_template("register.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/convert", methods=["GET", "POST"])
def uploadfile():

    global filename
    if request.method == "POST":
        if request.files:
            file = request.files["file"]

            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename or "")
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                return confirm(ocr(file))

        if request.form["confirm"]:
            high_qual = False
            if 'high_qual' in request.form:
                high_qual = request.form['high_qual']
            return download(filename, high_qual)

    return render_template("convert.html")


@app.route("/delete")
def delete():
    number = 0
    path = os.path.join("uploads/")
    for root, _, files in os.walk(path):
        for file in files:
            number += 1
            os.remove(os.path.join(root, file))
    path = os.path.join("conversions/")
    for root, _, files in os.walk(path):
        for file in files:
            number += 1
            os.remove(os.path.join(root, file))
    return jsonify(deleted=number)


if __name__ == "__main__":
    app.run(debug=True)
    # app.run()
