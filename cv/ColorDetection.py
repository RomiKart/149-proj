import cv2
import sys
import math
import numpy as np

# define a video capture object
vid = cv2.VideoCapture(1)

def onMouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('x = %d, y = %d'%(x, y))

# lower_blue = np.array([88, 240, 64])
# upper_blue = np.array([255, 255, 112])

# Actual run
# lower_blue = np.array([96, 128, 64])
# upper_blue = np.array([255, 255, 255])

# lower_blue = np.array([92, 180, 50])
# upper_blue = np.array([128, 255, 255])

# Cyan
lower_blue = np.array([100, 112, 80])
upper_blue = np.array([128, 255, 255])

# lower_green = np.array([64, 128, 32])
# upper_green = np.array([96, 255, 128])

# Actual run
lower_green = np.array([40, 40, 20])
upper_green = np.array([98, 255, 255])

# Yellow
# lower_green = np.array([16, 0, 0])
# upper_green = np.array([32, 255, 225])

blue_x = []
blue_y = []
blue_count = 0
blue_pos = [0, 0]

green_x = []
green_y = []
green_count = 0
green_pos = [0, 0]

median_filt = 5

while(True):
    ret, frame = vid.read()

    if frame is not None:

        gaus_blur_frame = cv2.GaussianBlur(frame, (3, 3), 0)
        # gaus_blur_frame = cv2.medianBlur(frame, 3)

        # Homography correction
        # pts_actual = np.array([[47, 20], [47, 390], [560, 20],[560, 390]]) # from top down image
        # pts_camera = np.array([[130, 156], [32, 382],[471, 154],[573, 388]]) # from camera feed

        # pts_actual = np.array([[132, 391], [564, 381], [520, 43],[158, 39]]) # from top down image
        # pts_camera = np.array([[98, 351], [570, 349],[481, 78],[162, 67]]) # from camera feed

        # Actual run
        pts_actual = np.array([[150, 386], [540, 386], [540, 41],[150, 41]]) # from top down image
        pts_camera = np.array([[64, 412], [573, 402],[477, 102],[143, 92]]) # from camera feed

        h, status = cv2.findHomography(pts_camera, pts_actual)
        
        height, width, channels = frame.shape
        homographized = cv2.warpPerspective(gaus_blur_frame, h, (width, height))

        hsv_frame = cv2.cvtColor(homographized, cv2.COLOR_BGR2HSV)

        # Blue mask
        blue_mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
        blue = cv2.bitwise_and(homographized, homographized, mask=blue_mask)

        # red_mask = cv2.inRange(hsv_frame, lower_red, upper_red)
        # red = cv2.bitwise_and(homographized, homographized, mask=red_mask)

        # Green mask
        green_mask = cv2.inRange(hsv_frame, lower_green, upper_green)
        green = cv2.bitwise_and(homographized, homographized, mask=green_mask)

        # Both colors
        colors = cv2.add(blue, green)

        blue_grayscale = cv2.cvtColor(blue, cv2.COLOR_BGR2HSV)
        blue_canny = cv2.Canny(blue_grayscale, 50, 240)
        blue_circles = cv2.HoughCircles(blue_canny, cv2.HOUGH_GRADIENT, dp = 1, minDist = 100, param1 = 10, param2 = 20, minRadius = 1, maxRadius = 120)
        blue_cen = []

        if blue_circles is not None:
            blue_cen = blue_circles[0,:][0][:2]
            if (len(blue_x) == median_filt):
                blue_x[blue_count] = blue_cen[0]
                blue_y[blue_count] = blue_cen[1]
            else:
                blue_x.append(blue_cen[0])
                blue_y.append(blue_cen[1])

            if (blue_count == median_filt - 1):
                blue_count = 0
            else:
                blue_count += 1

        green_grayscale = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
        green_canny = cv2.Canny(green_grayscale, 50, 240)
        green_circles = cv2.HoughCircles(green_canny, cv2.HOUGH_GRADIENT, dp = 1, minDist = 100, param1 = 10, param2 = 20, minRadius = 1, maxRadius = 120)
        green_cen = []

        if green_circles is not None:
            green_cen = green_circles[0,:][0][:2]
            if (len(green_x) == median_filt):
                green_x[green_count] = green_cen[0]
                green_y[green_count] = green_cen[1]
            else:
                green_x.append(green_cen[0])
                green_y.append(green_cen[1])

            if (green_count == median_filt - 1):
                green_count = 0
            else:
                green_count += 1

        if (len(blue_x) == median_filt):
            blue_pos = [np.median(blue_x), np.median(blue_y)]
            if (blue_cen == []):
                cv2.circle(homographized, (blue_pos[0], blue_pos[1]), 2, (255, 255, 255), 3)
            else:
                cv2.circle(homographized, (blue_pos[0], blue_pos[1]), 2, (0,0,255), 3)
        if (len(green_x) == median_filt):
            green_pos = [np.median(green_x), np.median(green_y)]
            if (green_cen == []):
                cv2.circle(homographized, (green_pos[0], green_pos[1]), 2, (255,255,255), 3)
            else:
                cv2.circle(homographized, (green_pos[0], green_pos[1]), 2, (255,255,0), 3)

        if ((len(blue_x) == median_filt) and (len(green_x) == median_filt)):
            y_dist = green_pos[1] - blue_pos[1]
            x_dist = green_pos[0] - blue_pos[0]
            angle = np.arctan2(y_dist, x_dist) * 180 / np.pi
            print(angle)

        cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("frame", onMouse)
        cv2.imshow('frame', frame)

        # cv2.imshow("Blue", blue)
        # cv2.imshow("Green", green)
        cv2.imshow("Colors", colors)

        cv2.imshow("Homography", homographized)

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
