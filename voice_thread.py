from PyQt5.QtCore import QThread, pyqtSignal
import speech_recognition as sr

class VoiceThread(QThread):
    result_signal = pyqtSignal(str)

    def run(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio)
                self.result_signal.emit(text)
        except sr.UnknownValueError:
            self.result_signal.emit("[ERROR] Could not understand the audio.")
        except sr.RequestError as e:
            self.result_signal.emit(f"[ERROR] API request error: {e}")
        except Exception as e:
            self.result_signal.emit(f"[ERROR] {type(e).__name__}: {str(e)}")


# voice = VoiceThread()
# text = voice.run()
# print(text)