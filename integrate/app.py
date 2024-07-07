from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import docx
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
import os
import pytesseract
from PIL import Image
from PIL import ImageEnhance, ImageFilter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the recognizer
recognizer = sr.Recognizer()

# Helper functions
def extract_text_from_pdf(pdf_path):
    text = ""
    document = fitz.open(pdf_path)
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        page_text = page.get_text("text")
        lines = [line for line in page_text.split('\n') if line.strip()]
        text += '\n'.join(lines)
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = []
    for para in doc.paragraphs:
        lines = [line.text for line in para.runs if line.text.strip()]
        text.extend(lines)
    return "\n".join(text)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(img):
    img_gray = img.convert('L')
    enhancer = ImageEnhance.Contrast(img_gray)
    img_enhanced = enhancer.enhance(2.0)
    img_threshold = img_enhanced.point(lambda x: 0 if x < 128 else 255, '1')
    return img_threshold

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        img_preprocessed = preprocess_image(img)
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img_preprocessed, config=custom_config)
        return text.strip()
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
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_language = request.form['language']

        file = request.files.get('file')
        audio = request.files.get('audio')

        extracted_text = ""
        translated_text = ""
        tts_output_path = ""

        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            extracted_text = extract_text(file_path)

        if audio and audio.filename:
            audio_filename = secure_filename(audio.filename)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            audio.save(audio_path)
            extracted_text = speech_to_text(audio_path)

        if extracted_text:
            translated_text = translate_text(extracted_text, target_language)
            tts_output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'translated_speech.mp3')
            text_to_speech(translated_text, target_language, tts_output_path)

        return render_template('index.html', extracted_text=extracted_text, translated_text=translated_text, tts_output_path=tts_output_path)

    return render_template('index.html')

@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'})

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Save the audio file to a temporary location
    filename = secure_filename(audio_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(file_path)

    # Recognize speech using SpeechRecognition
    try:
        text = speech_to_text(file_path)
        return jsonify({'text': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'})
    except sr.RequestError as e:
        return jsonify({'error': f'Speech recognition error: {str(e)}'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True)
