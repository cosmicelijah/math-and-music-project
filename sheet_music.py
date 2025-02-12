import tkinter as tk
from PIL import Image, ImageTk
import math

def __draw_grand_staff(canvas, width, height, staff_top, staff_spacing):
  # Draw the 5 lines for the grand staff (treble and bass clef)
  treble_staff_top_y = staff_top
  bass_staff_top_y = treble_staff_top_y + 6 * staff_spacing
  for i in range(5):
    canvas.create_line(50, treble_staff_top_y + i * staff_spacing, width - 50, treble_staff_top_y + i * staff_spacing)
  
  for i in range(5):
    canvas.create_line(50, bass_staff_top_y + i * staff_spacing, width - 50, bass_staff_top_y + i * staff_spacing)
  
  # Load and resize the treble clef image
  treble_clef_image = Image.open("clefs/treble-clef.png")  # Open the image using Pillow
  treble_clef_image = treble_clef_image.resize((40, 80))  # Resize to 40x80 (adjust as needed)
  treble_clef_photo = ImageTk.PhotoImage(treble_clef_image)  # Convert to Tkinter-compatible image
  
  # Display the treble clef image
  canvas.create_image(80, treble_staff_top_y + 50 - staff_spacing, image=treble_clef_photo)  # Position it near the top staff lines
  canvas.image_references["treble_clef_photo"] = treble_clef_photo  # Keep a reference to the image

  # Load and resize the bass clef image
  bass_clef_image = Image.open("clefs/bass-clef.png")  # Open the image using Pillow
  bass_clef_image = bass_clef_image.resize((40, 50))  # Resize to 40x80 (adjust as needed)
  bass_clef_photo = ImageTk.PhotoImage(bass_clef_image)  # Convert to Tkinter-compatible image
  
  # Display the bass clef image
  canvas.create_image(80, bass_staff_top_y + 25, image=bass_clef_photo)  # Position it near the bottom staff lines
  canvas.image_references["bass_clef_photo"] = bass_clef_photo  # Keep a reference to the image

# Only whole, half, quarter, and eighth supported
def __draw_note(canvas, x, y, length, staff_top, staff_spacing, ledger_lines=[], invert=False, accidental=None):
  accidental_image = None

  if accidental != None:
    accidentalx = x - staff_spacing
    accidentaly = y
    if accidental == "flat":
      accidentaly = y - staff_spacing * 2 / 3

    accidental_image = Image.open(f"clefs/{accidental}.png")  # Open the image using Pillow
    accidental_image = accidental_image.resize((staff_spacing, staff_spacing * 3))  # Resize to 40x80 (adjust as needed)
    accidental_image = ImageTk.PhotoImage(accidental_image)  # Convert to Tkinter-compatible image

    canvas.create_image(accidentalx, accidentaly, image=accidental_image)  # Position it near the top staff lines
    canvas.image_references[f"{accidental}-{x}-{y}"] = accidental_image  # Keep a reference to the image


  stem_length = staff_spacing * 3.5
  fill = "black"
  draw_flag = False

  if length == "whole":
    # Whole note is an empty circle with no stem
    stem_length = 0
    fill = ""
  elif length == "half":
    # Half note is an empty circle with a stem
    fill = ""
  elif length == "eighth":
    # Eighth note has a flag
    draw_flag = True

  # Draw the note head (quarter note)
  canvas.create_oval(x, y - staff_spacing / 2, x + staff_spacing, y + staff_spacing / 2, outline="black", width=2, fill=fill)  # A 20x20 oval

  # Draw the stem (quarter note)
  if invert:
    canvas.create_line(x, y, x, y + stem_length, width=2)  # Vertical line
  else:
    canvas.create_line(x + staff_spacing, y, x + staff_spacing, y - stem_length, width=2)  # Vertical line

  if draw_flag:
    # Top of stem
    x1 = x + staff_spacing
    y1 = y - stem_length

    # Middle point (control point)
    x2 = x + staff_spacing * 2.5
    y2 = y - stem_length / 2

    # Bottom of curve
    x3 = x + staff_spacing * 1.5
    y3 = y - staff_spacing / 2

    if invert:
      # Bottom of stem
      x1 = x
      y1 = y + stem_length

      # Middle point (control point)
      x2 = x + staff_spacing * 1.5
      y2 = y + stem_length / 2

      # Top of curve
      x3 = x + staff_spacing * 0.5
      y3 = y + staff_spacing

    canvas.create_line(x1, y1, x2, y2, x3, y3, width=2, smooth=True)  # Curvy line

  if len(ledger_lines) > 0:
    # Draw the ledger line if asked
    for i in range(len(ledger_lines)):
      canvas.create_line(x - staff_spacing / 2, staff_top + staff_spacing * ledger_lines[i], x + staff_spacing + staff_spacing / 2, staff_top + staff_spacing * ledger_lines[i])  # Horizontal line

def __pitch_to_num(pitch):
  # God forbid Python has a switch statement like a real language would
  if pitch == "C":
    return 0
  elif pitch == "D":
    return 1
  elif pitch == "E":
    return 2
  elif pitch == "F":
    return 3
  elif pitch == "G":
    return 4
  elif pitch == "A":
    return 5
  else:
    return 6

def __get_accidental_name(accidental):
  if accidental == "#":
    return "sharp"
  elif accidental == "b":
    return "flat"
  else:
    return "natural"

def __calculate_ledger_lines(staff_placement):
  ledger_lines = []
  if staff_placement == 5:
    # Middle C
    ledger_lines.append(5)
  elif staff_placement <= -1:
    for i in range(-1, math.ceil(staff_placement) - 1, -1):
      ledger_lines.append(i)
  elif staff_placement >= 11:
    for i in range(11, math.floor(staff_placement) + 1):
      ledger_lines.append(i)
  return ledger_lines

def __is_inverted(staff_placement):
  if staff_placement <= 2:
    return True
  elif staff_placement > 5 and staff_placement < 8:
    return True
  else:
    return False

def __draw_note_name(canvas, position, pitch, octave, length, staff_top, staff_spacing):
  if len(pitch) == 1:
    # No accidental
    staff_placement = 19 - __pitch_to_num(pitch) * 0.5 - 3.5 * int(octave)
    ledger_lines = __calculate_ledger_lines(staff_placement)
    __draw_note(canvas, 150 + 50 * position, staff_top + staff_spacing * staff_placement, length, staff_top, staff_spacing, ledger_lines=ledger_lines, invert=__is_inverted(staff_placement))
  else:
    note = pitch[0]
    accidental = pitch[1]
    accidental_name = __get_accidental_name(accidental)
    staff_placement = 19 - __pitch_to_num(note) * 0.5 - 3.5 * int(octave)
    ledger_lines = __calculate_ledger_lines(staff_placement)
    __draw_note(canvas, 150 + 50 * position, staff_top + staff_spacing * staff_placement, length, staff_top, staff_spacing, accidental=accidental_name, ledger_lines=ledger_lines, invert=__is_inverted(staff_placement))

def display_sheet_music(notes, time_signature="4/4", tempo=100, key_signature="C"):
  """Takes list of notes and displays it as a series of quarter notes (for now)

  time_signature, tempo, and key_signature are unused (for now)

  notes -- list of string representations of notes formatted as pitch octave, ie "C#5", "A4", "Bb4"

  time_signature -- string representing time signature, formatted like "top/bottom", ie "4/4" (common time), "2/2" (cut time), "6/8"

  tempo -- integer value that represents tempo in BPM

  key_signature -- string representing key signature, uses major key representations for simplicity, ie "C" is C major (no accidentals), "Bb" is Bb major (2 flats). Only accepts up to 7 flats or sharps (Cb or C#, respectively)
  """

  # Create main window
  root = tk.Tk()
  root.title("Grand Staff in Tkinter")

  # Create a canvas widget
  width = 1000
  height = 600
  canvas = tk.Canvas(root, width=width, height=height, bg='white')
  canvas.pack()
  
  canvas.image_references = {}

  # Call the function to draw the grand staff
  staff_top = 100
  staff_spacing = 15
  __draw_grand_staff(canvas, width, height, staff_top, staff_spacing)

  for i, n in enumerate(notes):
    pitch = ""
    octave = ""
    if len(n) == 2:
      pitch = n[0]
      octave = n[1]
    else:
      pitch = n[:2]
      octave = n[2]
    
    __draw_note_name(canvas, i, pitch, octave, "eighth", staff_top, staff_spacing)
  


  # Run the Tkinter event loop
  root.mainloop()

display_sheet_music(["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"])