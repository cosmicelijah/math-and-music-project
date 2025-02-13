import tkinter as tk
import scipy.signal
import soundfile as sf
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
import scipy
from math import log2, pow
from scipy.signal import butter, filtfilt
from sheet_music import display_sheet_music

height = 800
width = 1800

root = tk.Tk()
root.title("Math and Music Final Project")

# Create a Frame for the labels and entry boxes
frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.1, anchor="center")  # Center the frame within the window

# Create the labels inside the frame
label_tempo = tk.Label(frame, text="Tempo")
label_tempo.grid(row=0, column=0, padx=10, pady=5)

label_time_signature = tk.Label(frame, text="Time signature")
label_time_signature.grid(row=1, column=0, padx=10, pady=5)

label_key_signature = tk.Label(frame, text="Key signature")
label_key_signature.grid(row=2, column=0, padx=10, pady=5)

# Create the text entry boxes inside the frame
entry_tempo = tk.Entry(frame)
entry_tempo.grid(row=0, column=1, padx=10, pady=5)

entry_time_signature = tk.Entry(frame)
entry_time_signature.grid(row=1, column=1, padx=10, pady=5)

entry_key_signature = tk.Entry(frame)
entry_key_signature.grid(row=2, column=1, padx=10, pady=5)

label_error = tk.Label(frame, wraplength=100)
label_error.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

canvas = tk.Canvas(root, width=width, height=height // 2, bg='white')
canvas.filepath = ""
canvas.is_clear = True

canvas.place(relx=0.5, rely=0.5, anchor="center")

def low_pass_filter(data, cutoff=3000, samplerate=44100, order=5):
    nyquist = 0.5 * samplerate
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def get_closest_note(frequency, tolerance=3):
  standard_notes = [27.5 * (2 ** (i / 12)) for i in range(88)]  # Piano range

  closest_note = min(standard_notes, key=lambda x: abs(x - frequency))
  if abs(closest_note - frequency) <= tolerance:
    return closest_note
  return frequency

def notenames(notes):
  note_names = []
  A4 = 440
  C0 = A4 * pow(2, -4.75)
  name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
  for note in notes:
    h = round(12 * log2(note / C0))
    octave = h // 12
    n = h % 12
    note_names.append(name[n] + str(octave))
  return note_names

def quadratic_interpolation(magnitude_spectrum, freqs):
    peak_idx = np.argmax(magnitude_spectrum)
    if peak_idx == 0 or peak_idx == len(magnitude_spectrum) - 1:
        return freqs[peak_idx]  # Edge case

    # Quadratic interpolation formula
    alpha = magnitude_spectrum[peak_idx - 1]
    beta = magnitude_spectrum[peak_idx]
    gamma = magnitude_spectrum[peak_idx + 1]
    
    delta = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)
    refined_freq = freqs[peak_idx] + delta * (freqs[1] - freqs[0])  
    
    return refined_freq

def transcribe_file():
  stereo_data, samplerate = sf.read(canvas.filepath, always_2d=True)  # Always read as stereo, even if mono

  data = stereo_data.mean(axis=1)  # Average channels if stereo
  # time = np.arange(0, len(data)) / samplerate  # Time vector
  # plt.figure(figsize=(10, 6))
  # plt.plot(time, data)
  # plt.title("Waveform of Audio Signal")
  # plt.xlabel("Time [s]")
  # plt.ylabel("Amplitude")
  # plt.grid(True)
  # plt.show()
  data = low_pass_filter(data)
  data_size = data.shape[0]
  song_length_seconds = data_size / samplerate

  print("Data size:", data_size)
  print("Sample rate:", samplerate)
  print("Song length:", song_length_seconds, "seconds")

  f, t, Zxx = scipy.signal.stft(data, samplerate, nperseg=4096)

  # plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
  # plt.title('STFT Magnitude')
  # plt.ylabel('Frequency [Hz]')
  # plt.xlabel('Time [sec]')
  # plt.colorbar(label='Magnitude')
  # plt.ylim(0, 4200)
  # plt.show()

  notes = []
  durations = []
  start_time = None
  last_note = None # Ensure no duplicate notes from weird waveform issues
  note_active = False 

  for i in range(len(t)):
    magnitude_spectrum = np.abs(Zxx[:, i])
    fundamental_freq = quadratic_interpolation(magnitude_spectrum, f)

    peak_magnitude = np.max(magnitude_spectrum)
    if peak_magnitude < 0.01 or fundamental_freq < 27.5 or fundamental_freq > 4000:
      continue

    snapped_note = get_closest_note(fundamental_freq)
    current_note = notenames([snapped_note])[0]
    if last_note is None or last_note != current_note: 
      if note_active:
        durations.append([round(start_time, 2), round(t[i], 2)])

      notes.append(fundamental_freq)
      start_time = t[i] 
      last_note = current_note
      note_active = True

  if note_active:
    durations.append([round(start_time, 2), round(t[-1], 2)])

  note_names = notenames(notes)
  print("Notes:", note_names)
  print(len(durations))
  notes_with_durations = list(zip(note_names, durations))

  # access elements like this notes_with_durations[0][1][1]
  filename = canvas.filepath.split("/")[len(canvas.filepath.split("/")) - 1]
  time_signature = entry_time_signature.get()
  key_signature = entry_key_signature.get()
  tempo = entry_tempo.get()

  if time_signature == "":
    time_signature = "4/4"
  if key_signature == "":
    key_signature = "C"
  if tempo == "":
    tempo = "100"
  if not canvas.is_clear:
    clear_canvas(canvas, False)
  canvas.is_clear = False
  display_sheet_music(canvas, width, height//2, notes_with_durations, filename=filename, time_signature=time_signature, key_signature=key_signature, tempo=int(tempo))

def open_file():
  if canvas.filepath != "":
    label_error.config(text="")
    transcribe_file()
    return

  canvas.filepath = filedialog.askopenfilename(
    initialdir='./wavs/',
    title="Select a file",
    filetypes=(("Raw audio files", "*.wav"), ("All files", "*.*"))
  )

  if canvas.filepath == "":
    return
  
  if not canvas.filepath.endswith(".wav"):
    label_error.config(text="Incorrect file type")
    return

  label_error.config(text="")
  transcribe_file()

def clear_canvas(canvas, clear_filename):
  canvas.delete("all")
  canvas.is_clear = True
  if clear_filename:
    canvas.filepath = ""


button = tk.Button(frame, text="Open file", command=open_file)
button.grid(row=3, column=0, padx=10, pady=5)

button = tk.Button(frame, text="Clear", command=lambda: clear_canvas(canvas, True))
button.grid(row=3, column=1, padx=10, pady=5)

root.geometry(f"{width}x{height}")

root.mainloop()



