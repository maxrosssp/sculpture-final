import numpy as np
import imutils
import cv2
import time
from picamera.array import PiRGBArray
from picamera import PiCamera

##camera = cv2.VideoCapture(0)
##time.sleep(0.25)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
##rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

##while True:
for cur_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
##  (grabbed, frame) = camera.read()
##  if not grabbed:
##    break

  frame = cur_frame.array
  image = imutils.resize(frame, width=1000)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(gray,50,150,apertureSize = 3)
##  edges = cv2.Canny(gray,129,276, apertureSize = 3)

  lines = cv2.HoughLines(edges,1,np.pi/180,200)
  if lines != None:
    for line in lines:
      rho,theta = line[0]
      a = np.cos(theta)
      b = np.sin(theta)
      x0 = a*rho
      y0 = b*rho
      x1 = int(x0 + 1000*(-b))
      y1 = int(y0 + 1000*(a))
      x2 = int(x0 - 1000*(-b))
      y2 = int(y0 - 1000*(a))

      cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)

  cv2.imshow('frame',frame)
  cv2.imshow('gray',gray)
  cv2.imshow('edges', edges)
  key = cv2.waitKey(1)

  rawCapture.truncate(0)
  
  if key == ord("q"):
    break

  #master.update()


##camera.release()
##cv2.destroyAllWindows()
