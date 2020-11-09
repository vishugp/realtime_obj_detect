
#!/usr/bin/env python

from collections import deque
import urllib
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import rospy

rospy.init_node("double_motion_detection")


ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
ap.add_argument('-url',"--url", action = 'store_true', help="Takes input from the IP WEBCAM")
ap.add_argument('-cam',"--cam",action = 'store_true', help = "Takes input from device camera")
args = vars(ap.parse_args())


if args["url"]:
    URL = raw_input("Enter the URL of the IP camera : ")

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


blueLower = (94,123, 162)
blueUpper = (125, 255, 255)

greenLower = (25,  51, 123)
greenUpper = (41, 195, 231)

yellowLower = (21,  67, 182)
yellowUpper = (34, 223, 255)

hsvLower = (21,  85, 138)
hsvUpper = (  48, 184, 255)

hsvLower = greenLower
hsvUpper = greenUpper

green_centers = deque(maxlen=args["buffer"])
green_radii = deque(maxlen=args["buffer"])

blue_centers = deque(maxlen=args["buffer"])
blue_radii = deque(maxlen=args["buffer"])
green_counter=0
blue_counter=0

(green_dX,green_dY)=(0,0)
green_direction = ""
flag=0
green_dR = 0
green_perc_area  =0

(blue_dX,blue_dY)=(0,0)
blue_direction = ""
flag=0
blue_dR = 0
blue_perc_area  =0

blue_x = 0
blue_y = 0 
green_x = 0
green_y = 0
blue_R = 0
green_R = 0

while True:
    if(args["url"]==True):
        imgResp = urllib.urlopen(URLS)
        print(type(imgResp))
        img_arr = np.array(bytearray(imgResp.read()),dtype=np.uint8)
        print(img_arr)
        frame = cv2.imdecode(img_arr,1)
    else:
        frame = vs.read()
        frame=cv2.flip(frame,1)
        frame = imutils.resize(frame, width=1200)
    

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
 
    green = cv2.inRange(hsv, hsvLower, hsvUpper)
    green = cv2.erode(green, None, iterations=2)
    green = cv2.dilate(green, None, iterations=2)

    contours = cv2.findContours(green.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    center = None
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        area=cv2.contourArea(c)
        if area>800:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            green_x = x
            green_y = y
            green_R = radius
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius > 10:
                flag = 1
                cv2.circle(frame, (int(x), int(y)), int(radius),(0,100,0), 2)
                cv2.circle(frame, center, 5, (0,100,0), -1)
    if flag ==1:           
        green_centers.appendleft(center)
        green_radii.appendleft(radius)

    for i in np.arange(1, len(green_centers)):

        if green_centers[i - 1] is None or green_centers[i] is None:
            continue

        if green_counter >= 10 and i == 1 and green_centers[-10] is not None:

            green_dX = green_centers[-10][0] - green_centers[i][0]
            green_dY = green_centers[-10][1] - green_centers[i][1]
            (green_dirX, green_dirY) = ("", "")

            if np.abs(green_dX) > 20:
                green_dirX = "LEFT" if np.sign(green_dX) == 1 else "RIGHT"

            if np.abs(green_dY) > 20:
                green_dirY = "UP" if np.sign(green_dY) == 1 else "DOWN"
            if green_dirX != "" and green_dirY != "":
                green_direction = "{}-{}".format(green_dirY, green_dirX)
            else:
                green_direction = green_dirX if green_dirX != "" else green_dirY
            green_dR = green_radii[i] -green_radii[-10] 
            green_area = 3.1415*(radius**2)
            framesize = frame.shape[0]*frame.shape[1]
            green_perc_area = (100*area)/framesize
            

    if len(green_radii)>10:
        green_counter+=1
        for i in range(2, len(green_centers)):
            if green_centers[i - 1] is None or green_centers[i] is None:
                continue
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            print(green_centers[i])
            cv2.line(frame, green_centers[i - 1], green_centers[i], (0,100,0),thickness)
        cv2.putText(frame,"DIRECTION: {} ".format(green_direction) , (0, 30), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0,100,0), 3)
        #cv2.putText(frame, " green_dR: {} green_dX : {}, green_dY: {}".format(green_dR, green_dX/10, green_dY/10),(frame.shape[1]- 800, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 0, 255), 2)
        #cv2.putText(frame , "Coordinates x:{} y:{} ;  Radius:{} green_dR:{} ; green_dX :{} green_dY:{} ; Percentage Area: {}".format(int(x),int(y),int(radius),int(green_dR),green_dX/10, green_dY/10,float(green_perc_area)),(0, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0,100,0), 2)
        cv2.putText(frame , "x:{} y:{} ".format(int(green_x),int(green_y)),(0, 70), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0,100,0), 2)
        cv2.putText(frame , "dx:{} dy:{} ".format(int(green_dX),int(green_dY)),(0, 110), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0,100,0), 2)
         #Radius:{} blue_dR:{} ; blue_dX :{} blue_dY:{} ; Percentage Area: {}".format(int(x),int(y),int(radius),int(blue_dR),blue_dX/10, blue_dY/10,float(blue_perc_area)),(0, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 0, 255), 2)
        cv2.putText(frame , "Radius:{}  dR:{} ".format(int(green_R),int(green_dR)),(0, 150), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0,100,0), 2)

        cv2.imshow("MASK",green)
        cv2.imshow("Frame", frame)
      

    ############################################################################################################################################################################################################################################################################
    blue = cv2.inRange(hsv, blueLower, blueUpper)
    blue = cv2.erode(blue, None, iterations=2)
    blue = cv2.dilate(blue, None, iterations=2)

    contours = cv2.findContours(blue.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    center = None
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        area=cv2.contourArea(c)
        if area>800:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            blue_x = x
            blue_y = y
            blue_R = radius
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius > 10:
                flag = 1
                cv2.circle(frame, (int(x), int(y)), int(radius),(255,0,0), 2)
                cv2.circle(frame, center, 5, (255,0,0), -1)
    if flag ==1:           
        blue_centers.appendleft(center)
        blue_radii.appendleft(radius)

    for i in np.arange(1, len(blue_centers)):

        if blue_centers[i - 1] is None or blue_centers[i] is None:
            continue

        if blue_counter >= 10 and i == 1 and blue_centers[-10] is not None:

            blue_dX = blue_centers[-10][0] - blue_centers[i][0]
            blue_dY = blue_centers[-10][1] - blue_centers[i][1]
            (blue_dirX, blue_dirY) = ("", "")

            if np.abs(blue_dX) > 20:
                blue_dirX = "LEFT" if np.sign(blue_dX) == 1 else "RIGHT"

            if np.abs(blue_dY) > 20:
                blue_dirY = "UP" if np.sign(blue_dY) == 1 else "DOWN"
            if blue_dirX != "" and blue_dirY != "":
                blue_direction = "{}-{}".format(blue_dirY, blue_dirX)
            else:
                blue_direction = blue_dirX if blue_dirX != "" else blue_dirY
            blue_dR = blue_radii[i] -blue_radii[-10] 
            blue_area = 3.1415*(radius**2)
            framesize = frame.shape[0]*frame.shape[1]
            blue_perc_area = (100*area)/framesize
            

    if len(blue_radii)>10:
        blue_counter+=1
        for i in range(2, len(blue_centers)):
            if blue_centers[i - 1] is None or blue_centers[i] is None:
                continue
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            print(blue_centers[i])
            cv2.line(frame, blue_centers[i - 1], blue_centers[i], (255,0,0),thickness)
        cv2.putText(frame,"DIRECTION: {}".format(blue_direction), (900, 30), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 0, 0), 3)
        #cv2.putText(frame, " blue_dR: {} blue_dX : {}, blue_dY: {}".format(blue_dR, blue_dX/10, blue_dY/10),(frame.shape[1]- 800, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 0, 255), 2)
        cv2.putText(frame , "x:{} y:{} ".format(int(blue_x),int(blue_y)),(900, 70), cv2.FONT_HERSHEY_SIMPLEX,0.75, (255,0,0), 2)
        cv2.putText(frame , "dx:{} dy:{} ".format(int(blue_dX),int(blue_dY)),(900, 110), cv2.FONT_HERSHEY_SIMPLEX,0.75, (255,0,0), 2)
        cv2.putText(frame , "Radius:{}  dR:{} ".format(int(blue_R),int(blue_dR)),(900, 150), cv2.FONT_HERSHEY_SIMPLEX,0.75, (255,0,0), 2)
         #Radius:{} blue_dR:{} ; blue_dX :{} blue_dY:{} ; Percentage Area: {}".format(int(x),int(y),int(radius),int(blue_dR),blue_dX/10, blue_dY/10,float(blue_perc_area)),(0, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 0, 255), 2)

        cv2.imshow("MASK",blue)
        cv2.imshow("Frame", frame)




        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

green_centers[-10] 
vs.stop()
cv2.destroyAllWindows()