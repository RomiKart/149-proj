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

while(True):
    ret, frame = vid.read()

    if frame is not None:

        gaus_blur_frame = cv2.GaussianBlur(frame, (7, 7), 0)

        # Homography correction
        pts_actual = np.array([[47, 20], [47, 390], [560, 20],[560, 390]]) # from top down image
        pts_camera = np.array([[130, 156], [32, 382],[471, 154],[573, 388]]) # from camera feed
        h, status = cv2.findHomography(pts_camera, pts_actual)
        
        height, width, channels = frame.shape
        homographized = cv2.warpPerspective(gaus_blur_frame, h, (width, height))

        hsv_frame = cv2.cvtColor(homographized, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([110, 50, 50])
        upper_blue = np.array([130, 255, 255])
        # blue_mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
        # blue = cv2.bitwise_and(homographized, homographized, mask=blue_mask)

        lower_red = np.array([0, 50, 0])
        upper_red = np.array([60, 255, 255])
        red_mask = cv2.inRange(hsv_frame, lower_red, upper_red)
        red = cv2.bitwise_and(homographized, homographized, mask=red_mask)

        # blue_grayscale = cv2.cvtColor(blue, cv2.COLOR_BGR2HSV)
        # blue_canny = cv2.Canny(blue_grayscale, 50, 240)
        # circles = cv2.HoughCircles(blue_canny, cv2.HOUGH_GRADIENT, dp = 1, minDist = 100, param1 = 10, param2 = 20, minRadius = 1, maxRadius = 120)
        # cir_cen = []

        # if circles is not None:
        #     for i in circles[0,:]:
        #         # cv2.circle(frame, (i[0],i[1]), i[2], (0,255,0), 2)
        #         cv2.circle(homographized, (i[0],i[1]), 2, (0,0,255), 3)

        cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("frame", onMouse)
        cv2.imshow('frame', frame)
        # print(frame[155][378])

        # cv2.namedWindow('Blue',cv2.WINDOW_NORMAL)
        # cv2.imshow("Blue", blue)
        cv2.imshow("Red", red)

        # cv2.imshow("Homography", homographized)

    # dst = cv2.Canny(frame, 100, 150, None, 3)
    # linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, 100, 50, 10)
    # cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    # if linesP is not None:
    #     for i in range(0, len(linesP)):
    #         l = linesP[i][0]
    #         cv2.line(cdst, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
    # cv2.imshow("detected lines", cdst)
    # # the 'q' button is set as the quitting button
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Line detection
    # a = np.array([[225, 113]], dtype='float32')
    # a = np.array([a])
    # adjCoord = cv2.perspectiveTransform(frame, h) # convert camera coords to actual coords
    # print(adjCoord) # print actual coordinate for converted point (ie robot position?)

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
