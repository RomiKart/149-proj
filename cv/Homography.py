import cv2
import sys
import math
import numpy as np

# define a video capture object
vid = cv2.VideoCapture(1)
# width = 600
# height = 400
# count = 0
def onMouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('x = %d, y = %d'%(x, y))

# lower_yellow = np.array([0, 128, 128])
# upper_yellow = np.array([32, 190, 192])

lower_yellow = np.array([0, 128, 0])
upper_yellow = np.array([32, 190, 255])

while(True):
    ret, frame = vid.read()

    if frame is not None:

        gaus_blur_frame = cv2.GaussianBlur(frame, (5, 5), 0)

        hsv_frame = cv2.cvtColor(gaus_blur_frame, cv2.COLOR_BGR2HSV)

        # Yellow mask
        yellow_mask = cv2.inRange(hsv_frame, lower_yellow, upper_yellow)
        yellow = cv2.bitwise_and(frame, frame, mask=yellow_mask)

        grayscale = cv2.cvtColor(yellow, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(grayscale, 127, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if (contours != []):
            for c in contours:
                M = cv2.moments(c)
                if (M["m00"] != 0):
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    cv2.circle(frame, (cX, cY), 5, (255, 255, 255), -1)

        # Homography correction
        # pts_actual = np.array([[47, 20], [47, 390], [560, 20],[560, 390]]) # from top down image
        # pts_camera = np.array([[130, 156], [32, 382],[471, 154],[573, 388]]) # from camera feed
        # h, status = cv2.findHomography(pts_camera, pts_actual)
        
        # height, width, channels = frame.shape
        # homographized = cv2.warpPerspective(gaus_blur_frame, h, (width, height))

        cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("frame", onMouse)
        cv2.imshow('frame', frame)
        # print(frame[155][378])

        cv2.imshow("Yellow", yellow_mask)
        # cv2.imshow("Thresh", thresh)

        # cv2.imshow("Homography", homographized)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
