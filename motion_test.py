from picamera.array import PiRGBArray
from picamera import PiCamera
import imutils
import time
import cv2
from staff import Staffer
from music import Player
import os

## !!!!!!!!!!!!!!!!!!!!
## To set audio output to HDMI: > amixer cset numid=3 2
## To set audio output to headphone jack: > amixer cset numid=3 1
## To set audio output to automatic: > amixer cset numid=3 0
## !!!!!!!!!!!!!!!!!!!!
THRESHOLD = 25
MIN_AREA = 1200
SECONDS_TO_RESET = 20
TEMPO = 110


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1280, 720)
rawCapture = PiRGBArray(camera, size=(1280, 720))
 
# allow the camera to warmup
time.sleep(0.1)
 
# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array

print "Build staffer: "
cur_time = time.time()
staffer = Staffer(image, tempo=TEMPO)
print "Completed in " + str(time.time() - cur_time) + " seconds."
print ""

print "Export wav."
cur_time = time.time()
staffer.export_wav("final.wav")
print "Completed in " + str(time.time() - cur_time) + " seconds."
print ""

print "Build player."
cur_time = time.time()
player = Player()
print "Completed in " + str(time.time() - cur_time) + " seconds."
print ""

player.play_file("final.wav")
player.terminate()

##def motion_detected(frameGray, previousFrame):
##
##	frameDelta = cv2.absdiff(previousFrame, gray)
##	thresh = cv2.threshold(frameDelta, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
##	thresh = cv2.dilate(thresh, None, iterations=2)
##	(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
##	cv2.CHAIN_APPROX_SIMPLE)
##
##	for c in cnts:
##		# if the contour is too small, ignore it
##		if cv2.contourArea(c) < MIN_AREA:
##			continue
##		return True, frameDelta
##
##	return False, frameDelta
##
### initialize the camera and grab a reference to the raw camera capture
##camera = PiCamera()
##camera.resolution = (640, 360)
##camera.framerate = 10
##rawCapture = PiRGBArray(camera, size=(640,360))
##
####camera = cv2.VideoCapture(0)
##time.sleep(3)
##
##motion = False
##time_of_motion = 0
##create_song = False
##compareFrame = None
##previousFrame = None
##previous2frames = []
##
##i = 0
####while True:
##for cur_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
##        
####	(grabbed, frame) = camera.read()
####	if not grabbed:
####		break
##
##        frame = cur_frame.array
####	frame = imutils.resize(frame, width=500)
##	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
##	gray = cv2.GaussianBlur(gray, (21, 21), 0)
##	previousFrame = gray if previousFrame is None else previousFrame
##	if previous2frames == []:
##		previous2frames.append(gray)
##		previous2frames.append(gray)
##	if i == 1:
##		previous2frames.insert(0, gray)
##		previous2frames.pop()
##		i = 0
##
##
##	if motion:
##		detected, frameDelta = motion_detected(gray, compareFrame)  
##		#if (time.time() - time_of_motion) > SECONDS_TO_RESET:
##                 #       motion = False
##                  #      create_song = False
##		if not detected:
##			motion = False
##	else:
##		detected, frameDelta = motion_detected(gray, previousFrame)
##		if detected:
##			motion = True
##			create_song = True
##			time_of_motion = time.time()
##			compareFrame = previous2frames[1]
##			print "MOTION DETECTED"
##
##		if not motion and create_song:
##			print "Do SHIT"
##			staffer = Staffer(frame, tempo=TEMPO)
##			staffer.export_wav("final.wav")
##
##			player = Player()
##			player.play_file("final.wav")
##			player.terminate()
##			create_song = False
##
####	cv2.imshow("Security Feed", frame)
##  	# cv2.imshow("Thresh", thresh)
####  	cv2.imshow("Frame Delta", frameDelta)
##  	key = cv2.waitKey(1)
##
##        previousFrame = gray
##	i += 1
##  	rawCapture.truncate(0)
##
##	# if the `q` key is pressed, break from the lop
##	if key == ord("q"):
##		break
##
##	  	# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
##	  	# gray = cv2.GaussianBlur(gray, (21, 21), 0)
##
##		# frameDelta = cv2.absdiff(previousFrame, gray)
##		# thresh = cv2.threshold(frameDelta, threshold.get(), 255, cv2.THRESH_BINARY)[1]
##		# thresh = cv2.dilate(thresh, None, iterations=2)
##		# (_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
##	 #    cv2.CHAIN_APPROX_SIMPLE)
##
##	 #    for c in cnts:
##		#     # if the contour is too small, ignore it
##		#     if cv2.contourArea(c) < min_area.get():
##		#       continue
##
##		#     # compute the bounding box for the contour, draw it on the frame,
##		#     # and update the text
##		#     (x, y, w, h) = cv2.boundingRect(c)
##		#     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
##		#     compareFrame = previousFrame
##		#     motion_detected = True
##		#     create_song = True
##
##
##
##
##
##









