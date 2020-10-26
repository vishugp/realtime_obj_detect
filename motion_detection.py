
#!/usr/bin/env python

from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

blueLower = (94,123, 162)
blueUpper = (125, 255, 255)
greenLower = (28,42, 181)
greenUpper = (64, 255, 255)

pts = deque(maxlen=args["buffer"])

counter=0
(dX,dY)=(0,0)
direction = "lol"

vs = VideoStream(0).start()
time.sleep(2.0)

while True:
   
    frame = vs.read()
    frame=cv2.flip(frame,1)
    frame = imutils.resize(frame, width=1200)

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
 
    blue = cv2.inRange(hsv, blueLower, blueUpper)
    blue = cv2.erode(blue, None, iterations=2)
    blue = cv2.dilate(blue, None, iterations=2)

    contours = cv2.findContours(blue.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    center = None
    # only proceed if at least one contour was found
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        area=cv2.contourArea(c)
        if area>800:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
    pts.appendleft(center)


    for i in np.arange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue
        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and pts[-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the direction
            # text variables
            dX = pts[-10][0] - pts[i][0]
            dY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ("", "")
            # ensure there is significant movement in the
            # x-direction
            if np.abs(dX) > 20:
                dirX = "LEFT" if np.sign(dX) == 1 else "RIGHT"
            # ensure there is significant movement in the
            # y-direction
            if np.abs(dY) > 20:
                dirY = "UP" if np.sign(dY) == 1 else "DOWN"
            # handle when both directions are non-empty
            if dirX != "" and dirY != "":
                direction = "{}-{}".format(dirY, dirX)
            # otherwise, only one direction is non-empty
            else:
                direction = dirX if dirX != "" else dirY


    # loop over the set of tracked points
    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (255,0,0),thickness)
    #print(dX,dY,direction)
    cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 255), 3)
    cv2.putText(frame, "dx: {}, dy: {}".format(dX/10, dY/10),(frame.shape[1]- 250, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 255), 1)
    

    cv2.imshow("MASK",blue)
    cv2.imshow("Frame", frame)
    
    counter+=1
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


vs.stop()
cv2.destroyAllWindows()
