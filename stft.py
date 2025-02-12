import tkinter as tk
import scipy.signal
import soundfile as sf
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
import scipy
from math import log2, pow
from scipy.signal import butter, filtfilt

filepath = None


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

def open_file():
  filepath = filedialog.askopenfilename(
    initialdir='./wavs/',
    title="Select a file",
    filetypes=(("Raw audio files", "*.wav"), ("All files", "*.*"))
  )

  if not filepath:
    return
  
  if not filepath.endswith(".wav"):
    print("Incorrect file type")
    return

  stereo_data, samplerate = sf.read(filepath, always_2d=True)  # Always read as stereo, even if mono


  data = stereo_data.mean(axis=1)  # Average channels if stereo
  time = np.arange(0, len(data)) / samplerate  # Time vector
  plt.figure(figsize=(10, 6))
  plt.plot(time, data)
  plt.title("Waveform of Audio Signal")
  plt.xlabel("Time [s]")
  plt.ylabel("Amplitude")
  plt.grid(True)
  plt.show()
  data = low_pass_filter(data)
  data_size = data.shape[0]
  song_length_seconds = data_size / samplerate

  print("Data size:", data_size)
  print("Sample rate:", samplerate)
  print("Song length:", song_length_seconds, "seconds")

  f, t, Zxx = scipy.signal.stft(data, samplerate, nperseg=4096)

  plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
  plt.title('STFT Magnitude')
  plt.ylabel('Frequency [Hz]')
  plt.xlabel('Time [sec]')
  plt.colorbar(label='Magnitude')
  plt.ylim(0, 4200)
  plt.show()

  notes = []
  durations = []
  start_time = None
  last_note = None # Ensure no duplicate notes from weird waveform issues
  interval = 0.1
  note_active = False 

  for i in range(len(t)):
    if i % (samplerate // 4096 * interval) == 0:
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

height = 1200
width = 800

root = tk.Tk()
root.title("Math and Music Final Project")
root.geometry(f"{height}x{width}")

button = tk.Button(root, text="Open file", command=open_file)
button.pack(pady=50)

root.mainloop()