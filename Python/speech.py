import speech_recognition as sr
import pyaudio

# Initialize recognizer
recognizer = sr.Recognizer()

# Define the microphone stream
mic = sr.Microphone()

def recognize_audio():
    with mic as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
        print("Recording...")

        while True:
            print("Listening...")
            audio = recognizer.listen(source)
            try:
                print("Recognizing...")
                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio)
                print(f"Recognized Text: {text}")
            except sr.UnknownValueError:
                print("Google Web Speech API could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")

if __name__ == "__main__":
    recognize_audio()
