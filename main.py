import pygame
import time
from decoder import KeyDecoder, save_durations_to_file
from cytolk import tolk
from sine import SineWavePlayer

# Initialize Pygame
pygame.init()

# Set up display
width, height = 500, 500
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Morse Decoder")

# Set up font
font = pygame.font.Font(None, 36)

# Initialize variables
key_decoder = KeyDecoder()
sine=SineWavePlayer()
t = 0
pressed = False
text = ""

def elapsed(reset=False):
    global t
    current_time = time.time()
    elapsed_time = current_time - t if t > 0 else 0.0
    if reset:
        t = current_time
    return round(elapsed_time * 1000)

with tolk.tolk():
    tolk.speak("Press space to start decoding morse code. Press space again to stop decoding.")
    running=True  # loopbreaker
    while running:
        win.fill((255, 255, 255))
        # Display the text
        txt_surface = font.render(text, True, (0, 0, 0))
        win.blit(txt_surface, (20, 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if not pressed:
                        sine.play()
                        elapsed_time = elapsed(True)
                        if elapsed_time > 2000:
                            key_decoder.clear()
                            text = ""
                        else:
                            key_decoder.add_pause(elapsed_time)
                            text = key_decoder.decode()
                    pressed = True
            elif event.type == pygame.KEYUP:
                # if key enter released, speak the text
                if event.key == pygame.K_RETURN:
                    tolk.speak(text)
                if event.key == pygame.K_SPACE:
                    pressed = False
                    sine.stop()
                    elapsed_time = elapsed(True)
                    if elapsed_time > 2000:
                        save_durations_to_file(key_decoder.morse_code, "durs.json")
                        key_decoder.clear()
                        text = ""
                    else:
                        key_decoder.add_beep(elapsed_time)
                        text = key_decoder.decode()

        pygame.display.flip()

pygame.quit()
