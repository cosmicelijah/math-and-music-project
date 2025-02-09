import tkinter as tk
import scipy.signal
import soundfile as sf
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import clear_output
from scipy.fftpack import fft, fftshift
import scipy

filepath = None
comma = 1.021678153 # Just something I noticed, unsure if it makes sense in theory

def round_notes(notes):
  for i, note in enumerate(notes):
    notes[i] = round(note * comma)

def notenames(notes):
  note_names = []
  for i, note in enumerate(notes):
    midi = 69 + 12 * np.log2(note / 440)
    octave = midi // 12 - 1
    pitch = midi % 12
    if pitch == 0:
      note_names.append("C" + str(int(octave)))
    elif pitch == 1:
      note_names.append("C#" + str(int(octave)))
    elif pitch == 2:
      note_names.append("D" + str(int(octave)))
    elif pitch == 3:
      note_names.append("D#" + str(int(octave)))
    elif pitch == 4:
      note_names.append("E" + str(int(octave)))
    elif pitch == 5:
      note_names.append("F" + str(int(octave)))
    elif pitch == 6:
      note_names.append("F#" + str(int(octave)))
    elif pitch == 7:
      note_names.append("G" + str(int(octave)))
    elif pitch == 8:
      note_names.append("G#" + str(int(octave)))
    elif pitch == 9:
      note_names.append("A" + str(int(octave)))
    elif pitch == 10:
      note_names.append("A#" + str(int(octave)))
    elif pitch == 11:
      note_names.append("B" + str(int(octave)))
  return note_names

def open_file():
  # filepath = "./wavs/a440.wav"
  filepath = filedialog.askopenfilename(
    initialdir='./wavs/',
    title="Select a file",
    filetypes=(("Raw audio files", "*.wav"), ("All files", "*.*"))
  )

  if filepath == None:
    return
  
  file_arr = filepath.split(".")

  if file_arr[len(file_arr) - 1] != "wav":
    print("Incorrect file type")
  
  data, samplerate = sf.read(filepath)

  data_size = data.shape[0]
  song_length_seconds = data_size/samplerate

  print("Data size:", data_size)
  print("Sample rate:", samplerate)
  print("Song length:", song_length_seconds, "seconds")

  f, t, Zxx = scipy.signal.stft(data, samplerate, nperseg=1024)

  plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
  plt.title('STFT Magnitude')
  plt.ylabel('Frequency [Hz]')
  plt.xlabel('Time [sec]')
  plt.colorbar(label='Magnitude')
  plt.ylim(0, 2000)
  plt.show()

  # Get the peak frequency and magnitude only when it has changed
  notes = []
  interval = 2
  last_peak_freq = None
  for i, time in enumerate(t):
    if i % (samplerate // 1024 * interval) == 0:
      magnitude_spectrum = np.abs(Zxx[:, i])
      peak_idx = np.argmax(magnitude_spectrum)
      peak_freq = f[peak_idx]
      peak_magnitude = magnitude_spectrum[peak_idx]
      if last_peak_freq is None or peak_freq != last_peak_freq:
        notes.append(peak_freq)
        print("Time: {:.3f}s, Frequency: {:.3f}Hz, Magnitude: {:.3f}".format(time, peak_freq, peak_magnitude))
        last_peak_freq = peak_freq

  round_notes(notes)
  note_names = notenames(notes)
  print("Notes:", note_names)

  # Write to sheet music




height = 1200
width = 800

root = tk.Tk()
root.title("Math and Music Final Project")
root.geometry(f"{height}x{width}")

button = tk.Button(root, text="Open file", command=open_file)
button.pack(pady=50)

root.mainloop()