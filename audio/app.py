from flask import Flask, render_template, request, jsonify
import speech_recognition as sr

app = Flask(__name__)

# Initialize the recognizer
recognizer = sr.Recognizer()

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to receive and store the recorded audio
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'})

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Save the audio file to a temporary location or process it directly
    # For demonstration purposes, we'll simply return a success message
    return jsonify({'message': 'Audio uploaded successfully'})

# Endpoint to process the uploaded audio and perform speech-to-text
@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'})

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Recognize speech using SpeechRecognition
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)  # Read the entire audio file

    try:
        text = recognizer.recognize_google(audio_data)
        return jsonify({'text': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'})
    except sr.RequestError as e:
        return jsonify({'error': f'Speech recognition error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
