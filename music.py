import numpy as np
from line import *
import pyaudio
import wave

class Note:

	def __init__(self, note, octave, color=None):
		self.note = note
		self.octave = octave
		self.color = color

		if self.color == 'Red':
			self.octave += 1

	def get_note(self):
		if self.octave == 1:
			return self.note.upper()
		elif self.octave == 2:
			return self.note.lower()
		else:
			return self.note

class Beat:

	def __init__(self, pos, rows=[]):
		self.pos = pos
		self.rows = rows


	def add_row(self, row):
		self.rows.append(row)

class Song:

	def __init__(self, points, rows, columns, tempo=120):
		self.points = points
		self.rows = rows
		self.columns = columns
		self.tempo = tempo

		self.key = None

		self.beats = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]

		self.num_tracks = 0
		self.build()

	def build(self):

		for point in self.points:
			col = self.get_point_column(point)
			row = self.get_point_row(point, col)
			if col == 1:
				self.key = self.key_from_row(row)
			elif col >= 3:
				self.beats[col-3].append(row)

		self.num_tracks = self.find_num_tracks()

	def empty_track(self):
		return [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]

	def get_point_column(self, point):
		x, _ = point

		i = 0
		for line in self.columns[1:]:
			if x < line.b:
				return i
			i += 1
		return None

	def get_point_row(self, point, col):
		_, y = point

		left = self.columns[col]
		right = self.columns[col+1]

		i = 0
		for line in self.rows[1:]:
			p1 = line.intersect(left)
			p2 = line.intersect(right)
			_, y_mid = self.midpoint(p1, p2)


			if y < y_mid:
				return i
			i += 1
		return None

	def midpoint(self, (x1, y1), (x2, y2)):
		x = (x1 + x2) / 2.0
		y = (y1 + y2) / 2.0
		return x, y


	def key_from_row(self, row):
		keys = {
			0 : 'F',
			1 : 'E',
			2 : 'D',
			3 : 'C',
			4 : 'B',
			5 : 'A',
			6 : 'G',
			7 : 'F',
			8 : 'E'
		}
		return keys[row]

	def find_num_tracks(self):
		max_notes = len(self.beats[0])
		for beat in self.beats[1:]:
			a = len(beat)
			if a > max_notes:
				max_notes = a
		return max_notes

	def track_abc_string(self, track):
		abc = "| "
		for beat in track[:8]:
			if beat == []:
				abc += "z"
			else:
				abc += beat[0].get_note()
		abc += " | "
		for beat in track[8:]:
			if beat == []:
				abc += "z"
			else:
				abc += beat[0].get_note()
		abc += " |"
		return abc

	def abc_string(self, track, track_num, title):
		abc = "X: " + str(track_num) + "\n"
		abc += "T: " + title + "\n"
		abc += "M: 4/4\n"
		abc += "L: 1/8\n"
		abc += "K: " + self.key + "\n"
		abc += "Q: 1/4=" + str(self.tempo) + "\n"
		abc += self.track_abc_string(track) + "\n"
		abc += "\n"
		return abc

	def export_song(self, file_name):

		keys = {
			'C': [Note('F',2), Note('E',2), Note('D',2), Note('C',2), Note('B',1), Note('A',1), Note('G',1), Note('F',1), Note('E',1)],
			'G': [Note('F#',2), Note('E',2), Note('D',2), Note('C',2), Note('B',1), Note('A',1), Note('G',1), Note('F#',1), Note('E',1)],
			'D': [Note('F#',2), Note('E',2), Note('D',2), Note('C#',2), Note('B',1), Note('A',1), Note('G',1), Note('F#',1), Note('E',1)],
			'A': [Note('F#',2), Note('E',2), Note('D',2), Note('C#',2), Note('B',1), Note('A',1), Note('G#',1), Note('F#',1), Note('E',1)],
			'E': [Note('F#',2), Note('E',2), Note('D#',2), Note('C#',2), Note('B',1), Note('A',1), Note('G#',1), Note('F#',1), Note('E',1)],
			'B': [Note('F#',2), Note('E',2), Note('D#',2), Note('C#',2), Note('B',1), Note('A#',1), Note('G#',1), Note('F#',1), Note('E',1)],
			'Cb': [Note('Fb',2), Note('Eb',2), Note('Db',2), Note('Cb',2), Note('Bb',1), Note('Ab',1), Note('Gb',1), Note('Fb',1), Note('Eb',1)],
			'F#': [Note('F#',2), Note('E#',2), Note('D#',2), Note('C#',2), Note('B',1), Note('A#',1), Note('G#',1), Note('F#',1), Note('E#',1)],
			'Gb': [Note('F',2), Note('Eb',2), Note('Db',2), Note('Cb',2), Note('Bb',1), Note('Ab',1), Note('Gb',1), Note('F',1), Note('Eb',1)],	
			'Db': [Note('F',2), Note('Eb',2), Note('Db',2), Note('C',2), Note('Bb',1), Note('Ab',1), Note('Gb',1), Note('F',1), Note('Eb',1)],
			'C#': [Note('F#',2), Note('E#',2), Note('D#',2), Note('C#',2), Note('B#',1), Note('A#',1), Note('G#',1), Note('F#',1), Note('E#',1)],
			'Ab': [Note('F',2), Note('Eb',2), Note('Db',2), Note('C',2), Note('Bb',1), Note('Ab',1), Note('G',1), Note('F',1), Note('Eb',1)],
			'Eb': [Note('F',2), Note('Eb',2), Note('D',2), Note('C',2), Note('Bb',1), Note('Ab',1), Note('G',1), Note('F',1), Note('Eb',1)],
			'Bb': [Note('F',2), Note('Eb',2), Note('D',2), Note('C',2), Note('Bb',1), Note('A',1), Note('G',1), Note('F',1), Note('Eb',1)],
			'F': [Note('F',2), Note('E',2), Note('D',2), Note('C',2), Note('Bb',1), Note('A',1), Note('G',1), Note('F',1), Note('E',1)]
		}


		scale = keys[self.key]
		tracks = []
		num_tracks = self.num_tracks
		for track in range(num_tracks):
			tracks.append(self.empty_track())

		beats = list(self.beats)

		for i in range(num_tracks):
			for j in range(16):
				if beats[j] != []:
					 tracks[i][j].append(scale[beats[j][0]])
					 beats[j].remove(beats[j][0])

		out_abc = ""
		for i in range(num_tracks):
			out_abc += self.abc_string(tracks[i], i+1, "track_" + str(i))

		f = open(file_name, 'w')
		f.write(out_abc)
		f.close()


class Player:

	def __init__(self):
		self.CHUNK = 1024
		self.p = pyaudio.PyAudio()

	def play_file(self, filename):
		wf = wave.open(filename, 'rb')
		
		stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
		      channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
		data = wf.readframes(self.CHUNK)

		while data != '':
		  stream.write(data)
		  data = wf.readframes(self.CHUNK)

		stream.stop_stream()
		stream.close()
	
	def terminate(self):
		self.p.terminate()



















