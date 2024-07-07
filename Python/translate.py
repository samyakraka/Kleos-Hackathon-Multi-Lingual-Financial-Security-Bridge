import fitz  # PyMuPDF
import docx
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
import os

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using PyMuPDF.
    """
    try:
        text = ""
        document = fitz.open(pdf_path)
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return ""

def extract_text_from_docx(docx_path):
    """
    Extracts text from a DOCX file using python-docx.
    """
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error processing DOCX file {docx_path}: {e}")
        return ""

def extract_text(file_path):
    """
    Determines the file type and calls the appropriate extraction function.
    """
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file format: {file_path}")
        return ""

def translate_text(text, target_language):
    """
    Translates text to the target language using googletrans.
    """
    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return ""

def text_to_speech(text, language, output_path):
    """
    Converts text to speech using gTTS.
    """
    try:
        tts = gTTS(text=text, lang=language)
        tts.save(output_path)
        print(f"Saved speech to {output_path}")
    except Exception as e:
        print(f"Error converting text to speech: {e}")

def speech_to_text(audio_path):
    """
    Converts speech to text using SpeechRecognition.
    """
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return text
    except Exception as e:
        print(f"Error converting speech to text: {e}")
        return ""

# Example usage
if __name__ == "__main__":
    # Specify the path to your file
    file_path = 'E:\\Code Playground\\kleos\\Python\\sample1.docx'
    
    # Extract text based on the file type
    extracted_text = extract_text(file_path)
    print("Extracted Text:")
    print(extracted_text)

    # Translate the text
    target_language = 'de'  
    translated_text = translate_text(extracted_text, target_language)
    print("Translated Text:")
    print(translated_text)

    # Convert translated text to speech
    tts_output_path = 'translated_speech.mp3'
    text_to_speech(translated_text, target_language, tts_output_path)

    # Convert speech to text (example, use your own audio file)
    stt_input_path = 'sample.mp3'
    recognized_text = speech_to_text(stt_input_path)
    print("Recognized Text from Speech:")
    print(recognized_text)
