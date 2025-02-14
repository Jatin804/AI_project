import pygame
from PIL import Image, ImageSequence
import get_speech

pygame.init()

# display rendering 
display_info = pygame.display.Info()
WIDTH, HEIGHT = display_info.current_w, display_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

# main gif variable
gif = Image.open("gif2.gif")
frames = [pygame.image.fromstring(frame.convert("RGBA").tobytes(), frame.size, "RGBA") for frame in ImageSequence.Iterator(gif)]
gif_width, gif_height = gif.size
frame_rect = pygame.Rect(0,0, gif_width, gif_height)



# Listening process
sentence = "i am a robot"                 # get_speech.voice_to_text() # The text that determines size changes
word_lengths = [len(word) for word in sentence.split()]  # [1, 2, 1, 5]
print(f"Scaling pattern based on word lengths: {word_lengths}")



# Animation variables
frame_index = 0
clock = pygame.time.Clock()

# Scale transition variables
word_index = 0  # Which word's length we are using
scale_factor = 1.0  # Initial scale factor
target_scale = 1.0 + word_lengths[word_index] * 0.1 
scale_speed = 0.1  # Speed of transition




running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = screen.get_size()  # Update screen size

    screen.fill((0, 0, 0))  # Black background

    # Smooth transition towards target scale
    if scale_factor < target_scale:
        scale_factor += scale_speed
    elif scale_factor > target_scale:
        scale_factor -= scale_speed

    # Apply scaling
    scaled_frame = pygame.transform.scale(frames[frame_index], 
        (int(gif_width * scale_factor), int(gif_height * scale_factor)))
    
    # Center the GIF
    scaled_rect = scaled_frame.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Display the frame
    screen.blit(scaled_frame, scaled_rect)

    # Update frame index for animation loop
    frame_index = (frame_index + 1) % len(frames)

    # Change scaling based on word length every few frames
    if frame_index % 10 == 0:  # Change every 10 frames
        word_index = (word_index + 1) % len(word_lengths)  # Loop through word lengths
        target_scale = 1.0 + word_lengths[word_index] * 0.1  # Update target scale

    pygame.display.flip()  # Update the display
    clock.tick(40)  # Adjust speed (FPS)

pygame.quit()
