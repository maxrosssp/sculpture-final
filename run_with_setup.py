from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import imutils
import time
import cv2
from staff import Staffer
from music import Player
import os
from Tkinter import *
import cPickle as pickle

PARAMS_FILEPATH = 'data/params.p'

class MainSetup(Frame):
    
    def __init__(self, params, *args, **kwargs):

        self.params = params
        self.staffer = None
        self.create_staffer()
            
        Frame.__init__(self, *args, **kwargs)
        self.w_circle = None
        self.w_welcome = Toplevel(self)
        start_message = Label(self.w_welcome, text="Click 'Start' to begin the staff calibration.")
        start_message.pack()
        b_start = Button(self.w_welcome, text="Start", command=self.circle_window)
        b_start.pack()

    def create_staffer(self):
        
        camera = PiCamera()
        camera.resolution = (1120, 630)
        rawCapture = PiRGBArray(camera, size=(1120, 630))

        time.sleep(0.1)

        camera.capture(rawCapture, format="bgr")
        image = rawCapture.array
        
        self.staffer = Staffer(image)
        self.staffer.staff.draw_vertical_lines()
        self.staffer.staff.draw_staff_lines()
        self.staffer.staffy.draw_grid_rows()
        self.staffer.staffy.draw_grid_columns()

    def set_circle(self):

            self.need_circle_setup = False
            
            self.params['dp'] = self.dp_s.get()
            self.params['minDist'] = self.minDist_s.get()
            self.params['param1'] = self.param1_s.get()
            self.params['param2'] = self.param2_s.get()
            self.params['minRadius'] = self.minRadius_s.get()
            self.params['maxRadius'] = self.maxRadius_s.get()

            self.w_circle.destroy()

            self.finish()

    def circle_window(self):

        self.w_welcome.destroy()
        self.w_circle = Toplevel(self)
        
        self.dp_label = Label(self.w_circle, text="dp")
        self.dp_label.pack()
        self.dp_s = Scale(self.w_circle, from_=1, to=5, orient=HORIZONTAL)
        self.dp_s.set(self.params['dp'])
        self.dp_s.pack()

        self.minDist_label = Label(self.w_circle, text="minDist")
        self.minDist_label.pack()
        self.minDist_s = Scale(self.w_circle, from_=1, to=100, orient=HORIZONTAL)
        self.minDist_s.set(self.params['minDist'])
        self.minDist_s.pack()

        self.param1_label = Label(self.w_circle, text="param1")
        self.param1_label.pack()
        self.param1_s = Scale(self.w_circle, from_=1, to=265, orient=HORIZONTAL)
        self.param1_s.set(self.params['param1'])
        self.param1_s.pack()

        self.param2_label = Label(self.w_circle, text="param2")
        self.param2_label.pack()
        self.param2_s = Scale(self.w_circle, from_=1, to=100, orient=HORIZONTAL)
        self.param2_s.set(self.params['param2'])
        self.param2_s.pack()

        self.minRadius_label = Label(self.w_circle, text="minRadius")
        self.minRadius_label.pack()
        self.minRadius_s = Scale(self.w_circle, from_=0, to=50, orient=HORIZONTAL)
        self.minRadius_s.set(self.params['minRadius'])
        self.minRadius_s.pack()

        self.maxRadius_label = Label(self.w_circle, text="maxRadius")
        self.maxRadius_label.pack()
        self.maxRadius_s = Scale(self.w_circle, from_=0, to=200, orient=HORIZONTAL)
        self.maxRadius_s.set(self.params['maxRadius'])
        self.maxRadius_s.pack()

        self.b_next = Button(self.w_circle, text="Next", command=self.set_circle)
        self.b_next.pack()

        self.circle_setup()

    def circle_setup(self):

        clean_image = self.staffer.staffy.image.copy()
        blur = cv2.medianBlur(clean_image,1)
        gray = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                self.dp_s.get(),
                self.minDist_s.get(),
                param1=self.param1_s.get(),
                param2=self.param2_s.get(),
                minRadius=self.minRadius_s.get(),
                maxRadius=self.maxRadius_s.get()
            )

        if circles != None and circles != []:
            circles = np.uint16(np.around(circles))

            for i in circles[0,:]:
                # draw the outer circle        
                cv2.circle(clean_image,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(clean_image,(i[0],i[1]),2,(0,0,255),3)

        cv2.imshow("Circlieeees", clean_image)
##        cv2.imshow("Circlieeees", blur)

##        cv2.imshow("Boot", self.staffer.staffy.image)
##            self.after(20, self.circle_setup)

    def finish(self):

        pickle.dump(self.params, open(PARAMS_FILEPATH, 'wb'))
        root.quit()
     
PARAMS = None
try:
    PARAMS = pickle.load( open(PARAMS_FILEPATH, 'rb') )
except:
    print "Unable to load saved parameters. Using defaults."
    PARAMS = {
        'dp': 1,
        'minDist': 33,
        'param1': 51,
        'param2': 27,
        'minRadius': 9,
        'maxRadius': 25
        }
        
root = Tk()
setup = MainSetup(PARAMS, root)
setup.pack()
root.mainloop()




