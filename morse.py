import tkinter as tk
import pygame
import base64
from io import BytesIO
import numpy as np
import struct
import wave
import threading

# Morse code dictionary
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', 
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', 
    '9': '----.', '0': '-----', ' ': ' ', '!': '-.-.--', '?': '..--..', '.': '.-.-.-', ',': '--..--'
}

def sine_samples(freq, duration, framerate=44100, amplitude=0.5):
    X = (2*np.pi*freq/framerate) * np.arange(framerate*duration)
    S = (amplitude*32767*np.sin(X)).astype(int)
    as_packed_bytes = (map(lambda v: struct.pack('h', v), S))
    return b''.join(as_packed_bytes)

def create_sound(freq, duration, framerate=44100):
    frames = sine_samples(freq, duration, framerate)
    data_buffer = BytesIO()
    with wave.open(data_buffer, 'wb') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(framerate)
        wf.writeframes(frames)
    return data_buffer.getvalue()

# Generate sound data for the Morse code signals
framerate = 44100
beep_freq = 800
dit_duration = 0.1
dah_duration = 0.3

dit_sound = create_sound(beep_freq, dit_duration, framerate)
dah_sound = create_sound(beep_freq, dah_duration, framerate)

# Initialize pygame for sound
pygame.mixer.init(frequency=framerate)

def play_sound(sound_data):
    sound = pygame.mixer.Sound(BytesIO(sound_data))
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))

def play_morse_sound(morse_code, char):
    highlight_key(char)
    for symbol in morse_code:
        if symbol == '.':
            play_sound(dit_sound)
        elif symbol == '-':
            play_sound(dah_sound)
        pygame.time.wait(100)  # delay between sounds
    reset_key(char)

def char_to_morse(char):
    char = char.upper()
    if char in MORSE_CODE_DICT:
        morse_code = MORSE_CODE_DICT[char]
        threading.Thread(target=play_morse_sound, args=(morse_code, char)).start()
        morse_display.insert(tk.END, morse_code + ' ')
        morse_display.see(tk.END)
    elif char == '\x08':  # Backspace
        morse_display.delete("end-2c", "end-1c")

def highlight_key(char): 
    for key, label in key_labels.items(): 
        if key == char: 
            label.config(bg='yellow', fg='black') 
        else: 
            label.config(bg='black', fg='white')

def reset_key(char): 
    if char in key_labels: 
        key_labels[char].config(bg='black', fg='white')

# Create the main window
root = tk.Tk()
root.title("Morse Code Keyboard")
root.configure(bg='black')
root.geometry("1000x600")  # Make the window bigger

# Create a frame for the Morse code display
display_frame = tk.Frame(root, bg='black')
display_frame.pack(fill=tk.BOTH, expand=True)

# Create a Text widget for displaying Morse code
morse_display = tk.Text(display_frame, height=4, bg='black', fg='white', font=('Courier', 24), wrap=tk.WORD)
morse_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
morse_display.tag_configure("center", justify='center')
morse_display.tag_add("center", 1.0, "end")

# Create a frame for the keyboard
keyboard_frame = tk.Frame(root, bg='black')
keyboard_frame.pack(expand=True)

# QWERTY layout with space bar and backspace
qwerty_layout = [
    "1234567890",
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM",
    ".,?!"
]

# Create labels for each key
key_labels = {}
for row_index, row in enumerate(qwerty_layout):
    row_frame = tk.Frame(keyboard_frame, bg='black')
    row_frame.pack(side=tk.TOP, expand=True)
    for col_index, char in enumerate(row):
        morse = MORSE_CODE_DICT.get(char, "")
        label = tk.Label(row_frame, text=f"{char}\n{morse}", fg='white', bg='black', font=('Courier', 16), width=6, height=3, relief='raised')
        label.pack(side=tk.LEFT, padx=5, pady=5)
        key_labels[char] = label

# Add a frame for the space bar and backspace key
bottom_row_frame = tk.Frame(keyboard_frame, bg='black')
bottom_row_frame.pack(side=tk.TOP, expand=True)

# Add a space bar
space_label = tk.Label(bottom_row_frame, text="SPACE", fg='white', bg='black', font=('Courier', 16), width=40, height=3, relief='raised')
space_label.pack(side=tk.LEFT, padx=5, pady=5)
key_labels[' '] = space_label

# Add a backspace key
backspace_label = tk.Label(bottom_row_frame, text="BACKSPACE", fg='white', bg='black', font=('Courier', 16), width=20, height=3, relief='raised')
backspace_label.pack(side=tk.LEFT, padx=5, pady=5)
key_labels['\x08'] = backspace_label

# Bind key press event
root.bind('<KeyPress>', lambda event: char_to_morse(event.char))

# Run the main loop
root.mainloop()