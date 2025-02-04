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

  freq_domain = np.linspace(-samplerate/2, samplerate/2, data_size)

  fourier_data = abs(fft(data))
  fourier_data_shift = fftshift(fourier_data)

  plt.xlim([0, 1000])
  plt.xlabel("Frequency (Hz)")
  plt.ylabel("Amplitude")
  plt.plot(freq_domain, fourier_data_shift)
  plt.show()

  max = fourier_data_shift.max()

  # Normalize array
  for f in fourier_data_shift:
    f /= max

  peak_indices, props = scipy.signal.find_peaks(fourier_data_shift, height=0.5)

  for i, peak in enumerate(peak_indices):
    freq = freq_domain[peak]
    magnitude = props["peak_heights"][i]
    print("{}hz with magnitude {:.3f}".format(freq, magnitude))



height = 1200
width = 800

root = tk.Tk()
root.title("Math and Music Final Project")
root.geometry(f"{height}x{width}")

button = tk.Button(root, text="Open file", command=open_file)
button.pack(pady=50)

root.mainloop()