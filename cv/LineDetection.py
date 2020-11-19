import cv2
import sys
import math
import numpy as np

# define a video capture object
vid = cv2.VideoCapture(0)
width = 600
height = 400
count = 0

while(True):
    # Capture the video frame by frame
    ret, frame = vid.read()

    #Display the initial, detection free frame
    cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', width, height)
    cv2.imshow('frame', frame)
    im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # the 'q' button is set as the quitting button
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Line detection
    dst = cv2.Canny(frame, 50, 200, None, 3)
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, 100, 50, 10)
    cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdst, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
    cv2.namedWindow('detected lines',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('detected lines', width, height)
    cv2.imshow("detected lines", cdst)

    # QR Code
    qrDecoder = cv2.QRCodeDetector()
    retval,data,points,rectifiedImage = qrDecoder.detectAndDecodeMulti(frame)

    # Compact Version
    # for i in range(len(data)):
    #     center_x = (points[i][0][0] + points[i][1][0] + points[i][2][0] + points[i][3][0])/4
    #     center_y = (points[i][0][1] + points[i][1][1] + points[i][2][1] + points[i][3][1])/4
    #     print(data[i] + " X Center: ", center_x)
    #     print(data[i] + " Y Center: ", center_y)

    if len(data) > 0:
        if ("TL" in data):
            TLind = data.index("TL")
            TLx = (points[TLind][0][0] + points[TLind][1][0] + points[TLind][2][0] + points[TLind][3][0])/4
            TLy = (points[TLind][0][1] + points[TLind][1][1] + points[TLind][2][1] + points[TLind][3][1])/4
            print("TL X Center: ", TLx)
            print("TL Y Center: ", TLy, "\n")
        if ("TR" in data):
            TRind = data.index("TR")
            TRx = (points[TRind][0][0] + points[TRind][1][0] + points[TRind][2][0] + points[TRind][3][0])/4
            TRy = (points[TRind][0][1] + points[TRind][1][1] + points[TRind][2][1] + points[TRind][3][1])/4
            print("TR X Center: ", TRx)
            print("TR Y Center: ", TRy, "\n")
        if ("BL" in data):
            BLind = data.index("BL")
            BLx = (points[BLind][0][0] + points[BLind][1][0] + points[BLind][2][0] + points[BLind][3][0])/4
            BLy = (points[BLind][0][1] + points[BLind][1][1] + points[BLind][2][1] + points[BLind][3][1])/4
            print("BL X Center: ", BLx)
            print("BL Y Center: ", BLy, "\n")
        if ("BR" in data):
            BRind = data.index("BR")
            BRx = (points[BRind][0][0] + points[BRind][1][0] + points[BRind][2][0] + points[BRind][3][0])/4
            BRy = (points[BRind][0][1] + points[BRind][1][1] + points[BRind][2][1] + points[BRind][3][1])/4
            print("BR X Center: ", BRx)
            print("BR Y Center: ", BRy, "\n")

    # Homography correction
    pts_actual = np.array([[210, 100], [210, 730], [1100, 100],[1100, 730]]) # from top down image
    pts_camera = np.array([[225, 113],[197, 731],[1100, 86],[1139, 725]]) # from camera feed
    h, status = cv2.findHomography(pts_camera, pts_actual)
    a = np.array([[225, 113]], dtype='float32')
    a = np.array([a])
    adjCoord = cv2.perspectiveTransform(a, h) # convert camera coords to actual coords
    #print(adjCoord) # print actual coordinate for converted point (ie robot position?)
    count+=1

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
