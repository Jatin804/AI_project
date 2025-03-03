import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
import get_speech  # Your voice-to-text module

# Create Tkinter window
root = tk.Tk()
root.title("GIF Animation with Speech")
root.geometry("500x500")  # Small window

# Load GIF
gif = Image.open("gif2.gif")
frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(gif)]

# Label to display GIF
gif_label = tk.Label(root)
gif_label.pack()

# Label to display speech text
sentence = tk.StringVar()
sentence.set("Listening...")
text_label = tk.Label(root, textvariable=sentence, font=("Arial", 14), fg="white", bg="black")
text_label.pack(pady=10)

def animate(index=0):
    """Loop through GIF frames."""
    gif_label.config(image=frames[index])
    root.after(40, animate, (index + 1) % len(frames))

def speech_recognition():
    """Update text label with speech recognition."""
    while True:
        try:
            sentence.set(get_speech.voice_to_text())  # Replace with real speech input
        except Exception:
            sentence.set("Error in speech recognition")

# Start animation and speech recognition in parallel
threading.Thread(target=speech_recognition, daemon=True).start()
animate()




root.mainloop()
