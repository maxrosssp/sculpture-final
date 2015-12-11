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
import cPickle as pickle

HOUGHLINES_PARAMS_FILEPATH = 'data/houghlines_params.p'

HOUGHLINES_PARAMS = None
try:
    HOUGHLINES_PARAMS = pickle.load( open(HOUGHLINES_PARAMS_FILEPATH, 'rb') )
except:
    print "Unable to load saved parameters. Using defaults."
    HOUGHLINES_PARAMS = {
        'canny_threshold1': 50,
        'canny_threshold2': 150,
        'canny_apertureSize': 3,
        'rho': 1,
        'theta': 180,
        'threshold': 200
        }

master = Tk()
canny_threshold1_label = Label(master, text="canny_threshold1")
canny_threshold1_label.pack()
canny_threshold1 = Scale(master, from_=1, to=800, orient=HORIZONTAL)
canny_threshold1.set(HOUGHLINES_PARAMS['canny_threshold1'])
canny_threshold1.pack()

canny_threshold2_label = Label(master, text="canny_threshold2")
canny_threshold2_label.pack()
canny_threshold2 = Scale(master, from_=1, to=800, orient=HORIZONTAL)
canny_threshold2.set(HOUGHLINES_PARAMS['canny_threshold2'])
canny_threshold2.pack()

canny_apertureSize_label = Label(master, text="canny_apertureSize")
canny_apertureSize_label.pack()
canny_apertureSize = Scale(master, from_=1, to=3, orient=HORIZONTAL)
canny_apertureSize.set((HOUGHLINES_PARAMS['canny_apertureSize']+1)/2)
canny_apertureSize.pack()

rho_label = Label(master, text="rho")
rho_label.pack()
rho = Scale(master, from_=1, to=10, orient=HORIZONTAL)
rho.set(HOUGHLINES_PARAMS['rho'])
rho.pack()

theta_label = Label(master, text="x (theta=pi/x)")
theta_label.pack()
theta = Scale(master, from_=1, to=360, orient=HORIZONTAL)
theta.set(HOUGHLINES_PARAMS['theta'])
theta.pack()

threshold_label = Label(master, text="threshold")
threshold_label.pack()
threshold = Scale(master, from_=0, to=800, orient=HORIZONTAL)
threshold.set(HOUGHLINES_PARAMS['threshold'])
threshold.pack()

if len(sys.argv) > 1:
    image = cv2.imread(sys.argv[1])
    if 'cropped' not in sys.argv[1]:
        height, width, channels = image.shape
        image = image[.075*height:(1-.075)*height, 0:width]
    image = imutils.resize(image, width=800)
        
else:
    camera = PiCamera()
    camera.resolution = (1120, 630)
    rawCapture = PiRGBArray(camera, size=(1120, 630))

    time.sleep(0.1)

    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array


def task():
##        clean_image = imutils.resize(staffer.staffy.image, width=1000)
    clean_image = image.copy()
    gray = cv2.cvtColor(clean_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,
    				canny_threshold1.get(),
    				canny_threshold2.get(),
    				apertureSize = ((canny_apertureSize.get()*2) - 1)
                )

    lines = cv2.HoughLines(edges,
                    rho.get(),
                    np.pi/theta.get(),
                    threshold.get()
                )
    if lines != None:
            for line in lines:
                    rho_x,theta_x = line[0]
                    a = np.cos(theta_x)
                    b = np.sin(theta_x)
                    x0 = a*rho_x
                    y0 = b*rho_x
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))

                    cv2.line(clean_image,(x1,y1),(x2,y2),(0,0,255),2)
    
    cv2.imshow("Lines", clean_image)

    key = cv2.waitKey(1)

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
            exit()
    elif key == ord("s"):
        HOUGHLINES_PARAMS['canny_threshold1'] = canny_threshold1.get()
        HOUGHLINES_PARAMS['canny_threshold2'] = canny_threshold2.get()
        HOUGHLINES_PARAMS['canny_apertureSize'] = ((canny_apertureSize.get()*2) - 1)
        HOUGHLINES_PARAMS['rho'] = rho.get()
        HOUGHLINES_PARAMS['theta'] = theta.get()
        HOUGHLINES_PARAMS['threshold'] = threshold.get()
        pickle.dump(HOUGHLINES_PARAMS, open(HOUGHLINES_PARAMS_FILEPATH, 'wb'))
        exit()

    master.after(20, task)

master.after(20, task)
master.mainloop()























