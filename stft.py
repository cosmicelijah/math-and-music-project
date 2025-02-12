import tkinter as tk
import scipy.signal
import soundfile as sf
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
import scipy
from math import log2, pow

filepath = None

def harmonic_product_spectrum_stft(magnitude, fs, num_harmonics=5):
  N = magnitude.shape[0]  # Number of frequency bins
  spectrum_product = np.copy(magnitude)
  
  for i in range(2, num_harmonics + 1):
    downsampled_spectrum = np.zeros(N)
    downsampled_spectrum[::i] = magnitude[::i]  # Downsample
    spectrum_product[:len(downsampled_spectrum)] *= downsampled_spectrum
  
  peak_index = np.argmax(spectrum_product[1:]) + 1  # Ignore DC component
  fundamental_freq = fs * peak_index / N  # Convert index to frequency
  return spectrum_product, fundamental_freq

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
  k = np.argmax(magnitude_spectrum)
  if k == 0 or k == len(magnitude_spectrum) - 1:
    return freqs[k] 

  alpha = magnitude_spectrum[k - 1]
  beta = magnitude_spectrum[k]
  gamma = magnitude_spectrum[k + 1]

  delta = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)

  refined_freq = freqs[k] + delta * (freqs[1] - freqs[0])  # Scale by bin width

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
  last_peak_freq = None
  interval = 0.1
  note_active = False 

  for i in range(len(t)):
    if i % (samplerate // 4096 * interval) == 0:
      magnitude_spectrum = np.abs(Zxx[:, i])
      fundamental_freq = quadratic_interpolation(magnitude_spectrum, f)

      peak_magnitude = np.max(magnitude_spectrum)
      if peak_magnitude < 0.01 or fundamental_freq < 27.5 or fundamental_freq > 4000:
        continue

      if last_peak_freq is None or abs(fundamental_freq - last_peak_freq) > 4: 
        if note_active:
          durations.append([round(start_time, 2), round(t[i], 2)])

        notes.append(fundamental_freq)
        start_time = t[i] 
        last_peak_freq = fundamental_freq
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
