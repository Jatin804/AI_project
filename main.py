from PyQt5.QtWidgets import QApplication
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QMovie, QPixmap, QFont
from PyQt5.QtCore import Qt
from voice_thread import VoiceThread
from speak_clean import speak_message, extract_shell_commands, execute_shell_command
from api import chat_with_llama

class SystemAIGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SYSTEMAI Desktop Assistant")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #121212; color: white;")
        self.voice_thread = None
        self.init_ui()

    def init_ui(self):
        self.gif_label = QLabel()
        self.gif_label.setFixedSize(600, 600)
        self.gif_label.setStyleSheet("border: 2px solid #00FFFF; border-radius: 10px;")

        self.blank_image = QPixmap("assets/black_image_600x600.png")
        self.movie = QMovie("assets/gif.gif")
        self.movie.setScaledSize(self.gif_label.size())
        self.set_idle_state()

        version_label = QLabel("SYSTEMAI\nVersion: 3.0.1\nStatus: Good")
        version_label.setFont(QFont("Consolas", 10))
        version_label.setAlignment(Qt.AlignTop)
        version_label.setStyleSheet("border: 1px solid #00FFFF; padding: 10px; border-radius: 5px; background-color: #1e1e1e;")

        self.start_btn = QPushButton("▶ Start")
        self.stop_btn = QPushButton("■ Stop")
        style = """QPushButton { background-color: #0d7377; color: white; border: 1px solid #14ffec; border-radius: 8px; padding: 10px; }
                   QPushButton:hover { background-color: #14ffec; color: #0d1b2a; }"""
        self.start_btn.setStyleSheet(style)
        self.stop_btn.setStyleSheet(style)
        self.start_btn.setFixedWidth(120)
        self.stop_btn.setFixedWidth(120)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont("Courier", 10))
        self.output_box.setStyleSheet("background-color: #1e1e1e; color: #14ffec; border-radius: 8px; padding: 8px;")

        right_layout = QVBoxLayout()
        right_layout.addWidget(version_label)
        right_layout.addSpacing(10)
        right_layout.addLayout(button_layout)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.output_box)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.gif_label)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        self.start_btn.clicked.connect(self.start_system_ai)
        self.stop_btn.clicked.connect(self.stop_system_ai)

    def set_idle_state(self):
        self.movie.stop()
        self.gif_label.setPixmap(self.blank_image)

    def start_system_ai(self):
        if self.voice_thread and self.voice_thread.isRunning():
            self.output_box.append("[!] Already listening...")
            return
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        self.output_box.append("[+] SYSTEMAI started. Listening...")
        self.listen_voice_input()


    def stop_system_ai(self):
        self.set_idle_state()
        self.output_box.append("[-] SYSTEMAI stopped.")

    def listen_voice_input(self):
        try:
            self.voice_thread = VoiceThread()
            self.voice_thread.result_signal.connect(self.process_transcription)
            self.voice_thread.start()
        except Exception as e:
            self.output_box.append(f"[Error] Voice input failed: {e}")
            speak_message("Voice input failed.")


    def process_transcription(self, text):
        self.output_box.append(f"[Voice] {text}")
        speak_message("Processing your input.")

        ai_response = chat_with_llama(text)                     # API call 
        if not ai_response:
            self.output_box.append("[!] AI did not respond.")
            speak_message("AI did not respond.")
            return
        
        self.output_box.append(f"[AI] {ai_response}")
        speak_message("Done processing.")
        commands = extract_shell_commands(ai_response)

        if commands:
            for cmd in commands:
                result = execute_shell_command(cmd)
                if result and result.returncode == 0:
                    self.output_box.append(f"[✔] {cmd}\n{result.stdout}")
                    speak_message(f"Executed command: {cmd}")
                else:
                    err = result.stderr if result else "Unknown error"
                    self.output_box.append(f"[✘] Failed to run: {cmd}\n{err}")
                    speak_message("Command failed.")
        else:
            self.output_box.append("[!] No valid command found.")
            speak_message("No valid command found.")


        
        self.listen_voice_input()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemAIGUI()
    window.show()
    sys.exit(app.exec_())
