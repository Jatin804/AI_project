import pyttsx3
import subprocess
import re

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 180)

def speak_message(text):
    try:
        if text:
            engine.say(text)
            engine.runAndWait()
    except Exception as e:
        print(f"[TTS Error] {e}")



def extract_shell_commands(text):
    block_cmds = re.findall(r"```(?:bash)?\n(.*?)```", text, re.DOTALL)
    line_cmds = re.findall(r"^(?:\$?\s*)?([a-zA-Z0-9._/-]+\s+[^\n]+)", text, re.MULTILINE)
    
    commands = []
    for cmd in block_cmds + line_cmds:
        for line in cmd.strip().split('\n'):
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("#") and not cleaned.lower().startswith("run"):
                commands.append(cleaned)
    return commands


def execute_shell_command(command_str):
    try:
        result = subprocess.run(command_str, shell=True, capture_output=True, text=True)
        return result
    except Exception as e:
        print(f"Error executing command: {e}")
        return None
