import numpy as np
import cv2
import imutils
from Tkinter import *
from picamera.array import PiRGBArray
from picamera import PiCamera
import time



master = Tk()
dp_label = Label(master, text="dp")
dp_label.pack()
dp = Scale(master, from_=1, to=5, orient=HORIZONTAL)
dp.set(1)
dp.pack()

minDist_label = Label(master, text="minDist")
minDist_label.pack()
minDist = Scale(master, from_=1, to=100, orient=HORIZONTAL)
minDist.set(int(1000/25.0))
minDist.pack()

param1_label = Label(master, text="param1")
param1_label.pack()
param1 = Scale(master, from_=1, to=265, orient=HORIZONTAL)
param1.set(50)
param1.pack()

param2_label = Label(master, text="param2")
param2_label.pack()
param2 = Scale(master, from_=1, to=100, orient=HORIZONTAL)
param2.set(30)
param2.pack()

minRadius_label = Label(master, text="minRadius")
minRadius_label.pack()
minRadius = Scale(master, from_=0, to=1000, orient=HORIZONTAL)
minRadius.set(0)
minRadius.pack()

maxRadius_label = Label(master, text="maxRadius")
maxRadius_label.pack()
maxRadius = Scale(master, from_=0, to=1200, orient=HORIZONTAL)
maxRadius.set(int(1000/40.0))
maxRadius.pack()

##b2 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
##b2.set(25)
##b2.pack()
##g2 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
##g2.set(25)
##g2.pack()
##r2 = Scale(master, from_=0, to=255, orient=HORIZONTAL)
##r2.set(25)
##r2.pack()

##camera = PiCamera()
##camera.resolution = (640, 480)
##camera.framerate = 32
##rawCapture = PiRGBArray(camera, size=(640, 480))
##camera = PiCamera()
##camera.resolution = (1120, 630)
##rawCapture = PiRGBArray(camera)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(1)

def task():

    for cur_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

##        cur_frame = camera.capture(rawCapture, format="bgr", use_video_port=True)
        
        frame = cur_frame.array
        image = imutils.resize(frame, width=1000)

        blur = cv2.medianBlur(frame,1)
        gray = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)

    ##    circles = cv2.HoughCircles(
    ##                    gray,
    ##                    cv2.HOUGH_GRADIENT,
    ##                    1,
    ##                    int(1000/25.0),
    ##                    param1=50,
    ##                    param2=30,
    ##                    minRadius=0,
    ##                    maxRadius=int(1000/40.0)
    ##                )
        
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
                cv2.circle(frame,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(frame,(i[0],i[1]),2,(0,0,255),3)

        cv2.imshow('blur', blur)
        cv2.imshow('frame',frame)

        key = cv2.waitKey(1)

        rawCapture.truncate(0)
          
        if key == ord("q"):
            exit()

        master.update()


master.after(20, task)
master.mainloop()



















