# importing the required libraries
import time
from flask import Flask, render_template, request
from flask import send_from_directory
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect
import os

from convert import ocr

UPLOAD_FOLDER = "/home/dez/Downloads/Project/Main/uploads/"
AUDIO_FOLDER = "/home/dez/Downloads/Project/Main/conversions/"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "png", "doc", "docx", "odt"}
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["AUDIO_FOLDER"] = AUDIO_FOLDER
app.config["SECRET_KEY"] = "NotSecret"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact-us")
def contact():
    return render_template("contact-us.html")


@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/about-us")
def about():
    return render_template("about-us.html")


@app.route("/convert", methods=["GET", "POST"])
def uploadfile():
    # print(request.method)
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            ocr(file, False)
            time.sleep(10)
            print(f"{(filename).split('.')[0]}.mp3")
            return send_from_directory(
                app.config["AUDIO_FOLDER"], f"{(filename).split('.')[0]}.mp3"
            )
    return render_template("convert.html")


if __name__ == "__main__":
    app.run()
