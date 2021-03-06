from Tkinter import *
import numpy as np
import cv2
import time
import imutils
from staff import Staffer
from music import Player
from picamera.array import PiRGBArray
from picamera import PiCamera
import sys

master = Tk()
dp_label = Label(master, text="dp")
dp_label.pack()
dp = Scale(master, from_=1, to=5, orient=HORIZONTAL)
dp.set(1)
dp.pack()

minDist_label = Label(master, text="minDist")
minDist_label.pack()
minDist = Scale(master, from_=1, to=100, orient=HORIZONTAL)
minDist.set(33)
minDist.pack()

param1_label = Label(master, text="param1")
param1_label.pack()
param1 = Scale(master, from_=1, to=265, orient=HORIZONTAL)
param1.set(51)
param1.pack()

param2_label = Label(master, text="param2")
param2_label.pack()
param2 = Scale(master, from_=1, to=100, orient=HORIZONTAL)
param2.set(27)
param2.pack()

minRadius_label = Label(master, text="minRadius")
minRadius_label.pack()
minRadius = Scale(master, from_=0, to=50, orient=HORIZONTAL)
minRadius.set(9)
minRadius.pack()

maxRadius_label = Label(master, text="maxRadius")
maxRadius_label.pack()
maxRadius = Scale(master, from_=0, to=200, orient=HORIZONTAL)
maxRadius.set(25)
maxRadius.pack()

if len(sys.argv) > 1:
        image = cv2.imread(sys.argv[1])
        image = imutils.resize(image, width=1120)
        
else:
        camera = PiCamera()
        camera.resolution = (1120, 630)
        rawCapture = PiRGBArray(camera, size=(1120, 630))

        time.sleep(0.1)

        camera.capture(rawCapture, format="bgr")
        image = rawCapture.array

staffer = Staffer(image)
staffer.staff.draw_vertical_lines()
staffer.staff.draw_staff_lines()
staffer.staffy.draw_grid_rows()
staffer.staffy.draw_grid_columns()
##staffer.staffy.draw_circles()

def task():
##        clean_image = imutils.resize(staffer.staffy.image, width=1000)
        clean_image = staffer.staffy.image.copy()
        blur = cv2.medianBlur(clean_image,1)
        gray = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp.get(),
                minDist.get(),
                param1=param1.get(),
                param2=param2.get(),
                minRadius=minRadius.get(),
                maxRadius=maxRadius.get()
            )

        if circles != None and circles != []:
            circles = np.uint16(np.around(circles))

            for i in circles[0,:]:
                # draw the outer circle        
                cv2.circle(clean_image,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(clean_image,(i[0],i[1]),2,(0,0,255),3)

        cv2.imshow("Circles", clean_image)
	cv2.imshow("Staff", staffer.staff.image)
	cv2.imshow("Staffy", staffer.staffy.image)

	key = cv2.waitKey(1)

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		exit()

	master.after(20, task)

master.after(20, task)
master.mainloop()























