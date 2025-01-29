import os
from django.http import JsonResponse
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

            # Calculate loudness (RMS energy)
            loudness = sum(abs(sample) for sample in text.frame_data) / len(text.frame_data)

        return text, loudness

    except sr.WaitTimeoutError:
        print("No speech detected within the time limit. Try again.")
        return None
    except Exception as e:
        print(f"Error capturing voice: {e}")
        return None

def voice_to_text(audio, loudness):

    # audio, loudness = capture_voice()

    if not audio:
        return JsonResponse({"text": "No speech detected", "loudness": 0})
    
    try:
        text = recognizer.recognize_google(audio)
        return JsonResponse({"text": text, "loudness": loudness})
    
    except sr.UnknownValueError:
        return JsonResponse({"text": "Sorry, I couldn't understand you.", "loudness": 0})
    
    except sr.RequestError as e:
        return JsonResponse({"text": f"Error with recognition service: {e}", "loudness": 0})
    
    except Exception as e:
        return JsonResponse({"text": f"Unexpected error: {e}", "loudness": 0})





# audio_data = capture_voice()
# if audio_data:
#     response = voice_to_text(audio_data)
#     print(response)
# else:
#     print("No audio captured or timeout occurred.")
