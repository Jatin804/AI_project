import sys
import os
import re
import subprocess
import pyttsx3
import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QMovie, QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Ensure you have the Groq library installed: pip install groq
from groq import Groq

# --- Configuration & Global Setup ---

# Initialize Text-to-Speech Engine
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Try to set a female voice if available, otherwise default to the first one
    female_voice_found = False
    for voice in voices:
        if 'female' in voice.name.lower() or voice.gender == 'female':
            engine.setProperty('voice', voice.id)
            female_voice_found = True
            break
    if not female_voice_found and voices:
        engine.setProperty('voice', voices[0].id)
    elif not voices:
        print("[WARNING] No voices found for pyttsx3. Speech output will not work.")
    engine.setProperty('rate', 180)
except Exception as e:
    print(f"[ERROR] Failed to initialize pyttsx3: {e}. Speech output will not work.")
    engine = None # Set to None if initialization fails

def speak_message(text):
    if engine and text:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[TTS Error] Could not speak message: {e}")
    elif not engine:
        print(f"[TTS Not Initialized] Attempted to speak: '{text}'")


def extract_shell_commands(text):
    # Regex to find commands within triple backticks (```) optionally followed by 'bash'
    # and single lines that look like commands (e.g., 'ls -l', 'sudo apt update')
    block_cmds = re.findall(r"```(?:bash)?\n(.*?)```", text, re.DOTALL)
    # This regex is more robust for single-line commands
    # It captures lines that start with an optional '$' or whitespace,
    # followed by a word (command name) and then anything else until a newline.
    # It avoids capturing lines that are clearly not commands (e.g., plain sentences).
    line_cmds = re.findall(r"^\s*(?:[a-zA-Z0-9._/-]+\s+[^\n]+|[a-zA-Z0-9._/-]+)\s*$", text, re.MULTILINE)

    commands = []
    # Process block commands first
    for cmd_block in block_cmds:
        for line in cmd_block.strip().split('\n'):
            cleaned = line.strip()
            # Filter out comments and common non-command phrases
            if cleaned and not cleaned.startswith("#") and not cleaned.lower().startswith("run"):
                commands.append(cleaned)

    # Process single-line commands
    for cmd_line in line_cmds:
        cleaned = cmd_line.strip()
        # Ensure it's not already captured in block_cmds or is a duplicate
        if cleaned and cleaned not in commands and \
           not cleaned.startswith("#") and not cleaned.lower().startswith("run"):
            commands.append(cleaned)
            
    return commands


def execute_shell_command(command_str):
    try:
        # Use subprocess.run for safer and more flexible execution
        # stdout and stderr are captured and returned as text
        result = subprocess.run(command_str, shell=True, capture_output=True, text=True, check=False)
        return result
    except Exception as e:
        print(f"Error executing command '{command_str}': {e}")
        return None

# --- API Integration ---
# Recommended: Set your Groq API key as an environment variable (e.g., GROQ_API_KEY)
# If not set, you can hardcode it here for testing, but NOT recommended for production.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY") # REPLACE "YOUR_GROQ_API_KEY"

def should_respond(text: str) -> bool:
    linux_keywords = [
        "build", "compile", "create", "enable", "disable", "execute", "find", "install",
        "list", "make", "open", "purge", "remove", "restart", "run", "search", "show",
        "start", "status", "stop", "uninstall", "update", "upgrade", "whereis", "which",
        "cat", "cd", "cp", "head", "less", "ls", "mkdir", "more", "mv", "nano",
        "pwd", "rm", "rmdir", "tail", "touch", "vi", "vim",
        "chgrp", "chmod", "chown", "umask",
        "df", "du", "free", "htop", "id", "kill", "killall", "nice", "ps", "renice",
        "top", "uptime", "w", "who",
        "curl", "dig", "ftp", "host", "ifconfig", "ip", "iwconfig", "netstat",
        "nmcli", "ping", "scp", "ssh", "ss", "telnet", "traceroute", "wget",
        "7z", "gzip", "gunzip", "tar", "unzip", "xz", "zip",
        "flatpak", "snap", "zypper", # openSUSE-specific + optional tools
        "journalctl", "reboot", "service", "shutdown", "systemctl",
        "btrfs", "blkid", "fdisk", "lsblk", "mount", "parted", "umount",
        "alias", "bash", "fish", "sh", "source", "tty", "zsh", "export",
        "awk", "cut", "diff", "grep", "sed", "sort", "tr", "uniq", "wc",
        "cmake", "docker", "g++", "gcc", "git", "kubectl", "kubernetes", "make",
        "node", "python",
        "at", "command", "crontab", "date", "shell", "terminal", "time"
    ]
    return any(word in text.lower() for word in linux_keywords)


def chat_with_llama(user_input: str) -> str:
    if not should_respond(user_input):
        return "Sorry, I only assist with Linux command-line usage. Please ask a related question."

    if GROQ_API_KEY == "YOUR_GROQ_API_KEY" or not GROQ_API_KEY:
        return "Error: Groq API key is not configured. Please set GROQ_API_KEY environment variable or replace the placeholder."

    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        return f"Error initializing Groq client: {str(e)}"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Linux command assistant. "
                "ONLY answer questions about Linux commands. "
                "Give output ONLY as one Linux command. "
                "Do NOT explain anything. "
                "If a user asks anything unrelated, reply: 'I can only help with Linux commands.'"
                "Ensure the command is complete and executable. Do not include introductory phrases like 'Here is the command:'."
                "Do not put commands in code blocks unless they are multi-line scripts."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192", # Or "llama3-8b-8192" for faster, smaller model
            messages=messages,
            temperature=0.7, # Slightly lower temperature for more predictable commands
            max_tokens=256,  # Reduced max_tokens as commands are usually short
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[API Error] Failed to get response from Llama: {str(e)}")
        return f"An API error occurred: {str(e)}"


# --- Voice Thread ---
class VoiceThread(QThread):
    result_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str) # New signal for specific errors

    def run(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        try:
            with mic as source:
                self.result_signal.emit("[INFO] Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1) # Adjust duration
                self.result_signal.emit("[INFO] Listening for voice command...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio)
                self.result_signal.emit(text)
        except sr.UnknownValueError:
            self.error_signal.emit("[ERROR] Could not understand the audio.")
        except sr.WaitTimeoutError:
            self.error_signal.emit("[ERROR] No speech detected within timeout.")
        except sr.RequestError as e:
            self.error_signal.emit(f"[ERROR] Speech recognition API error: {e}")
        except Exception as e:
            self.error_signal.emit(f"[ERROR] Voice input general error: {type(e).__name__}: {str(e)}")


# --- GUI MODE ---
class SystemAIGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SYSTEMAI Desktop Assistant")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #121212; color: white;")
        self.voice_thread = None
        self.listening = False
        self.init_ui()

    def init_ui(self):
        self.gif_label = QLabel()
        self.gif_label.setFixedSize(600, 600)
        self.gif_label.setStyleSheet("border: 2px solid #00FFFF; border-radius: 10px;")
        
        # Ensure these asset paths are correct
        try:
            self.blank_image = QPixmap("assets/black_image_600x600.png")
        except Exception as e:
            print(f"[ERROR] Could not load blank image: {e}. Using a fallback.")
            self.blank_image = QPixmap(600, 600)
            self.blank_image.fill(Qt.black)

        try:
            self.movie = QMovie("assets/gif.gif")
            self.movie.setScaledSize(self.gif_label.size())
        except Exception as e:
            print(f"[ERROR] Could not load GIF: {e}. Animation will not work.")
            self.movie = None

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
        
        self.output_box.append("Welcome to SYSTEMAI Desktop Assistant!")
        self.output_box.append("Choose a mode from the console or click 'Start' for GUI voice mode.")

    def set_idle_state(self):
        if self.movie:
            self.movie.stop()
        self.gif_label.setPixmap(self.blank_image)

    def start_system_ai(self):
        if self.listening:
            self.output_box.append("[!] Already listening...")
            return
        
        if self.movie:
            self.gif_label.setMovie(self.movie)
            self.movie.start()
            
        self.output_box.append("[+] SYSTEMAI started. Initializing voice input...")
        speak_message("System AI started.")
        self.listening = True
        self.listen_voice_input()

    def stop_system_ai(self):
        self.set_idle_state()
        self.listening = False
        self.output_box.append("[-] SYSTEMAI stopped.")
        speak_message("System AI stopped.")
        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.terminate() # Request termination
            self.voice_thread.wait()     # Wait for thread to finish

    def listen_voice_input(self):
        if not self.listening: # Ensure we are still in listening mode
            return

        if self.voice_thread and self.voice_thread.isRunning():
            self.output_box.append("[!] Voice thread already running. Waiting for current input.")
            return

        self.voice_thread = VoiceThread()
        self.voice_thread.result_signal.connect(self.process_transcription)
        self.voice_thread.error_signal.connect(self.handle_voice_error) # Connect new error signal
        self.voice_thread.start() # Start the thread

    def handle_voice_error(self, error_message):
        self.output_box.append(error_message)
        speak_message("I didn't catch that. Please try again.")
        # Decide whether to restart listening immediately or wait
        if self.listening: # Only restart if still in listening mode
            self.listen_voice_input()

    def process_transcription(self, text):
        # A result_signal can also be an INFO message from VoiceThread
        if text.startswith("[INFO]"):
            self.output_box.append(text)
            return

        if not self.listening: # Ensure we are still in listening mode
            return

        self.output_box.append(f"[You] {text}")
        speak_message("Processing your input.")
        
        ai_response = chat_with_llama(text)
        
        # Check if AI response is an error message
        if ai_response.startswith("Error:") or ai_response.startswith("An API error occurred:"):
            self.output_box.append(f"[AI Error] {ai_response}")
            speak_message("I'm having trouble connecting to the AI. Please check your internet or API key.")
            self.listen_voice_input() # Continue listening
            return

        if not ai_response:
            self.output_box.append("[!] AI did not respond with a command.")
            speak_message("AI did not respond with a valid command.")
            self.listen_voice_input() # Continue listening
            return

        self.output_box.append(f"[AI] {ai_response}")
        speak_message("I've received a command. Attempting to execute.")
        
        commands = extract_shell_commands(ai_response)

        if commands:
            for cmd in commands:
                self.output_box.append(f"[Executing] {cmd}")
                result = execute_shell_command(cmd)
                if result:
                    if result.returncode == 0:
                        self.output_box.append(f"[✔ Success] Command: {cmd}\nOutput:\n{result.stdout}")
                        speak_message(f"Executed command: {cmd}")
                    else:
                        self.output_box.append(f"[✘ Failed] Command: {cmd}\nError:\n{result.stderr}\nReturn Code: {result.returncode}")
                        speak_message(f"Command failed with error: {result.stderr or 'No specific error'}")
                else:
                    self.output_box.append(f"[✘ Error] Failed to run command: {cmd} (Unknown error)")
                    speak_message("Command execution failed.")
        else:
            self.output_box.append("[!] No valid command found in AI response.")
            speak_message("AI did not provide a valid command.")
            
        self.listen_voice_input() # Continue listening for next input

# --- CLI MODE ---
def handle_voice_result_cli(text):
    if text.startswith("[INFO]"):
        print(text)
        return

    print("Recognized Voice:", text)
    if text.startswith("[ERROR]"):
        speak_message("I didn't catch that. Please try again.")
        return # Don't process errors as commands

    speak_message("Processing your input.")
    response = chat_with_llama(text)
    print("LLM Response:", response)
    
    if response.startswith("Error:") or response.startswith("An API error occurred:"):
        print(f"[CLI Error] {response}")
        speak_message("I'm having trouble connecting to the AI. Please check your internet or API key.")
        return

    commands = extract_shell_commands(response)
    if commands:
        for command in commands:
            print(f"Executing: {command}")
            result = execute_shell_command(command)
            if result:
                if result.returncode == 0:
                    speak_message("Command executed successfully.")
                    print("Output:", result.stdout)
                else:
                    speak_message("Command execution failed.")
                    print("Error:", result.stderr)
                    print("Return Code:", result.returncode)
            else:
                speak_message("Command execution failed due to an unknown error.")
                print("Error: Unknown execution error.")
    else:
        print("[!] No valid command found in AI response.")
        speak_message("AI did not provide a valid command.")

# --- ENTRY POINT ---
if __name__ == "__main__":
    # Ensure QApplication is created only once and before any widgets/threads
    app = QApplication(sys.argv)

    mode = input("Choose mode: (1) GUI, (2) CLI Voice, (3) CLI Text: ")

    if mode == "1":
        window = SystemAIGUI()
        window.show()
        sys.exit(app.exec_())

    elif mode == "2":
        print("Starting CLI Voice Mode. Speak into your microphone...")
        speak_message("Starting CLI Voice Mode.")
        voice_cli_thread = VoiceThread()
        voice_cli_thread.result_signal.connect(handle_voice_result_cli)
        voice_cli_thread.error_signal.connect(lambda msg: print(msg)) # Print errors directly
        voice_cli_thread.start()
        sys.exit(app.exec_()) # Keep the application running for voice thread

    elif mode == "3":
        print("Starting CLI Text Mode.")
        speak_message("Starting CLI Text Mode.")
        text = input("Enter your command: ")
        response = chat_with_llama(text)
        print("LLM Response:", response)
        
        if response.startswith("Error:") or response.startswith("An API error occurred:"):
            print(f"[CLI Error] {response}")
            speak_message("I'm having trouble connecting to the AI. Please check your internet or API key.")
            sys.exit(1) # Exit with an error code
            
        commands = extract_shell_commands(response)
        if commands:
            for command in commands:
                print(f"Executing: {command}")
                result = execute_shell_command(command)
                if result:
                    if result.returncode == 0:
                        speak_message(result.stdout) # Speak stdout for success
                        print("Output:", result.stdout)
                    else:
                        speak_message(result.stderr or "Command failed with an error.") # Speak stderr for failure
                        print("Error:", result.stderr)
                        print("Return Code:", result.returncode)
                else:
                    speak_message("Command execution failed due to an unknown error.")
                    print("Error: Unknown execution error.")
        else:
            print("[!] No valid command found in AI response.")
            speak_message("AI did not provide a valid command.")
        sys.exit(0) # Exit after processing text command

    else:
        print("Invalid option. Please choose 1, 2, or 3.")
        sys.exit(1) # Exit with an error code