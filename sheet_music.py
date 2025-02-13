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
  treble_clef_image = treble_clef_image.resize((staff_spacing * 3, staff_spacing * 7))  # Resize to 40x80 (adjust as needed)
  treble_clef_photo = ImageTk.PhotoImage(treble_clef_image)  # Convert to Tkinter-compatible image
  
  # Display the treble clef image
  canvas.create_image(50 + staff_spacing * 2, treble_staff_top_y + staff_spacing * 2 + 2, image=treble_clef_photo)  # Position it near the top staff lines
  canvas.image_references[f"treble_clef_photo_{staff_top}"] = treble_clef_photo  # Keep a reference to the image

  # Load and resize the bass clef image
  bass_clef_image = Image.open("clefs/bass-clef.png")  # Open the image using Pillow
  bass_clef_image = bass_clef_image.resize((staff_spacing * 3, staff_spacing * 4))  # Resize to 40x80 (adjust as needed)
  bass_clef_photo = ImageTk.PhotoImage(bass_clef_image)  # Convert to Tkinter-compatible image
  
  # Display the bass clef image
  canvas.create_image(50 + staff_spacing * 2, bass_staff_top_y + staff_spacing * 2, image=bass_clef_photo)  # Position it near the bottom staff lines
  canvas.image_references[f"bass_clef_photo_{staff_top}"] = bass_clef_photo  # Keep a reference to the image

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
  flag_count = 0

  if length == "whole":
    # Whole note is an empty circle with no stem
    stem_length = 0
    fill = ""
  elif length == "half":
    # Half note is an empty circle with a stem
    fill = ""
  elif length == "eighth":
    # Eighth note has a flag
    flag_count = 1
  elif length == "sixteenth":
    flag_count = 2


  # Draw the note head (quarter note)
  canvas.create_oval(x, y - staff_spacing / 2, x + staff_spacing, y + staff_spacing / 2, outline="black", width=2, fill=fill)  # A 20x20 oval

  # Draw the stem (quarter note)
  if invert:
    canvas.create_line(x, y, x, y + stem_length, width=2)  # Vertical line
  else:
    canvas.create_line(x + staff_spacing, y, x + staff_spacing, y - stem_length, width=2)  # Vertical line

  if flag_count > 0:
    shift = 0
    # Top of stem
    x1 = x + staff_spacing
    y1 = y - stem_length

    # Middle point (control point)
    x2 = x + staff_spacing * 2.5
    y2 = y - stem_length / 2

    # Bottom of curve
    x3 = x + staff_spacing * 1.5
    y3 = y - staff_spacing / 2

    if flag_count == 2:
      shift = 5

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

      if flag_count == 2:
        shift = -5

    canvas.create_line(x1, y1, x2, y2, x3, y3, width=2, smooth=True)  # Curvy line
    if flag_count == 2:
      canvas.create_line(x1, y1 + shift, x2, y2 + shift, x3, y3 + shift, width=2, smooth=True)  # Curvy line

  if len(ledger_lines) > 0:
    # Draw the ledger line if asked
    for i in range(len(ledger_lines)):
      canvas.create_line(x - staff_spacing / 2, staff_top + staff_spacing * ledger_lines[i], x + staff_spacing + staff_spacing / 2, staff_top + staff_spacing * ledger_lines[i])  # Horizontal line

def __pitch_to_num(pitch):
  # God forbid Python has a switch statement like a real language would. Nvm
  match pitch:
    case "C":
      return 0
    case "D":
      return 1
    case "E":
      return 2
    case "F":
      return 3
    case "G":
      return 4
    case "A":
      return 5
    case _:
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

def __draw_note_name(canvas, position, pitch, octave, length, staff_top, staff_spacing, note_offset):
  if len(pitch) == 1:
    # No accidental
    staff_placement = 19 - __pitch_to_num(pitch) * 0.5 - 3.5 * int(octave)
    ledger_lines = __calculate_ledger_lines(staff_placement)
    __draw_note(canvas, note_offset + 50 * position, staff_top + staff_spacing * staff_placement, length, staff_top, staff_spacing, ledger_lines=ledger_lines, invert=__is_inverted(staff_placement))
  else:
    note = pitch[0]
    accidental = pitch[1]
    accidental_name = __get_accidental_name(accidental)
    staff_placement = 19 - __pitch_to_num(note) * 0.5 - 3.5 * int(octave)
    ledger_lines = __calculate_ledger_lines(staff_placement)
    __draw_note(canvas, note_offset + 50 * position, staff_top + staff_spacing * staff_placement, length, staff_top, staff_spacing, accidental=accidental_name, ledger_lines=ledger_lines, invert=__is_inverted(staff_placement))

def __get_nearest_note_length(lengths, start, end):
  shortest = lengths[len(lengths) - 1]
  tolerance = shortest # 8th note length
  if abs(start - end) - tolerance < 0:
    # filter out anomalous blips that got through the previous filters
    return None
  else:
    length = abs(start - end)
    closest_length = min(lengths, key=lambda x: abs(x - length))

    match lengths.index(closest_length) :
      case 0:
        return "whole"
      case 1:
        return "half"
      case 2:
        return "quarter"
      case 3:
        return "eighth"
      case _:
        return None
      
def __get_pitch(note):
  pitch = ""
  if len(note) == 2:
    pitch = note[0]
  else:
    pitch = note[:2]
  return pitch

def __get_octave(note):
  octave = ""
  if len(note) == 2:
    octave = note[1]
  else:
    octave = note[2]
  return octave

def __preprocess_notes(notes, lengths, key_signature):
  # Assume that octave jumps close together are the same note, favoring the lower note
  tolerance = lengths[len(lengths) - 1] / 2 # Smallest allowed length of a pitch (16th note)

  processed_notes = []

  active_pitch = None
  active_octave = None
  for i in range(len(notes)):
    if notes[i] == None:
      continue

    n = notes[i]

    pitch = __get_pitch(n[0])
    octave = __get_octave(n[0])

    start = n[1][0]
    end = n[1][1]
    # If smaller than tolerance, merge into one of the notes adjacent, or delete if neither note matches pitch. Regardless of octave
    if abs(start - end) < tolerance:
      offset = 0
      into = ""
      if i > 0 and active_pitch == pitch:
        # Merge into previous note
        into = "prev"
        offset = -1
      else:
        # Merge into next note
        into = "next"
        offset = 1

        if i == len(notes) - 1:
          into = "prev"
          offset = -1
      
      pos = i + offset
      while notes[pos] == None:
        if into == "prev":
          pos -= 1
        else:
          pos += 1
      if into == "prev":
        notes[pos][1][1] += abs(start - end)
      else:
        notes[pos][1][0] -= abs(start - end)
      notes[i] = None

      if into == "prev":
        active_pitch = pitch
    else:
      active_pitch = pitch

    

  for i in range(len(notes)):
    if notes[i] != None:
      processed_notes.append(notes[i])

  return processed_notes

def __get_num_accidentals(key_signature):
  match key_signature:
    case "C" | "a":
        return 0
    case "G" | "e":
        return 1
    case "D" | "b":
        return 2
    case "A" | "f#":
        return 3
    case "E" | "c#":
        return 4
    case "B" | "g#":
        return 5
    case "F#" | "d#":
        return 6
    case "C#" | "a#":
        return 7
    case "F" | "d":
        return -1
    case "Bb" | "g":
        return -2
    case "Eb" | "c":
        return -3
    case "Ab" | "f":
        return -4
    case "Db" | "bb":
        return -5
    case "Gb" | "eb":
        return -6
    case "Cb" | "ab":
        return -7

def __draw_time_signature(canvas, staff_top, staff_spacing, x, time_signature):
  top = time_signature.split("/")[0]
  bottom = time_signature.split("/")[1]

  if top == "4" and bottom == "4":
    # Common time
    # Load and resize the common time image
    common_time_image = Image.open("clefs/common-time.png")  # Open the image using Pillow
    common_time_image = common_time_image.resize((staff_spacing * 2, staff_spacing * 2))  # Resize to 40x80 (adjust as needed)
    common_time_photo = ImageTk.PhotoImage(common_time_image)  # Convert to Tkinter-compatible image
    
    # Display the common time image
    canvas.create_image(x, staff_top + staff_spacing * 2, image=common_time_photo)  # Position it in the middle of the treble staff right after the 
    canvas.image_references[f"common_time_photo_treble_{staff_top}"] = common_time_photo  # Keep a reference to the image

    # Display the common time image
    canvas.create_image(x, staff_top + staff_spacing * 8, image=common_time_photo)  # Position it near the top staff lines
    canvas.image_references[f"common_time_photo_bass_{staff_top}"] = common_time_photo  # Keep a reference to the image
  elif top == "2" and bottom == "2":
    # Cut time
    # Load and resize the cut time image
    cut_time_image = Image.open("clefs/cut-time.png")  # Open the image using Pillow
    cut_time_image = cut_time_image.resize((staff_spacing * 2, staff_spacing * 2 + 7))  # Resize to 40x80 (adjust as needed)
    cut_time_photo = ImageTk.PhotoImage(cut_time_image)  # Convert to Tkinter-compatible image
    
    # Display the cut time image
    canvas.create_image(x, staff_top + staff_spacing * 2, image=cut_time_photo)  # Position it in the middle of the treble staff right after the 
    canvas.image_references[f"cut_time_photo_treble_{staff_top}"] = cut_time_photo  # Keep a reference to the image

    # Display the cut time image
    canvas.create_image(x, staff_top + staff_spacing * 8, image=cut_time_photo)  # Position it near the top staff lines
    canvas.image_references[f"cut_time_photo_bass_{staff_top}"] = cut_time_photo  # Keep a reference to the image
  else:
    canvas.create_text(x, staff_top + staff_spacing, text=top, font=("Times New Roman", staff_spacing * 2, "bold"))
    canvas.create_text(x, staff_top + staff_spacing * 3, text=bottom, font=("Times New Roman", staff_spacing * 2, "bold"))

def __draw_key_signature(canvas, staff_top, staff_spacing, key_signature):
  accidentals = __get_num_accidentals(key_signature)

  sharps_order = [0, 1.5, -0.5, 1, 2.5, 0.5, 2]
  flats_order = [2, 0.5, 2.5, 1, 3, 1.5, 3.5]

  accidentals_order = []

  accidental_str = ""

  if accidentals > 0:
    accidental_str = "sharp"
    accidentals_order = sharps_order
  elif accidentals < 0:
    accidental_str = "flat"
    accidentals_order = flats_order
  else:
    # C major/A minor
    return 0
  
  adjustment = 0
  if accidental_str == "flat":
    adjustment = staff_spacing * 2 // 3

  accidental_image = Image.open(f"clefs/{accidental_str}.png")  # Open the image using Pillow
  accidental_image = accidental_image.resize((staff_spacing, staff_spacing * 3))  # Resize to 40x80 (adjust as needed)
  accidental_image = ImageTk.PhotoImage(accidental_image)  # Convert to Tkinter-compatible image

  for i in range(abs(accidentals)):
    canvas.create_image(120 + staff_spacing * i, staff_top + accidentals_order[i] * staff_spacing - adjustment, image=accidental_image)  # Position it near the top staff lines
    canvas.image_references[f"{accidental_str}-treble-{i}"] = accidental_image  # Keep a reference to the image

  for i in range(abs(accidentals)):
    canvas.create_image(120 + staff_spacing * i, staff_top + (accidentals_order[i] + 7) * staff_spacing - adjustment, image=accidental_image)  # Position it near the top staff lines
    canvas.image_references[f"{accidental_str}-bass-{i}"] = accidental_image  # Keep a reference to the image

  return abs(accidentals)

def __draw_tempo(canvas, staff_top, staff_spacing, x, tempo, length):
  length_str = ""
  match length:
    case 1:
      length_str = "whole"
    case 2:
      length_str = "half"
    case 4:
      length_str = "quarter"
    case 8:
      length_str = "eighth"
    case _:
      length_str = "quarter"

  __draw_note(canvas, x - 60, staff_top - staff_spacing * 2, length_str, staff_top, staff_spacing * 2 // 3)
  canvas.create_text(x, staff_top - staff_spacing * 2, text=f"= {tempo}", font=("Times New Roman", staff_spacing * 3 // 2, "bold"))

def __sharp_to_flat(c: str) -> str:
  if len(c) == 1:
      return c
  else:
    if c[1] == "b":
      return c
    else:
      match c[0]:
        case "A":
          return "Bb"
        case "B":
          return "C"
        case "C":
          return "Db"
        case "D":
          return "Eb"
        case "E":
          return "F"
        case "F":
          return "Gb"
        case "G":
          return "Ab"

def __adjust_accidental(pitch, key_signature):
  num_accidentals = __get_num_accidentals(key_signature)

  if num_accidentals == 0:
    return pitch
  elif num_accidentals > 0:
    # Sharp
    order = ["F", "C", "G", "D", "A", "E", "B"]
    if len(pitch) == 1:
      # Natural or no?
      index_key = order.index(pitch) + 1
      if index_key <= num_accidentals:
        return pitch + "n"
      else:
        return pitch
    else:
      # Default values of notes from transcriber is all sharps
      true_pitch = pitch[0]
      index_key = order.index(true_pitch) + 1
      if index_key <= num_accidentals:
        return true_pitch
      else:
        return pitch
  else:
    # Flats
    order = ["B", "E", "A", "D", "G", "C", "F"]
    flat_pitch = __sharp_to_flat(pitch)
    if len(pitch) == 1:
      index_key = order.index(pitch) + 1
      if index_key <= abs(num_accidentals):
        return pitch + "n"
      else:
        return flat_pitch
    else:
      true_pitch = flat_pitch[0]
      index_key = order.index(true_pitch) + 1
      if index_key <= abs(num_accidentals):
        return true_pitch
      else:
        return flat_pitch


def display_sheet_music(canvas, width, height, notes, filename="", time_signature="4/4", tempo=100, key_signature="C"):
  """Takes list of notes and displays it as a series of quarter notes (for now)

  root -- TKinter window

  notes -- list of string representations of notes formatted as pitch octave, ie "C#5", "A4", "Bb4"

  time_signature -- string representing time signature, formatted like "top/bottom", ie "4/4" (common time), "2/2" (cut time), "6/8"

  tempo -- integer value that represents tempo in BPM

  key_signature -- string representing key signature, uses major/minor key representations, ie "C" is C major (no accidentals), "eb" is Eb minor (6 flats). Only accepts up to 7 flats or sharps (Cb/ab or C#/a#, respectively)
  """
  # Create a canvas widget
  # canvas = tk.Canvas(root, width=width, height=height, bg='white')
  
  canvas.create_text(width // 2, 20, text=filename, anchor="n", font=("Helvetica", 16))
  canvas.image_references = {}

  num_beats_per_measure = int(time_signature.split("/")[0])
  note_length_per_beat = int(time_signature.split("/")[1]) # 1 = whole, 2 = half, 4 = quarter, 8 = eighth

  seconds_per_beat = 60 / tempo

  note_values = [1, 2, 4, 8] # Whole, half, quarter, eighth
  lengths = []

  for i, n in enumerate(note_values):
    if n == 1:
      lengths.append(seconds_per_beat * num_beats_per_measure)
    else:
      lengths.append(seconds_per_beat * note_length_per_beat / n)
  
  # Call the function to draw the grand staff
  staff_top = 100
  staff_spacing = 15

  __draw_grand_staff(canvas, width, height, staff_top, staff_spacing)
  time_signature_offset = __draw_key_signature(canvas, staff_top, staff_spacing, key_signature)
  __draw_time_signature(canvas, staff_top, staff_spacing, 120 + staff_spacing * (time_signature_offset + 2), time_signature)
  __draw_tempo(canvas, staff_top, staff_spacing, 250, tempo, note_length_per_beat)

  note_offset = time_signature_offset + 6

  processed_notes = __preprocess_notes(notes.copy(), lengths, key_signature)

  # print(notes)
  # print(processed_notes)

  for i, n in enumerate(processed_notes):
    nearest_note_length = __get_nearest_note_length(lengths, n[1][0], n[1][1])

    note = n[0]

    pitch = __get_pitch(note)
    octave = __get_octave(note)

    pitch = __adjust_accidental(pitch, key_signature)
    
    __draw_note_name(canvas, i, pitch, octave, nearest_note_length, staff_top, staff_spacing, note_offset * staff_spacing + 120)

  return canvas