import numpy as np

class Line:

	def __init__(self, *args, **kwargs):
		if args != []:
			if type(args[0]) == int or type(args[0]) == float or type(args[0]) == str:
				# if len(args) == 2:
				try:
					self.init_m_and_b(args[0], args[1])
				# else:
				except:
					print "Insufficient arguments to create object"
			elif type(args[0]) == tuple:
				try:
					self.init_coordinates(args[0], args[1])
				except:
					print "Insufficient arguments to create object"
			else:
				try:
					self.init_line(args[0])
				except:
					print "Insufficient arguments to create object"
		if kwargs.has_key('width') and kwargs.has_key('height'):
			self.set_border(kwargs['width'], kwargs['height'])


	def init_line(self, line):
		(self.x1, self.y1), (self.x2, self.y2) = self.coordinates_from_polar(line)
		self.m, self.b = self.get_line_equation(((self.x1, self.y1), (self.x2, self.y2)))

	def init_coordinates(self, a, b):
		self.x1, self.y1 = a
		self.x2, self.y2 = b
		self.m, self.b = self.get_line_equation(((self.x1, self.y1), (self.x2, self.y2)))

	def init_m_and_b(self, m, b):
		self.m = m
		self.b = b
		self.x1 = None
		self.y1 = None
		self.x2 = None
		self.y2 = None

	def __str__(self):
		return "(" + str(self.x1) + ", " + str(self.y1) + ") -> (" + str(self.x2) + ", " + str(self.y2) + ")"

	def coordinates_from_polar(self, line):
		rho, theta = line[0]
		a = np.cos(theta)
		b = np.sin(theta)
		x0 = a*rho
		y0 = b*rho
		x1 = int(x0 + 3000*(-b))
		y1 = int(y0 + 3000*(a))

		x2 = int(x0 - 3000*(-b))
		y2 = int(y0 - 3000*(a))
		return (x1, y1), (x2, y2)

	def coordinates(self):
		return (self.x1, self.y1), (self.x2, self.y2)

	def set_border(self, width, height):
		self.width = width
		self.height = height

		border = {
			"top": Line(0.0,0.0),
			"right": Line("INF", width),
			"bottom": Line(0.0, height),
			"left": Line("INF", 0.0)
		}

		hits_border = {
			"top": (False, None),
			"right": (False, None),
			"bottom": (False, None),
			"left": (False, None)
		}

		if self.intersect(border["top"]):
			hits_border["top"] = (True, self.intersect(border["top"])) if 0 <= self.intersect(border["top"])[0] <= width else (False, None)
		if self.intersect(border["right"]):
			hits_border["right"] = (True, self.intersect(border["right"])) if 0 < self.intersect(border["right"])[1] < height else (False, None)
		if self.intersect(border["bottom"]):
			hits_border["bottom"] = (True, self.intersect(border["bottom"])) if 0 <= self.intersect(border["bottom"])[0] <= width else (False, None)
		if self.intersect(border["left"]):
			hits_border["left"] = (True, self.intersect(border["left"])) if 0 < self.intersect(border["left"])[1] < height else (False, None)

		coordinates = []
		for key in hits_border:
			if hits_border[key][0]:
				coordinates.append(hits_border[key][1])
		if len(coordinates) == 2:
			self.x1, self.y1 = coordinates[0]
			self.x2, self.y2 = coordinates[1]


	def get_line_equation(self, line):
		(x1, y1), (x2, y2) = line
		if (x2-x1) != 0:
			m = ((y2 - y1)*1.0) / (x2 - x1)
			b = y1 - (m * x1)
		else:
			m = "INF"
			b = x1
		return m, b

	def line_value_at_x(self, x):
		if self.m == "INF":
			return None
		else:
			return (self.m * x) + self.b

	def line_value_at_y(self, y):
		if self.m == "INF":
			return self.b
		else:
			return (y - self.b) / self.m

	def is_horizontal(self):
		if self.m != "INF":
			if abs(self.m) < 1.0:
				return True
			else:
				return False
		else:
			return False

	def midpoint(self):
		x = (self.x1 + self.x2) / 2.0
		y = (self.y1 + self.y2) / 2.0
		return x, y

	def vertical_shift(self, i):
		self.b += i
		self.set_border(self.width, self.height)

	def copy(self):
		return Line(self.m, self.b, width=self.width, height=self.height)

	def intersect(self, line):
		if self.m == "INF":
			if line.m == "INF":
				return None
			else:
				return (self.b, line.line_value_at_x(self.b))
		else:
			if line.m == "INF":
				return (line.b, self.line_value_at_x(line.b))
			elif self.m != line.m:
				x = (line.b - self.b) / (self.m - line.m)
				y = (self.m * x) + self.b
				return (x, y)
			else:
				return None
