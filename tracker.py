#!/usr/bin/env python

import rospy
from std_msgs.msg import Int32
from geometry_msgs.msg import Pose
import sys
import cv2
import numpy as np 

rospy.init_node("track_colored_object")
cap=cv2.VideoCapture(0)

x_d=0.0
y_d=0.0
x_d_p=0.0
y_d_p=0.0

while(1):
	_, img1 = cap.read()
	img=cv2.flip(img1,1)    
	#converting frame(img i.e BGR) to HSV (hue-saturation-value)

	hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

	blue_lower=np.array([94,123,162],np.uint8)
	blue_upper=np.array([125,255,255],np.uint8)

	red_lower=np.array([169,87,193],np.uint8)
	red_upper=np.array([255,255,255],np.uint8)


	green_lower=np.array([21,77,148],np.uint8)
	green_upper=np.array([43,168,255],np.uint8)


	green=cv2.inRange(hsv,green_lower,green_upper)
	blue=cv2.inRange(hsv,blue_lower,blue_upper)
	red=cv2.inRange(hsv,red_lower,red_upper)

	#Morphological transformation, Dilation  	
	kernal = np.ones((5 ,5), "uint8")


	
	dim=img.shape

	img=cv2.circle(img,(0,int(img.shape[0])),5,(0,0,255),-1)

			
	#Tracking the Green Color
	green=cv2.dilate(green,kernal)

	(_,contours,hierarchy)=cv2.findContours(green,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	if len(contours)>0:
		contour= max(contours,key=cv2.contourArea)
		area = cv2.contourArea(contour)
		#rint(area)
		if area>800: 
			x,y,w,h = cv2.boundingRect(contour)	
			#print(x,y,w,h,int(img.shape[0]))
			lol=int(max(w,h))
			#img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
			img=cv2.circle(img,((2*x+w)/2,(2*y+h)/2),lol/2,(0,100,0),5)
			img=cv2.circle(img,((2*x+w)/2,(2*y+h)/2),5,(0,0,255),-1)
			img=cv2.line(img,(0,int(img.shape[0])),((2*x+w)/2,(2*y+h)/2),(0,255,0),2)
		
			x_d= x
			y_d= int(img.shape[0]) - y - h

			#x_d= (((2*y+h)/2)-0) * 0.06
			#y_d= (((2*x+w)/2)-int(img.shape[0])) * 0.075
			
			s= 'x= ' + str(x_d)  + ',  y= ' + str(y_d)
			cv2.putText(img,s,(x-20,y-5),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255),2,cv2.LINE_AA)
			cv2.putText(img,"GREEN",(x+w+20,y+h+5),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (100,100,0),2,cv2.LINE_AA)



	#Tracking Blue Color	
	blue=cv2.dilate(blue,kernal)
	(_,contours,hierarchy)=cv2.findContours(blue,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	if len(contours)>0:
		contour= max(contours,key=cv2.contourArea)
		area = cv2.contourArea(contour)
		#print(area)
		if area>800: 
			x,y,w,h = cv2.boundingRect(contour)	
			#print(x,y,w,h,int(img.shape[0]))
			lol=int(max(w,h))
			#img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
			img=cv2.circle(img,((2*x+w)/2,(2*y+h)/2),lol/2,(100,0,0),5)
			img=cv2.circle(img,((2*x+w)/2,(2*y+h)/2),5,(0,0,255),-1)
			img=cv2.line(img,(0,int(img.shape[0])),((2*x+w)/2,(2*y+h)/2),(0,255,0),2)
		
			x_d= x
			y_d= int(img.shape[0]) - y - h

			#x_d= (((2*y+h)/2)-0) * 0.06
			#y_d= (((2*x+w)/2)-int(img.shape[0])) * 0.075
			
			s= 'x= ' + str(x_d)  + ',  y= ' + str(y_d)
			cv2.putText(img,s,(x-20,y-5),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255),2,cv2.LINE_AA)
			cv2.putText(img,"BLUE",(x+w+20,y+h+5),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (100,0,0),2,cv2.LINE_AA)


	#Tracking Red Color	
	red=cv2.dilate(red,kernal)
	(_,contours,hierarchy)=cv2.findContours(red,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	if len(contours)>0:
		contour= max(contours,key=cv2.contourArea)
		area = cv2.contourArea(contour)
		#print(area)
		if area>800: 
			x,y,w,h = cv2.boundingRect(contour)	
			#print(x,y,w,h,int(img.shape[0]))
			lol=int(max(w,h))
			#img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
			img=cv2.circle(img,((2*x+w)/2,(2*y+h)/2),lol/2,(0,0,100),5)
			img=cv2.circle(img,((2*x+w)/2,(2*y+h)/2),5,(0,0,255),-1)
			img=cv2.line(img,(0,int(img.shape[0])),((2*x+w)/2,(2*y+h)/2),(0,255,0),2)
		
			x_d= x
			y_d= int(img.shape[0]) - y - h

			#x_d= (((2*y+h)/2)-0) * 0.06
			#y_d= (((2*x+w)/2)-int(img.shape[0])) * 0.075
			
			s= 'x= ' + str(x_d)  + ',  y= ' + str(y_d)
			cv2.putText(img,s,(x-20,y-5),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255),2,cv2.LINE_AA)
			cv2.putText(img,"RED",(x+w+20,y+h+5),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,100),2,cv2.LINE_AA)

			
		
	
	cv2.imshow("Mask GREEN",green)
	cv2.imshow("Mask BLUE",blue)
	cv2.imshow("Mask RED",red)
	cv2.imshow("Object Tracking",img)
	
	if cv2.waitKey(1)== ord('q'):
		break

cap.release()
cv2.destroyAllWindows()