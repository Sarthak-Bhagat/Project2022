import pytesseract
from pathlib import Path
from PIL import Image
import cv2
import time
import docx
from gtts import gTTS
import pyttsx3
import os
from pdf2image import convert_from_path

engine = pyttsx3.init()


def ocr(f):
    print(f.filename)
    filename = os.path.join(f"uploads/{f.filename}")
    fname = Path(f.filename).stem
    ext = Path(f.filename).suffix
    print(fname, ext)

    output = "Something went wrong"

    if ext in [".png", ".jpg", ".jpeg"]:
        image = cv2.imread(filename)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        threshold_img = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )[1]
        custom_config = r"--oem 3 --psm 6"
        output = pytesseract.image_to_string(threshold_img, config=custom_config)

    elif ext in [".docx", ".doc"]:
        doc = docx.Document(f)
        output = ""
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
            output = "\n".join(fullText)

    elif ext == ".pdf":

        doc = convert_from_path(f"uploads/{f.filename}")
        output = ""

        for _, page_data in enumerate(doc):
            output += "\n" + pytesseract.image_to_string(page_data)

    print(output)

    return output


def speak(text, fname):
    print("Converting to audio")
    high_qual = False
    if high_qual == True:
        tts = gTTS(text=text, lang="en")
        tts.save(fname)
    else:
        engine.setProperty("voice", "english")
        fname = os.path.join(f"conversions/{fname}")
        engine.save_to_file(text, fname)
        time.sleep(1)
        engine.runAndWait()
        while not os.path.exists(fname):
            print("waiting")
            time.sleep(1)
    return True
