import cv2
import numpy as np
from line import *
from pydub import AudioSegment
import random
import sys
import os
from music import *

class Staff:

	def __init__(self, image, min_staff_length, min_vert_length, 
		CANNY_THRESHOLD1=50, CANNY_THRESHOLD2=150, CANNY_APERTURESIZE=3, RHO=1, THETA=180, THRESHOLD=200):
		self.CANNY_THRESHOLD1 = CANNY_THRESHOLD1
		self.CANNY_THRESHOLD2 = CANNY_THRESHOLD2
		self.CANNY_APERTURESIZE = CANNY_APERTURESIZE
		self.RHO = RHO
		self.THETA = THETA
		self.THRESHOLD = THRESHOLD

		self.image = image
		height, width, channels = self.image.shape
		self.image_height = height
		self.image_width = width
		self.min_staff_length = min_staff_length
		self.min_vert_length = min_vert_length

		self.gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
		self.edges = cv2.Canny(self.gray,self.CANNY_THRESHOLD1,self.CANNY_THRESHOLD2,apertureSize = self.CANNY_APERTURESIZE)
		self.staff_lines = []
		self.vertical_lines = []
		self.staff_spaces = []

	def find_staff_lines(self):
		all_staff_lines = cv2.HoughLines(self.edges,self.RHO,np.pi/self.THETA, self.min_staff_length)
		hori_lines, _ = self.filter_orient_size_and_outliers(all_staff_lines)

		staff_line_groups = self.group_staff_lines(hori_lines)
		staff_lines = []
		for group in staff_line_groups:
			staff_lines.append(self.avg_group(group))
		staff_lines = self.order_staff_lines(staff_lines)

		if len(staff_lines) == 5:
			self.staff_lines = staff_lines
			return True
		else:
			return False


	def find_vert_lines(self):
		all_vert_lines = cv2.HoughLines(self.edges,self.RHO,np.pi/self.THETA, self.min_vert_length)
		_, vert_lines = self.filter_orient_size_and_outliers(all_vert_lines)

		vert_line_groups = self.group_vert_lines(vert_lines)
		vert_lines = []
		for group in vert_line_groups:
			vert_lines.append(self.avg_group(group))
		vert_lines = self.order_vert_lines(vert_lines)
		
		if len(vert_lines) == 4:
			self.vertical_lines = vert_lines
			return True
		else:
			return False

	def extract_staff(self):
		self.find_staff_lines()
		self.find_vert_lines()

		shift_up_by = abs(self.staff_lines[0].midpoint()[1] - self.staff_lines[1].midpoint()[1]) / 2.0
		shift_down_by = abs(self.staff_lines[4].midpoint()[1] - self.staff_lines[3].midpoint()[1]) / 2.0

		btop = self.staff_lines[0].copy()
		bbottom = self.staff_lines[4].copy()
		btop.vertical_shift(-1 * shift_up_by)
		bbottom.vertical_shift(shift_down_by)

		topl = btop.intersect(self.vertical_lines[0])
		topr = btop.intersect(self.vertical_lines[3])
		botl = bbottom.intersect(self.vertical_lines[0])
		botr = bbottom.intersect(self.vertical_lines[3])

		widthA = self.distance(topl, topr)
		widthB = self.distance(botl, botr)

		heightA = self.distance(topl, botl)
		heightB = self.distance(topr, botr)

		maxWidth = max(int(widthA), int(widthB))
		maxHeight = max(int(heightA), int(heightB))

		rect = np.array([
			[topl[0], topl[1]],
			[topr[0], topr[1]],
			[botr[0], botr[1]],
			[botl[0], botr[1]]], dtype = "float32")

		dst = np.array([
			[0, 0],
			[maxWidth - 1, 0],
			[maxWidth - 1, maxHeight - 1],
			[0, maxHeight - 1]], dtype = "float32")

		M = cv2.getPerspectiveTransform(rect, dst)
		warp = cv2.warpPerspective(self.image, M, (maxWidth, maxHeight))
		return warp

	def get_m1_start(self):
		if self.vertical_lines == []:
			return None
		else:
			x1, _ = self.vertical_lines[0].intersect(self.staff_lines[2])
			x2, _ = self.vertical_lines[1].intersect(self.staff_lines[2])
			return x2 - x1

	def get_m2_start(self):
		if self.vertical_lines == []:
			return None
		else:
			x1, _ = self.vertical_lines[0].intersect(self.staff_lines[2])
			x3, _ = self.vertical_lines[2].intersect(self.staff_lines[2])
			return x3 - x1


	# This orders the 5 staff lines, 0 being the bottom
	# line to 4 being the top line
	def order_staff_lines(self, staff_lines):
		if staff_lines != None and staff_lines != []:
			ordered_lines = [staff_lines[0]]
			for line in staff_lines[1:]:
				i = 0
				for ordered_line in ordered_lines:
					if line.y1 < ordered_line.y1:
						ordered_lines.insert(i, line)
						break
					elif i == len(ordered_lines) - 1:
						ordered_lines.append(line)
						break
					else:
						i += 1
			return ordered_lines
		else:
			return []

	def order_vert_lines(self, vert_lines):
		if vert_lines != None and vert_lines != []:
			ordered_lines = [vert_lines[0]]
			for line in vert_lines[1:]:
				i = 0
				for ordered_line in ordered_lines:
					if line.x1 < ordered_line.x1:
						ordered_lines.insert(i, line)
						break
					elif i == len(ordered_lines) - 1:
						ordered_lines.append(line)
						break
					else:
						i += 1
			return ordered_lines
		else:
			return []

	def get_min_max_ys(self, lines):
		max_y = lines[0].y1
		min_y = lines[0].y1
		for line in lines[1:]:
			max_y = max(max_y, line.y1)
			min_y = min(min_y, line.y1)
		return min_y, max_y

	def get_min_max_xs(self, lines):
		max_x = lines[0].x1
		min_x = lines[0].x1
		for line in lines[1:]:
			max_x = max(max_x, line.x1)
			min_x = min(min_x, line.x1)
		return min_x, max_x


	def get_min_max_xs_vert(self, lines):
		if lines != None and lines != []: 
			x1, _ = lines[0].midpoint()
			max_x = x1
			min_x = x1
			for line in lines[1:]:
				x, _ = line.midpoint() 
				max_x = max(max_x, x)
				min_x = min(min_x, x)
			return min_x, max_x
		else:
			return 0.0, 0.0


	def filter_orient_size_and_outliers(self, lines):
		
		if lines != None:
			w = self.image_width
			h = self.image_height
			horizontal = []
			vertical = []
			for line in lines:
				a = Line(line, width=w, height=h)
				if a.is_horizontal():
					if (a.y1 < (.99)*h and a.y1 > (.01)*h) and (a.y2 < (.99)*h and a.y2 > (.01)*h):
						horizontal.append(a)
				else:
					if (a.x1 < (.99)*w and a.x1 > (.01)*w) and (a.x2 < (.99)*w and a.x2 > (.01)*w):
						vertical.append(a)
			return horizontal, vertical
		else:
			return [], []


	def group_staff_lines(self, lines):
		if lines != []:
			line_groups = []
			(x1, y1), (x2, y2) = lines[0].coordinates()
			if lines[0].is_horizontal:
				min_y, max_y = self.get_min_max_ys(lines)
				dist = ((max_y+1) - min_y) / 5.0
				for i in range(5):
					group = []
					for line in lines:
						if min_y+(dist*i) <= line.y1 < min_y+(dist*(i+1)):
							group.append(line)
					line_groups.append(group)
			else:
				min_x, max_x = self.get_min_max_xs(lines)
				dist = ((max_x+1) - min_x) / 5.0
				for i in range(5):
					group = []
					for line in lines:
						if min_x+(dist*i) <= line.x1 < min_x+(dist*(i+1)):
							group.append(line)
					line_groups.append(group)
			return line_groups
		else:
			return []


	def group_vert_lines(self, lines):
		if lines != [] and lines != None:
			line_groups = []
			(x1, y1), (x2, y2) = lines[0].coordinates()
			if not lines[0].is_horizontal:
				min_y, max_y = self.get_min_max_ys(lines)
				dist = ((max_y+1) - min_y) / 2.0
				for i in range(2):
					group = []
					for line in lines:
						(_, y1), (_, _) = line.coordinates()
						if min_y+(dist*i) <= y1 < min_y+(dist*(i+1)):
							group.append(line)
					line_groups.append(group)
			else:
				min_x, max_x = self.get_min_max_xs_vert(lines)
				dist = ((max_x+1) - (min_x-1)) / 10.0
				ranges = [
					((min_x-1), (min_x-1)+(dist*1)),
					(((min_x-1)+(dist*1)+1), (min_x-1)+(dist*3)),
					(((min_x-1)+(dist*5)), (min_x-1)+(dist*7)),
					(((min_x-1)+(dist*9)), (max_x+1))
					]
				for span in ranges:
					group = []
					for line in lines:
						x1, _ = line.midpoint()
						if span[0] <= x1 < span[1]:
							group.append(line)
					line_groups.append(group)
			return line_groups
		else:
			return []


	def distance(self, (x1, y1), (x2, y2)):
		a = ((x1-x2)**2.0)
		b = ((y1-y2)**2.0)
		return (( a + b )**(.5))

	def midpoint(self, (x1, y1), (x2, y2)):
		x = (x1 + x2) / 2.0
		y = (y1 + y2) / 2.0
		return x, y

	def line_pairs(self, neighbors):
		pairs = []
		for (x, y) in neighbors:
			pairs.append((x,y))
			if (y,x) in neighbors:
				neighbors.remove((y,x))
		return pairs

	def avg_lines(self, neighbors, lines):
		avg_lines = []
		for (x, y) in neighbors:
			(x1, y1), (x2, y2) = self.get_coordinates(lines[x])
			(x3, y3), (x4, y4) = self.get_coordinates(lines[y])
			avg_lines.append((self.midpoint((x1,y1),(x3,y3)), self.midpoint((x2,y2),(x4,y4))))
		return avg_lines

	def avg_group(self, line_group):
		num = len(line_group)
		x1 = 0
		y1 = 0
		x2 = 0
		y2 = 0
		for line in line_group:
			x1 += line.x1
			y1 += line.y1
			x2 += line.x2
			y2 += line.y2
		if num != 0:
			return Line(((x1/num),(y1/num)), ((x2/num),(y2/num)), width=self.image_width, height=self.image_height)
		else:
			return Line((0,0), (0,0), width=self.image_width, height=self.image_height)

	def draw_staff_lines(self):
		for l in self.staff_lines:
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,0,255),1)

	def draw_staff_line(self, index):
		if len(self.staff_lines) > index:
			l = self.staff_lines[index]
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,0,255),1)

	def draw_staff_spaces(self):
		for l in self.staff_spaces:
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,0,255),1)

	def draw_vertical_lines(self):
		if self.vertical_lines != None and self.vertical_lines != []:
			for l in self.vertical_lines:
				cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,255,0),1)

	def draw_vertical_line(self, index):
		if len(self.vertical_lines) > index:
			l = self.vertical_lines[index]
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,255,0),1)




class Staffy:

	def __init__(self, image, min_staff_length, min_vert_length, m1_start, m2_start, 
		CANNY_THRESHOLD1=50, CANNY_THRESHOLD2=150, CANNY_APERTURESIZE=3, RHO=1, THETA=180, THRESHOLD=200,
		DP=1, MINDIST=33, PARAM1=51, PARAM2=27, MINRADIUS=9, MAXRADIUS=25):
		self.CANNY_THRESHOLD1 = CANNY_THRESHOLD1
		self.CANNY_THRESHOLD2 = CANNY_THRESHOLD2
		self.CANNY_APERTURESIZE = CANNY_APERTURESIZE
		self.RHO = RHO
		self.THETA = THETA
		self.THRESHOLD = THRESHOLD
		self.DP = DP
		self.MINDIST = MINDIST
		self.PARAM1 = PARAM1
		self.PARAM2 = PARAM2
		self.MINRADIUS = MINRADIUS
		self.MAXRADIUS = MAXRADIUS

		self.image = image
		height, width, channels = self.image.shape
		self.image_height = height
		self.image_width = width
		self.min_staff_length = min_staff_length
		self.min_vert_length = min_vert_length
		self.m1_start = m1_start
		self.m2_start = m2_start

		self.gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
		self.edges = cv2.Canny(self.gray,self.CANNY_THRESHOLD1,self.CANNY_THRESHOLD2,apertureSize = self.CANNY_APERTURESIZE)

		self.staff_lines = []
		self.vertical_lines = []
		self.staff_spaces = []
		self.grid_rows = []
		self.grid_columns = []
		self.circles = []
		self.circle_centers = []

		self.find_staff_lines()
		self.find_staff_spaces()
		self.find_circles_with_centers()
		self.build_rows()
		self.build_columns()

	def find_staff_lines(self):
		all_staff_lines = cv2.HoughLines(self.edges,self.RHO,np.pi/self.THETA, self.min_staff_length)
		hori_lines, _ = self.filter_orient_size_and_outliers(all_staff_lines)

		staff_line_groups = self.group_staff_lines(hori_lines)
		staff_lines = []
		for group in staff_line_groups:
			staff_lines.append(self.avg_group(group))
		staff_lines = self.order_staff_lines(staff_lines)

		# print "Staff Lines Length: " + str(len(staff_lines))
		# print "Staff Lines: " + self.lines_str(staff_lines)
		if len(staff_lines) == 5:
			self.staff_lines = staff_lines
			return True
		else:
			return False

	def find_staff_spaces(self):
		staff_spaces = []
		for i in range(len(self.staff_lines)-1):
			line1 = self.staff_lines[i]
			line2 = self.staff_lines[i+1]
			staff_spaces.append(Line(
				self.midpoint((line1.x1, line1.y1), (line2.x1, line2.y1)), 
				self.midpoint((line1.x2, line1.y2),(line2.x2, line2.y2)),
				width = self.image_width,
				height = self.image_height
				))
		self.staff_spaces = self.order_staff_lines(staff_spaces)

	def find_circles_with_centers(self):
		blur = cv2.medianBlur(self.image,5)
		gray = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)

		# circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,int(self.image_width/25.0),
  #                           param1=50,param2=30,minRadius=0,maxRadius=int(self.image_width/40.0))
		circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,self.DP,self.MINDIST,
                            param1=self.PARAM1,param2=self.PARAM2,minRadius=self.MINRADIUS,maxRadius=self.MAXRADIUS)
		self.circles = np.uint16(np.around(circles))
		
		centers = []
		for i in self.circles[0,:]:
			# draw the center of the circle
			centers.append((i[0],i[1]))
		self.circle_centers = centers


	def build_rows(self):
		lines = self.staff_lines
		spaces = self.staff_spaces
		rows = [Line((0.0,0.0),(self.image_width, 0.0),width=self.image_width, height=self.image_height)]
		# rows = []
		for i in range(len(spaces)):
			line1 = lines[i]
			line2 = spaces[i]
			line3 = lines[i+1]
			rows.append(Line(
				self.midpoint((line1.x1, line1.y1), (line2.x1, line2.y1)), 
				self.midpoint((line1.x2, line1.y2),(line2.x2, line2.y2)),
				width = self.image_width,
				height = self.image_height
				))
			rows.append(Line(
				self.midpoint((line2.x1, line2.y1), (line3.x1, line3.y1)), 
				self.midpoint((line2.x2, line2.y2),(line3.x2, line3.y2)),
				width = self.image_width,
				height = self.image_height
				))
		rows.append(Line((0.0,self.image_height), (self.image_width, self.image_height), width=self.image_width, height=self.image_height))
		# self.grid_rows = self.order_staff_lines(rows)
		self.grid_rows = rows

	def build_columns(self):
		w = self.image_width
		h = self.image_height
		left = Line((0,0),(0,h), width=w, height=h)
		m1 = Line((self.m1_start, 0.0), (self.m1_start, h), width=w, height=h)
		m2 = Line((self.m2_start, 0.0), (self.m2_start, h), width=w, height=h)
		right = Line((w, 0.0), (w, h), width=w, height=h)
		cols = [left]

		dist = self.m1_start / 3.0
		for i in range(1,3):
			cols.append(Line(
				((dist*i),0),
				((dist*i),h),
				width=w,
				height=h
				))

		cols.append(m1)
		dist = (self.m2_start - self.m1_start) / 8.0
		for i in range(1,8):
			cols.append(Line(
				((self.m1_start + (dist*i)),0),
				((self.m1_start + (dist*i)),h),
				width=w,
				height=h
				))

		cols.append(m2)
		dist = (w - self.m2_start) / 8.0
		for i in range(1,8):
			cols.append(Line(
				((self.m2_start + (dist*i)),0),
				((self.m2_start + (dist*i)),h),
				width=w,
				height=h
				))

		cols.append(right)
		self.grid_columns = cols

	# This orders the 5 staff lines, 0 being the bottom
	# line to 4 being the top line
	def order_staff_lines(self, staff_lines):
		# ordered_lines = []
		# if staff_lines and len(staff_lines) > 0:
		# 	ordered_lines.insert(0, staff_lines[0])
		# 	for line in staff_lines[1:]:
		# 		i = 0
		# 		for ordered_line in ordered_lines:
		# 			if 
		if staff_lines != None and staff_lines != []:
			ordered_lines = [staff_lines[0]]
			for line in staff_lines[1:]:
				i = 0
				for ordered_line in ordered_lines:
					if line.y1 < ordered_line.y1:
						ordered_lines.insert(i, line)
						break
					elif i == len(ordered_lines) - 1:
						ordered_lines.append(line)
						break
					else:
						i += 1
			return ordered_lines
		else:
			return []

	def get_min_max_ys(self, lines):
		max_y = lines[0].y1
		min_y = lines[0].y1
		for line in lines[1:]:
			max_y = max(max_y, line.y1)
			min_y = min(min_y, line.y1)
		return min_y, max_y

	# def get_min_max_ys(self, lines):
		# (_, y1), (_, _) = lines[0]
		# max_y = y1
		# min_y = y1
		# for line in lines[1:]:
		# 	(_, y), (_, _) = line
		# 	max_y = max(max_y, y)
		# 	min_y = min(min_y, y)
		# return min_y, max_y

	def get_min_max_xs(self, lines):
		max_x = lines[0].x1
		min_x = lines[0].x1
		for line in lines[1:]:
			max_x = max(max_x, line.x1)
			min_x = min(min_x, line.x1)
		return min_x, max_x

	def midpoint(self, (x1, y1), (x2, y2)):
		x = (x1 + x2) / 2.0
		y = (y1 + y2) / 2.0
		return x, y

	def lines_str(self, lines):
		if lines != None and len(lines) > 0:
			s = "["
			for line in lines[:-1]:
				s += str(line) + ", "
			s += str(lines[-1]) + "]"
			return s
		else:
			return ""

	def filter_orient_size_and_outliers(self, lines):
		
		if lines != None:
			w = self.image_width
			h = self.image_height
			horizontal = []
			vertical = []
			for line in lines:
				a = Line(line, width=w, height=h)
				if a.is_horizontal():
					if (a.y1 < (.99)*h and a.y1 > (.01)*h) and (a.y2 < (.99)*h and a.y2 > (.01)*h):
						horizontal.append(a)
						# horizontal.append(((x1, y1), (x2, y2)))
				else:
					# vertical.append(self.size_line(((x1, y1), (x2, y2))))
					if (a.x1 < (.99)*w and a.x1 > (.01)*w) and (a.x2 < (.99)*w and a.x2 > (.01)*w):
						vertical.append(a)
			return horizontal, vertical
		else:
			return [], []

	def group_staff_lines(self, lines):
		if lines != []:
			line_groups = []
			(x1, y1), (x2, y2) = lines[0].coordinates()
			if lines[0].is_horizontal:
				min_y, max_y = self.get_min_max_ys(lines)
				dist = ((max_y+1) - min_y) / 5.0
				for i in range(5):
					group = []
					for line in lines:
						if min_y+(dist*i) <= line.y1 < min_y+(dist*(i+1)):
							group.append(line)
					line_groups.append(group)
			else:
				min_x, max_x = self.get_min_max_xs(lines)
				dist = ((max_x+1) - min_x) / 5.0
				for i in range(5):
					group = []
					for line in lines:
						if min_x+(dist*i) <= line.x1 < min_x+(dist*(i+1)):
							group.append(line)
					line_groups.append(group)
			return line_groups
		else:
			return []

	def avg_group(self, line_group):
		num = len(line_group)
		x1 = 0
		y1 = 0
		x2 = 0
		y2 = 0
		for line in line_group:
			x1 += line.x1
			y1 += line.y1
			x2 += line.x2
			y2 += line.y2
		if num != 0:
			return Line(((x1/num),(y1/num)), ((x2/num),(y2/num)), width=self.image_width, height=self.image_height)
		else:
			return Line((0,0), (0,0), width=self.image_width, height=self.image_height)

	def draw_staff_lines(self):
		for l in self.staff_lines:
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,0,255),1)

	def draw_grid_rows(self):
		for l in self.grid_rows:
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,0,255),1)

	def draw_grid_columns(self):
		for l in self.grid_columns:
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,0,255),1)

	def draw_staff_line(self, index):
		if len(self.staff_lines) > index:
			l = self.staff_lines[index]
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,0,255),1)

	def draw_staff_spaces(self):
		for l in self.staff_spaces:
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,0,255),1)

	def draw_vertical_lines(self):
		if self.vertical_lines != None and self.vertical_lines != []:
			for l in self.vertical_lines:
				cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,255,0),1)

	def draw_vertical_line(self, index):
		if len(self.vertical_lines) > index:
			l = self.vertical_lines[index]
			cv2.line(self.image,(int(l.x1),int(l.y1)),(int(l.x2),int(l.y2)),(0,255,0),1)


	def draw_circles(self):
		for i in self.circles[0,:]:
		    # draw the outer circle
		    cv2.circle(self.image,(i[0],i[1]),i[2],(0,255,0),2)
		    # draw the center of the circle
		    cv2.circle(self.image,(i[0],i[1]),2,(0,0,255),3)



class Staffer:

	def __init__(self, image, tempo=120):
		self.image = image
		self.staff = Staff(self.image, 250, 100)
		self.staffy = Staffy(self.staff.extract_staff(), 200, 30, self.staff.get_m1_start(), self.staff.get_m2_start())
		self.song = Song(self.staffy.circle_centers, self.staffy.grid_rows, self.staffy.grid_columns, tempo)

	def export_wav(self, filename):
		n = self.song.num_tracks
		self.song.export_song("temp/song.abc")

		sounds = ['--syn_a','--syn_b','--syn_s','--syn_e']

		for i in range(n):
			os.system("python read_abc.py temp/song.abc " + str(i+1) + " temp/out_" + str(i+1) + ".wav " + random.choice(sounds))
		os.remove("temp/song.abc")

		combined = AudioSegment.from_file("temp/out_1.wav")
		if n >= 2:
			for i in range(1, n):
				sound = AudioSegment.from_file("temp/out_" + str(i+1) + ".wav")
				combined = combined.overlay(sound)

		combined.export(filename, format='wav')

		for i in range(n):
			os.remove("temp/out_" + str(i+1) + ".wav")
	 
