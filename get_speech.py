import os
import speech_recognition as sr

os.environ["ALSA_LOG_LEVEL"] = "none"

recognizer = sr.Recognizer()
recognizer.pause_threshold = 2.5
# recognizer.energy_threshold = 100

def capture_voice():
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise, please wait...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            print("Listening...")
            text = recognizer.listen(source)

        return text
    
    except sr.WaitTimeoutError:
        print("No speech detected within the time limit. Try again.")
        return None
    except Exception as e:
        print(f"Error capturing voice: {e}")
        return None

def voice_to_text():
    audio = capture_voice()

    if not audio:
        return "text No speech detected"
    
    try:
        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        return f"Error : In generating"

