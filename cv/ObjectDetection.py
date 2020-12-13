import cv2
import sys
import math
import numpy as np

# define a video capture object
vid = cv2.VideoCapture(0)
# width = 600
# height = 400
# count = 0
def onMouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        colorsB = frame[y,x,0]
        colorsG = frame[y,x,1]
        colorsR = frame[y,x,2]
        colors = frame[y,x]
        print("Red: ",colorsR)
        print("Green: ",colorsG)
        print("Blue: ",colorsB)
        print("BRG Format: ",colors)
        print("Coordinates of pixel: X: ",x,"Y: ",y)

cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
cv2.setMouseCallback("frame", onMouse)

while(True):
    ret, frame = vid.read()

    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 65, 255, cv2.THRESH_BINARY_INV)[1]

        cv2.imshow("gray", gray)
        cv2.imshow("blurred", blurred)
        cv2.imshow("thresh", thresh)
        # find contours in the thresholded image
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0]

        # loop over the contours
        for c in cnts:
            # compute the center of the contour
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                # draw the contour and center of the shape on the image
                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
                cv2.putText(frame, "center", (cX - 20, cY - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (36,255,12), 2)
                print(cv2.contourArea(c))

                # show the image
                cv2.imshow("frame", frame)
                cv2.waitKey(0)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()