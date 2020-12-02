
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

rospy.init_node("dual_motion_detection")

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
ap.add_argument('-url',"--url", action = 'store_true', help="Takes input from the IP WEBCAM")
ap.add_argument('-cam',"--cam",action = 'store_true', help = "Takes input from device camera")
args = vars(ap.parse_args())


if args["url"]:
    URL = raw_input("Enter the URL of the IP camera : ")
    #print(URL)
    #print(type(URL))
    #URL = "http://192.168.1.8:8080/shot.jpg"
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

blueLower=np.array([94,123,162],np.uint8)
blueUpper=np.array([125,255,255],np.uint8)

greenLower = (25,  51, 123)
greenUpper = (41, 195, 231)

yellowLower = (21,  67, 182)
yellowUpper = (34, 223, 255)

counter = 0
B_direction = ""
BdR = 0
B_perc_area=0

G_direction = ""
GdR = 0
G_perc_area=0


green_centres = deque(maxlen=args["buffer"])
blue_centres = deque(maxlen=args["buffer"])

blue_radii = deque(maxlen=args["buffer"])
green_radii = deque(maxlen=args["buffer"])




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

    blue = cv2.inRange(hsv,blueLower,blueUpper)
    blue = cv2.erode(blue, None, iterations=2)
    blue = cv2.dilate(blue, None, iterations=2)


    blue_contours  = cv2.findContours(blue.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    blue_contours = imutils.grab_contours(blue_contours)
    center = None
    # only proceed if at least one contour was found
    if len(blue_contours) > 0:
        c = max(blue_contours, key=cv2.contourArea)
        area=cv2.contourArea(c)
        if area>800:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius > 10:
                flag = 1
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
            blue_centres.append(center)
            blue_radii.append(radius)



    green = cv2.inRange(hsv,greenLower,greenUpper)
    green = cv2.erode(green, None, iterations=2)
    green = cv2.dilate(green, None, iterations=2)


    green_contours = cv2.findContours(green.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    green_contours = imutils.grab_contours(green_contours)
    center = None
    # only proceed if at least one contour was found
    if len(green_contours) > 0:
        c = max(green_contours, key=cv2.contourArea)
        area=cv2.contourArea(c)
        if area>800:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius > 10:
                flag = 1
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
            green_centres.append(center)
            green_radii.append(radius)



    for i in np.arange(1, len(blue_centres)):
        # if either of the tracked points are None, ignore
        # them
        if blue_centres[i - 1] is None or blue_centres[i] is None:
            continue
        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and blue_centres[-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the B_direction
            # text variables
            BdX = blue_centres[-10][0] - blue_centres[i][0]
            BdY = blue_centres[-10][1] - blue_centres[i][1]
            (BdirX, BdirY) = ("", "")
            # ensure there is significant movement in the
            # x-B_direction
            if np.abs(BdX) > 20:
                BdirX = "LEFT" if np.sign(BdX) == 1 else "RIGHT"
            # ensure there is significant movement in the
            # y-B_direction
            if np.abs(BdY) > 20:
                BdirY = "UP" if np.sign(BdY) == 1 else "DOWN"
            # handle when both B_directions are non-empty
            if BdirX != "" and BdirY != "":
                B_direction = "{}-{}".format(BdirY, BdirX)
            # otherwise, only one B_direction is non-empty
            else:
                B_direction = BdirX if BdirX != "" else BdirY
            BdR = -blue_radii[-10] + blue_radii[i]

            B_area = 3.1415*(blue_radii[i]**2)
            framesize = frame.shape[0]*frame.shape[1]
            B_perc_area = (100*B_area)/framesize
            #print(B_perc_area)




    for i in np.arange(1, len(green_centres)):
        # if either of the tracked points are None, ignore
        # them
        if green_centres[i - 1] is None or green_centres[i] is None:
            continue
        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and green_centres[-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the G_direction
            # text variables
            GdX = green_centres[-10][0] - green_centres[i][0]
            GdY = green_centres[-10][1] - green_centres[i][1]
            (GdirX, GdirY) = ("", "")
            # ensure there is significant movement in the
            # x-G_direction
            if np.abs(GdX) > 20:
                GdirX = "LEFT" if np.sign(GdX) == 1 else "RIGHT"
            # ensure there is significant movement in the
            # y-G_direction
            if np.abs(GdY) > 20:
                GdirY = "UP" if np.sign(GdY) == 1 else "DOWN"
            # handle when both G_directions are non-empty
            if GdirX != "" and GdirY != "":
                G_direction = "{}-{}".format(GdirY, GdirX)
            # otherwise, only one G_direction is non-empty
            else:
                G_direction = GdirX if GdirX != "" else GdirY
            GdR = -green_radii[-10] + green_radii[i]

            G_area = 3.1415*(green_radii[i]**2)
            framesize = frame.shape[0]*frame.shape[1]
            G_perc_area = (100*G_area)/framesize
            #print(G_perc_area)



    for i in range(1, len(blue_centres)):
            if blue_centres[i - 1] is None or blue_centres[i] is None:
                continue
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            #cv2.line(frame, blue_centres[i - 1], blue_centres[i], (255,0,0),thickness)
            cv2.putText(frame, B_direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 255), 3)
            #cv2.putText(frame, " BdR: {} Bdx : {}, Bdy: {}".format(BdR, BdX/10, BdY/10),(frame.shape[1]- 800, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 0, 255), 2)
            #cv2.putText(frame , "Coordinates x:{} y:{} ;  Radius:{} BdR:{} ; Bdx :{} Bdy:{} ; Percentage Area: {}".format(int(x),int(y),int(blue_radii[i]),int(BdR),BdX/10, BdY/10,float(perc_area)),(0, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 0, 255), 2)

            cv2.putText(frame, G_direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 255), 3)
 



            cv2.imshow("BLUE MASK",blue)
            cv2.imshow("GREEN MASK",green)
            cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


vs.stop()
cv2.destroyAllWindows()
