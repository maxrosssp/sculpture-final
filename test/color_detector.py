import numpy as np
import cv2
import imutils
from Tkinter import *

master = Tk()
b1_label = Label(master, text="Blue Low")
b1_label.pack()
b1 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
b1.set(25)
b1.pack()
g1 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
g1.set(25)
g1.pack()
r1 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
r1.set(25)
r1.pack()

b2 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
b2.set(25)
b2.pack()
g2 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
g2.set(25)
g2.pack()
r2 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
r2.set(25)
r2.pack()



boundaries = [
	([56, 68, 38], [94, 255, 68]), 			# DARK GREEN 
	([75, 15, 0], [146, 56, 49]),			# DARK BLUE
	([8, 32, 138], [0, 47, 255]),			# ORANGE
	([4, 30, 116], [71, 90, 255]),			# BLACK,
	([101, 26, 135], [161,109,218])			# PINK
]

image = cv2.imread("output.jpg")
image = imutils.resize(image, width=700)

# for (lower,upper) in boundaries:
# 	print "Lower: " + str(lower)
# 	print "Upper: " + str(upper)
# 	print
# 	lower = np.array(lower, dtype = "uint8")
# 	upper = np.array(upper, dtype = "uint8")
# 	# find the colors within the specified boundaries and apply
# 	# the mask
# 	mask = cv2.inRange(image, lower, upper)
# 	output = cv2.bitwise_and(image, image, mask = mask)
 
# 	# show the images
# 	cv2.imshow("images", np.hstack([image, output]))
# 	cv2.waitKey(0)

# boundaries = [ ([b1.get(), g1.get(), r1.get()], [b2.get(), g2.get(), r2.get()]) ]

# loop over the boundaries

##while True:
def task():
	lower = [b1.get(), g1.get(), r1.get()]
	upper = [b2.get(), g2.get(), r2.get()]
	# create NumPy arrays from the boundaries
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")
 
	# find the colors within the specified boundaries and apply
	# the mask
	mask = cv2.inRange(image, lower, upper)
	output = cv2.bitwise_and(image, image, mask = mask)
 
	# show the images
	cv2.imshow("images", np.hstack([image, output]))
	key = cv2.waitKey(1)
	if key == ord("q"):
	   exit()

	master.after(20, task)

master.after(20, task)
master.mainloop()
