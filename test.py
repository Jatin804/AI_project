import speech_recognition as sr
import pygame
import numpy as np
import time
import os
from PIL import Image, ImageSequence
import audioop

os.environ["ALSA_LOG_LEVEL"] = "none"


# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

# Load GIF frames
def load_gif(gif_path):
    gif = Image.open(gif_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]
    return frames

# Convert PIL images to pygame surfaces
def pil_to_pygame(frames):
    return [pygame.image.fromstring(f.tobytes(), f.size, f.mode) for f in frames]

# Function to adjust GIF speed based on volume
def play_gif_reactive(frames, volume):
    frame_surfaces = pil_to_pygame(frames)
    speed = max(5, int(20 - volume / 200))  # Adjust speed based on volume
    for frame in frame_surfaces:
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        clock.tick(speed)  # Adjust speed dynamically

# Voice Processing
def get_microphone_volume():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Start speaking...")
        while True:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)
                volume = audioop.rms(audio.frame_data, 2)  # Get audio volume level
                print(f"Volume: {volume}")  
                return volume
            except sr.WaitTimeoutError:
                return 0

# Main Function
if __name__ == "__main__":
    frames = load_gif("gif2.gif")

    running = True
    while running:
        volume = get_microphone_volume()
        if volume > 0:  
            play_gif_reactive(frames, volume)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
