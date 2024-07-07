from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import docx
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
import os
import pytesseract
from PIL import Image


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    document = fitz.open(pdf_path)
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text  # Remove leading/trailing whitespace
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def extract_text(file_path):
    if file_path.lower().endswith(('.pdf', '.docx')):
        return extract_text_from_pdf(file_path) if file_path.lower().endswith('.pdf') \
               else extract_text_from_docx(file_path)
    elif file_path.lower().endswith(('png', 'jpg', 'jpeg')):
        return extract_text_from_image(file_path)
    else:
        return ""


def translate_text(text, target_language):
    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        if translated and translated.text:
            return translated.text
        else:
            raise ValueError("Translation returned None or empty text.")
    except Exception as e:
        print(f"Error translating text: {e}")
        return "Error translating text."

def text_to_speech(text, language, output_path):
    tts = gTTS(text=text, lang=language)
    tts.save(output_path)

def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        target_language = request.form['language']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        extracted_text = extract_text(file_path)
        translated_text = translate_text(extracted_text, target_language)

        tts_output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'translated_speech.mp3')
        text_to_speech(translated_text, target_language, tts_output_path)

        return render_template('index.html', extracted_text=extracted_text, translated_text=translated_text, tts_output_path=tts_output_path)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True)
