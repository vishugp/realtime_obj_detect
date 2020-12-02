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
n=0
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

	frame = imutils.resize(frame, width=1000)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	if firstFrame is None:
		firstFrame = gray
		previousFrame = gray
		continue

	frameDeltaAbs = cv2.absdiff(firstFrame, gray)
	frameDeltarecent = cv2.absdiff(previousFrame, gray)

	thresholdAbs = cv2.threshold(frameDeltaAbs, 25, 255, cv2.THRESH_BINARY)[1]
	thresholdrecent = cv2.threshold(frameDeltarecent, 25, 255, cv2.THRESH_BINARY)[1]

	thresholdAbs = cv2.erode(thresholdAbs, None, iterations=2)
	thresholdAbs = cv2.dilate(thresholdAbs, None, iterations = 2)
	contoursAbs = cv2.findContours(thresholdAbs.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contoursAbs = imutils.grab_contours(contoursAbs)

	thresholdrecent = cv2.erode(thresholdrecent, None, iterations=2)
	thresholdrecent = cv2.dilate(thresholdrecent, None, iterations = 2)
	contoursrecent = cv2.findContours(thresholdrecent.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contoursrecent = imutils.grab_contours(contoursrecent)

	for c in contoursAbs:
		if cv2.contourArea(c) < 10000:
			continue
		(x,y,w,h) = cv2.boundingRect(c)

		#cv2.rectangle(frame ,(x,y), (x+w,y+h), (0,0,255), 2)
		text = "Motion Detected"
		cv2.drawContours(frame,contoursAbs , -1, (250,0,2), 5)

	for c in contoursrecent:
		if cv2.contourArea(c) < 10000:
			continue
		(x,y,w,h) = cv2.boundingRect(c)

		#cv2.rectangle(frame ,(x,y), (x+w,y+h), (0,0,255), 2)
		text = "Motion Detected"
		cv2.drawContours(frame,contoursAbs , -1, (0,0,255), 10)


	cv2.putText(frame, "Status: {}".format(text), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
	
	
	cv2.imshow("Threshold Absolute",thresholdAbs)
	cv2.imshow("Threshold Recent",thresholdrecent)
	cv2.imshow("Frame Change Absolute", frameDeltaAbs)
	cv2.imshow("Frame Change Recent", frameDeltarecent)
	cv2.imshow("FRAME", frame)

	#print(type(gray))
	if n%10==0:
		gray = gray
		previousFrame = gray

	n+=1
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

vs.stop()
cv2.destroyAllWindows()