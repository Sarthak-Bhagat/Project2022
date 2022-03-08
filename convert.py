import pytesseract
from PIL import Image
import cv2
import docx
import pdftotext
from gtts import gTTS
import pyttsx3


def ocr(f, high_qual):
    ext = f.filename.split(".")[-1]
    output = "Something went wrong"

    if ext in ["png", "jpg", "jpeg"]:
        image = cv2.imread(f.filename)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        threshold_img = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )[1]
        custom_config = r"--oem 3 --psm 6"
        output = pytesseract.image_to_string(threshold_img, config=custom_config)

    elif ext in ["docx", "doc"]:
        doc = docx.Document(f)
        output = ""
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
            output = "\n".join(fullText)

    elif ext == "pdf":

        high_qual = False
        with open(f.filename, "rb") as fi:
            output = pdftotext.PDF(fi)
        output = "\n\n".join(output)

    print("Converting to audio")
    if high_qual == True:
        tts = gTTS(text=output, lang="en")
        tts.save("output.mp3")
    else:
        engine = pyttsx3.init()
        engine.setProperty("voice", "english")
        engine.save_to_file(output, "output.mp3")
        engine.runAndWait()
    return True
