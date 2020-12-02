#!/usr/bin/env python


from collections import deque
import urllib.request 
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import rospy


ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,help="max buffer size")
ap.add_argument('-url',"--url", action = 'store_true', help="Takes input from the IP WEBCAM")
ap.add_argument('-cam',"--cam",action = 'store_true', help = "Takes input from device camera")
ap.add_argument("-a", "--min-area", type=int, default=50, help="minimum area size")
args = vars(ap.parse_args())


if args["url"]:
    URL = input("Enter the URL of the IP camera : ")

    URLS = ''

    for i in "http://":
        URLS += i
    for i in URL:
        URLS += i
    for i in "/shot.jpg":
        URLS += i

else:
    vs = VideoStream(0).start()
    #time.sleep(2.0)

firstFrame = None

while True:
	if(args["url"]==True):
		imgResp = urllib.request.urlopen(URLS)
		#print(type(imgResp))
		img_arr = np.array(bytearray(imgResp.read()),dtype=np.uint8)
		#print(img_arr)
		frame = cv2.imdecode(img_arr,1)
	else:
		frame = vs.read()
		frame=cv2.flip(frame,1)
	text = ""

	if frame is None:
		break

	frame = imutils.resize(frame, width=1250)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	if firstFrame is None:
		firstFrame = gray
		continue

	frameDelta = cv2.absdiff(firstFrame, gray)
	threshold = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	threshold = cv2.erode(threshold, None, iterations=2)
	threshold = cv2.dilate(threshold, None, iterations = 2)
	contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = imutils.grab_contours(contours)

	for c in contours:
		if cv2.contourArea(c) < 1000:
			continue
		(x,y,w,h) = cv2.boundingRect(c)

		#cv2.rectangle(frame ,(x,y), (x+w,y+h), (0,0,255), 2)
		text = "Motion Detected"
		cv2.drawContours(frame,contours , -1, (250,0,2), 5)
	cv2.putText(frame, "Status: {}".format(text), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
	
	
	cv2.imshow("Threshold",threshold)
	cv2.imshow("Frame Change", frameDelta)
	cv2.imshow("FRAME", frame)

	#print(type(gray))

	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

vs.stop()
cv2.destroyAllWindows()