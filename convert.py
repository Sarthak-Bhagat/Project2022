import os
import time

import cv2
import docx2txt
import pytesseract
import pyttsx3
from gtts import gTTS
from pdf2image import convert_from_path
from odf.opendocument import load
from odf import teletype

engine = pyttsx3.init()


def ocr(f):
    # print(f.filename)
    filename = os.path.join("uploads", f.filename)
    fname, ext = os.path.splitext(f.filename)
    # print(fname, ext)

    output = "Something went wrong"

    if ext in [".png", ".jpg", ".jpeg"]:
        image = cv2.imread(filename)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        threshold_img = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )[1]
        custom_config = r"--oem 3 --psm 6"
        output = pytesseract.image_to_string(
            threshold_img, config=custom_config)

    elif ext in [".docx", ".doc"]:
        output = docx2txt.process(filename)

    elif ext == ".pdf":
        pages = convert_from_path(filename)
        output = ""
        for _, page_data in enumerate(pages):
            output += "\n" + pytesseract.image_to_string(page_data)

    elif ext == ".txt":
        with open(filename, "r") as file:
            output = file.read()

    elif ext == ".odt":
        doc = load(filename)
        output = teletype.extractText(doc).strip()

    print(output)

    return output


def speak(text, fname):
    print("Converting to audio")
    print(text)
    print(fname)

    high_qual = True
    if high_qual:
        gTTS(text=text, lang="en").save(fname)
    else:
        engine.setProperty("voice", "english")
        fname = os.path.join(f"conversions/{fname}")
        engine.save_to_file(text, fname)
        engine.runAndWait()
        while not os.path.exists(fname):
            print("waiting")
            time.sleep(1)
    return True


def text_to_speech(input_text, filename, high_qual=False):
    filename = os.path.join(f"conversions/{filename}")
    print(filename)
    if high_qual:
        tts = gTTS(text=input_text, lang="en", slow=False)
        tts.save(filename)
    else:
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.7)
        engine.setProperty("voice", "en-us")
        tts = engine.save_to_file(input_text, filename)
        engine.runAndWait()
    while not os.path.exists(filename):
        print("waiting")
        time.sleep(1)
