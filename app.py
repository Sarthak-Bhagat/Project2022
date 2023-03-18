# importing the required libraries

# import time

# from flask import send_from_directory
import os

from os.path import isabs
import secrets

from pathlib import Path


from flask import (

    Flask,

    flash,

    jsonify,

    redirect,

    render_template,

    request,

    send_file,

    session,

    url_for,
)

from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.utils import secure_filename


from convert import extract_text_from_file, text_to_speech


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

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aural_mate.db"

# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy()

db.init_app(app)


login_manager = LoginManager(app)
login_manager.init_app(app)


with app.app_context():

    SQLAlchemy_Session = sessionmaker(bind=db.engine)

    sqla_session = SQLAlchemy_Session()



class User(db.Model, UserMixin):
    """

    The User class represents a user in the system and inherits from db.Model and UserMixin.


    Attributes:


    id (db.Integer): the user's unique identifier

    username (db.String): the user's username

    email (db.String): the user's email

    password_hash (db.String): the hashed password for the user

    file_size (db.Integer): the size of files uploaded by the user, default 0

    lines_converted (db.Integer): the number of lines converted by the user, default 0

    documents_uploaded (db.Integer): the number of documents uploaded by the user, default 0

    token (db.String): the user's unique token, nullable

    Methods:


    __init__(self, username, email, password): constructs a User instance with the given username, email, and password

    generate_token(self): generates a unique token for the user and updates the token attribute in the database

    check_password(self, password): checks if the given password matches the user's password_hash

    __repr__(self): returns a string representation of the user instance
    """


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



@app.route("/login", methods=["GET", "POST"])

def login():
    """

    The login function handles GET and POST requests to the "/login" route.


    On a GET request, the user is presented with the login page. On a POST request, the function attempts to log the user in.

    If the username and password are valid, a user session is started and the user is redirected to the home page.

    If the login is unsuccessful, the login page is displayed again with an error message.


    Parameters:


    None

    Returns:


    If the request method is GET, returns the "login.html" template rendered.

    If the request method is POST and the login is successful, redirects to the "home" route.

    If the request method is POST and the login is unsuccessful, returns the "login.html" template rendered with an error message.
    """

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):

            session["user_id"] = user.id

            user.generate_token()
            login_user(user)
            return redirect(url_for("home"))

        else:

            return render_template("login.html", error=True)

    else:
        return render_template("login.html")



def confirm(output):

    return render_template("confirm.html", output=output)



@app.route("/about-us")

def about():

    return render_template("about-us.html")



def download(filename, high_qual):
    """

    The download function takes in two arguments filename and high_qual.

    It converts the text obtained from a form to speech and saves the output file in the server's audio folder.

    If the current user is authenticated, the function updates the user's file_size, lines_converted, and documents_uploaded attributes in the database.

    Finally, the function sends the converted audio file as an attachment for download.


    Args:


    filename: A string representing the name of the file to be converted to speech.

    high_qual: A boolean value indicating whether to use high-quality speech synthesis or not.


    Returns:


    A Flask Response object representing the converted audio file.
    """


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
    """

    Register a new user.


    If the request method is GET, the function renders the registration form.


    If the request method is POST, the function attempts to create a new user

    with the provided username, email, and password. If the username or email

    already exists in the database, the function returns an error message. If

    the user is created successfully, the function redirects to the login page.


    Returns:

        str or flask.Response: If the request method is GET, the function returns

        the registration form as an HTML string. If the request method is POST

        and the user is created successfully, the function redirects to the

        login page. If the request method is POST and the user cannot be created

        due to a conflict with an existing username or email, the function returns
        an error message as a string.
    """

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]

        if (

            User.query.filter_by(username=username).first()

            or User.query.filter_by(email=email).first()

        ):

            return "Username or email already exists"


        user = User(username=username, email=email, password=password)


        db.session.add(user)

        db.session.commit()


        return redirect("/login")

    else:
        return render_template("register.html")



@app.route("/logout")

def logout():
    logout_user()

    return redirect("/")



@app.route("/convert", methods=["GET", "POST"])

def uploadfile():
    """

        This function defines the route for uploading and converting files. It handles both GET and POST requests.


    Parameters:


    None

    Returns:


    GET: Renders the "convert.html" template.

    POST: 

    If a file is selected and is valid, saves the file to the server, passes the file to the OCR function to extract text, then redirects the user to the confirmation page with the extracted text displayed.

    If the user confirms the extracted text, it calls the download() function to convert the extracted text to speech and download the audio file.

    If the user cancels the confirmation, the file is deleted from the server and the user is redirected back to the upload page.

    If there is an error with the file or extraction, the user is redirected back to the upload page with an error message.
    
    """


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
                return confirm(extract_text_from_file(file))


        if request.form["confirm"]:

            high_qual = False

            if "high_qual" in request.form:

                high_qual = request.form["high_qual"]

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

