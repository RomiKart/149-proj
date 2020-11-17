import cv2
import sys
import math
import numpy as np
# import pyzbar.pyzbar as pyzbar

# define a video capture object
vid = cv2.VideoCapture(0)
width = 600
height = 400

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
            #print(i, " line detected: x1 = ", l[0], "x2 = ", l[1], "y1 = ", l[2], "y2 = ", l[3])
            cv2.line(cdst, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
    cv2.namedWindow('detected lines',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('detected lines', width, height)
    cv2.imshow("detected lines", cdst)


    # QR code reader for four corners
    # decodedObjects = pyzbar.decode(im)
    # for obj in decodedObjects:
    #     print('Type : ', obj.type)
    #     print('Data : ', obj.data,'\n')

    # currently testing that it can read the QR code image directly
    topLeftQR = cv2.imread("TopLeftCorner.png")
    #topLeftQR = cv2.imread(im)
    topRightQR = cv2.imread("TopRightCorner.png")
    bottomLeftQR = cv2.imread("BottomLeftCorner.png")
    bottomRightQR = cv2.imread("BottomRightCorner.png")

    qrDecoderTL = cv2.QRCodeDetector()
    dataTL,pointsTL,rectifiedImageTL = qrDecoderTL.detectAndDecode(topLeftQR)
    qrDecoderTR = cv2.QRCodeDetector()
    dataTR,pointsTR,rectifiedImageTR = qrDecoderTR.detectAndDecode(topRightQR)
    qrDecoderBL = cv2.QRCodeDetector()
    dataBL,pointsBL,rectifiedImageBL = qrDecoderBL.detectAndDecode(bottomLeftQR)
    qrDecoderBR = cv2.QRCodeDetector()
    dataBR,pointsBR,rectifiedImageBR = qrDecoderBR.detectAndDecode(bottomRightQR)
    # #print(qrDecoderBR.detectAndDecode(bottomRightQR))
    # pts = pointsBR
    # for i in range(pts):
    #     nextPointIndex = (i+1) % pts
    #     cv2.line(bottomRightQR, tuple(pointsBR[i][0]), tuple(pointsBR[nextPointIndex][0]), (255,0,0), 5)
    #     print(pointsBR[i][0])

    if len(dataTL) > 0:
        TLx = (pointsTL[0][0][0] + pointsTL[0][1][0] + pointsTL[0][2][0] + pointsTL[0][3][0])/4
        TLy = (pointsTL[0][0][1] + pointsTL[0][1][1] + pointsTL[0][2][1] + pointsTL[0][3][1])/4
        print("TL X Center: ", TLx)
        print("TL Y Center: ", TLy)
    if len(dataTR) > 0:
        TRx = (pointsTR[0][0][0] + pointsTR[0][1][0] + pointsTR[0][2][0] + pointsTR[0][3][0])/4
        TRy = (pointsTR[0][0][1] + pointsTR[0][1][1] + pointsTR[0][2][1] + pointsTR[0][3][1])/4
        print("TR X Center: ", TRx)
        print("TR Y Center: ", TRy)
    if len(dataBL) > 0:
        print(pointsBL)
        BLx = (pointsBL[0][0][0] + pointsBL[0][1][0] + pointsBL[0][2][0] + pointsBL[0][3][0])/4
        BLy = (pointsBL[0][0][1] + pointsBL[0][1][1] + pointsBL[0][2][1] + pointsBL[0][3][1])/4
        print("BL X Center: ", BLx)
        print("BL Y Center: ", BLy)
    if len(dataBR) > 0:
        BRx = (pointsBR[0][0][0] + pointsBR[0][1][0] + pointsBR[0][2][0] + pointsBR[0][3][0])/4
        BRy = (pointsBR[0][0][1] + pointsBR[0][1][1] + pointsBR[0][2][1] + pointsBR[0][3][1])/4
        print("BR X Center: ", BRx)
        print("BR Y Center: ", BRy)
        print(pointsBR)


    # Homography correction
    pts_actual = np.array([[210, 100], [210, 730], [1100, 100],[1100, 730]]) # from top down image
    pts_camera = np.array([[225, 113],[197, 731],[1100, 86],[1139, 725]]) # from camera feed
    h, status = cv2.findHomography(pts_camera, pts_actual)
    a = np.array([[225, 113]], dtype='float32')
    a = np.array([a])
    adjCoord = cv2.perspectiveTransform(a, h) # convert camera coords to actual coords
    print(adjCoord) # print actual coordinate for converted point (ie robot position?)


# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
