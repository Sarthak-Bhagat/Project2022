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


def extract_text_from_file(file):
    """

    Extracts text data from a file based on the file extension using Python libraries such as OpenCV, pytesseract, docx2txt,

    pdf2image, and unoconv.


    Args:

    file: the file to be processed.


    Returns:

    The extracted text data as a string.
    """

    filename = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

    fname, ext = os.path.splitext(file.filename)


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

        try:

            output = docx2txt.process(filename)

        except:

            return "Could not extract text from the document."


    elif ext == ".pdf":

        try:

            pages = convert_from_path(filename)
            output = ""

            for _, page_data in enumerate(pages):

                output += "\n" + pytesseract.image_to_string(page_data)

        except:

            return "Could not extract text from the document."


    elif ext == ".txt":

        try:

            with open(filename, "r") as file:
                output = file.read()

        except:

            return "Could not read the text file."

    elif ext == ".odt":
        doc = load(filename)

        output = teletype.extractText(doc).strip()

    print(output)

    return output



def text_to_speech(input_text, filename, high_qual=False):
    """
    Generates an audio file from input text and saves it to a specified filename.

    Args:
        input_text (str): The text to convert to speech.
        filename (str): The name of the file to save the audio to.
        high_qual (bool): Whether to generate high quality audio or not. Defaults to False.

    Returns:
        None
    """
    filename = os.path.join(f"conversions/{filename}")
    print(filename)

    if high_qual:
        tts = gTTS(text=input_text, lang="en", slow=False)
        tts.save(filename)
    else:
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.7)
        engine.setProperty("voice", "en-us")
        engine.save_to_file(input_text, filename)
        engine.runAndWait()

    while not os.path.exists(filename):
        print("waiting")
        time.sleep(1)