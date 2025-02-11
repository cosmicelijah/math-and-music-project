import tkinter as tk 
from tkinter import filedialog
from scipy.fft import fft, fftfreq
from scipy.signal import stft, butter, filtfilt
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np

def get_closest_note(frequency):
  standard_notes = [27.5 * (2 ** (i / 12)) for i in range(88)]  # Piano range

  closest_note = min(standard_notes, key=lambda x: abs(x - frequency))
  
  return closest_note

# Maybe some way to think about key instead of leaving all accidentals as sharps
def notenames(notes):
  note_names = []
  for i, note in enumerate(notes):
    snapped_note = round(get_closest_note(note),2)
    midi = round(69 + 12 * np.log2(snapped_note / 440)) # MIDI note number
    octave = midi // 12 - 1 # Octave number
    pitch = midi % 12  # Pitch class

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

def _butter_lowpass(cutoff, fs, order=5):
  nyquist = 0.5 * fs
  normal_cutoff = cutoff / nyquist
  b, a = butter(order, normal_cutoff, btype='low', analog=False)
  return b, a

def lowpass_filter(data, cutoff, fs, order=5):
  b, a = _butter_lowpass(cutoff, fs, order)
  y = filtfilt(b, a, data)
  return y

def _butter_highpass(cutoff, fs, order=5):
  nyquist = 0.5 * fs
  normal_cutoff = cutoff / nyquist
  b, a = butter(order, normal_cutoff, btype='high', analog=False)
  return b, a

def highpass_filter(data, cutoff, fs, order=5):
  b, a = _butter_highpass(cutoff, fs, order)
  y = filtfilt(b, a, data)
  return y

def harmonic_product_spectrum_stft(magnitude, fs, num_harmonics=5):
  # Multiply the original spectrum by downsampled versions (harmonics)
  N = magnitude.shape[0]  # Number of frequency bins
  spectrum_product = np.copy(magnitude)
  
  for i in range(2, num_harmonics + 1):
    downsampled_spectrum = np.zeros(N)
    downsampled_spectrum[::i] = magnitude[::i]  # Downsample
    spectrum_product[:len(downsampled_spectrum)] *= downsampled_spectrum
  
  # Find peak corresponding to fundamental frequency
  peak_index = np.argmax(spectrum_product[1:]) + 1  # Ignore DC component
  fundamental_freq = fs * peak_index / N  # Convert index to frequency
  return spectrum_product, fundamental_freq

filepath = None

def open_file():
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
  
  stereo_data, samplerate = sf.read(filepath, always_2d=True) # Always read as stereo, even if mono
  data = stereo_data.mean(axis=1) # Average channels if stereo
  data_size = data.shape[0]
  song_length_seconds = data_size / samplerate

  print("Data size:", data_size)
  print("Sample rate:", samplerate)
  print("Song length:", song_length_seconds, "seconds")

  high_cutoff_freq = 4200 # Highest piano note is ~4186 Hz
  low_cutoff_freq = 20 # Lowest frequency of human hearing
  partial_filtered_data = lowpass_filter(data, high_cutoff_freq, samplerate)
  filtered_data = highpass_filter(partial_filtered_data, low_cutoff_freq, samplerate)

  f, t, Zxx = stft(filtered_data, samplerate, nperseg=8192)

  magnitude = np.abs(Zxx)

  print("f", f)
  print("t", t)

  plt.figure(figsize=(10, 6))
  plt.pcolormesh(t, f, 20 * np.log10(magnitude), shading='gouraud')
  plt.ylabel('Frequency [Hz]')
  plt.xlabel('Time [sec]')
  plt.title('STFT Magnitude Spectrogram')
  plt.colorbar(label='Magnitude [dB]')
  plt.ylim(0, 5000)
  plt.show()

  magnitude_stft = np.abs(Zxx)  # Use the magnitude of STFT
  for i in range(magnitude_stft.shape[1]):
    hps_spectrum, fundamental_freq = harmonic_product_spectrum_stft(magnitude_stft[:, i], samplerate)
    print(fundamental_freq)

  # Plot the original STFT magnitude and HPS result for the first time frame
  # plt.figure(figsize=(12, 6))

  # plt.subplot(2, 1, 1)
  # plt.plot(f, magnitude_stft[:, 20])  # Plot first frame of the STFT
  # plt.title("STFT Magnitude (First Time Frame)")
  # plt.xlabel("Frequency (Hz)")
  # plt.ylabel("Magnitude")

  # plt.subplot(2, 1, 2)
  # plt.plot(f, hps_spectrum)  # Plot HPS result
  # plt.title("Harmonic Product Spectrum (HPS) on STFT")
  # plt.xlabel("Frequency (Hz)")
  # plt.ylabel("Magnitude")

  # plt.tight_layout()
  # plt.show()

  # notes = []
  # interval = 2
  # last_peak_freq = None
  # for i, time in enumerate(t):
  #   if i % (samplerate // 1024 * interval) == 0:
  #     magnitude_spectrum = np.abs(Zxx[:, i])
  #     peak_freq = harmonic_product_spectrum(magnitude_spectrum)

  #     if last_peak_freq is None or abs(peak_freq - last_peak_freq) > 1: 
  #       notes.append(peak_freq)
  #       last_peak_freq = peak_freq

  # note_names = notenames(notes)
  # print("Notes:", note_names)



height = 1200
width = 800

root = tk.Tk()
root.title("Math and Music Final Project")
root.geometry(f"{height}x{width}")

button = tk.Button(root, text="Open file", command=open_file)
button.pack(pady=50)

root.mainloop()