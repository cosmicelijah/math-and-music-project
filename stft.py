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

  # Get the peak frequency and magnitude for every second 
  interval = 2
  for i, time in enumerate(t):
    if i % (samplerate // 1024 * interval) == 0:
      magnitude_spectrum = np.abs(Zxx[:, i])
      peak_idx = np.argmax(magnitude_spectrum)
      peak_freq = f[peak_idx]
      peak_magnitude = magnitude_spectrum[peak_idx]
      print("Time: {:.3f}s, Frequency: {:.3f}Hz, Magnitude: {:.3f}".format(time, peak_freq, peak_magnitude))




height = 1200
width = 800

root = tk.Tk()
root.title("Math and Music Final Project")
root.geometry(f"{height}x{width}")

button = tk.Button(root, text="Open file", command=open_file)
button.pack(pady=50)

root.mainloop()