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

def get_closest_note(frequency, tolerance=3):
    standard_notes = [16.35160 * (2 ** (i / 12)) for i in range(88)]  # Piano range

    closest_note = min(standard_notes, key=lambda x: abs(x - frequency))
    if abs(closest_note - frequency) <= tolerance:
        return closest_note
    return frequency

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

def quadratic_interpolation(magnitude_spectrum, freqs):
    k = np.argmax(magnitude_spectrum)
    if k == 0 or k == len(magnitude_spectrum) - 1:
        return freqs[k] 

    # Magnitudes of the peak and its neighbors
    alpha = magnitude_spectrum[k - 1]
    beta = magnitude_spectrum[k]
    gamma = magnitude_spectrum[k + 1]

    # Compute the shift (delta) using the quadratic interpolation formula
    delta = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)

    # Refined frequency estimate
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

    data, samplerate = sf.read(filepath)
    data_size = data.shape[0]
    song_length_seconds = data_size / samplerate

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
            peak_freq = quadratic_interpolation(magnitude_spectrum, f)

            # Apply a threshold to filter out noise
            peak_magnitude = np.max(magnitude_spectrum)
            if peak_magnitude < 0.01:
                continue

            if last_peak_freq is None or abs(peak_freq - last_peak_freq) > 1: 
                notes.append(peak_freq)
                last_peak_freq = peak_freq

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