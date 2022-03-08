# importing the required libraries
from flask import Flask, render_template, request, send_file
from numpy import False_
from werkzeug.utils import secure_filename
import os

from convert import ocr

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact-us")
def contact():
    return render_template("contact-us.html")


@app.route("/features")
def features():
    return render_template("contact-us.html")


@app.route("/about-us")
def about():
    return render_template("about-us.html")


@app.route("/convert", methods=["GET", "POST"])
def convert():
    return render_template("convert.html")


@app.route("/convert_bare", methods=["GET", "POST"])
def convert_bare():
    return render_template("test.html")


@app.route("/upload", methods=["GET", "POST"])
def uploadfile():
    if request.method == "POST":
        f = request.files["file"]
        print("Uploading")
        f.save(secure_filename(f.filename))
        ocr(f, True)
        print("Download")
        return send_file("output.mp3", as_attachment=True)


if __name__ == "__main__":
    app.run()  # running the flask app
