# importing the required libraries
# import time
# from flask import send_from_directory
from pathlib import Path
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, jsonify, send_file
from flask_login import current_user, login_user, logout_user
from pathlib import Path
from models import db
import os

from convert import ocr, speak

UPLOAD_FOLDER = os.path.join("uploads/")
AUDIO_FOLDER = os.path.join("conversions/")
ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".png",
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
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def allowed_file(filename):
    return "." in filename and Path(filename).suffix in ALLOWED_EXTENSIONS


@app.before_first_request
def create_table():
    db.create_all()


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


@app.route("/login", methods=["POST", "GET"])
def login():
    # if current_user.is_authenticated:
    #     return redirect("/")

    if request.method == "POST":
        email = request.form["email"]
        user = UserModel.query.filter_by(email=email).first()
        if user is not None and user.check_password(request.form["password"]):
            login_user(user)
            return redirect("/")

    return render_template("login.html")


def confirm(output):
    return render_template("confirm.html", output=output)


@app.route("/about-us")
def about():
    return render_template("about-us.html")


def download(filename):
    fname = f"{Path(filename).stem}.mp3"
    speak(request.form["confirm"], fname)
    return send_file(
        os.path.join(app.config["AUDIO_FOLDER"], fname),
        as_attachment=True,
        download_name=fname,
        mimetype="audio/mp3",
    )


@app.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        if UserModel.query.filter_by(email=email).first():
            return "Email already Present"

        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/convert", methods=["GET", "POST"])
def uploadfile():
    global filename
    if request.json:
        print(request.json)
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
            return download(filename)

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
    app.run()
