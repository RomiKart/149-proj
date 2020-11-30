# inspired from https://stackoverflow.com/questions/30023763/how-to-make-an-interactive-2d-grid-in-a-window-in-python

from tkinter import *
from tkinter import ttk

class Cell():
    FILLED_COLOR_BG = "blue"
    EMPTY_COLOR_BG = "black"
    FILLED_COLOR_BORDER = "blue"
    EMPTY_COLOR_BORDER = "white"

    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x
        self.ord = y
        self.size= size
        self.fill= False

    def _switch(self):
        """ Switch if the cell is filled or not. """
        self.fill= not self.fill

    def draw(self):
        """ order to the cell to draw its representation on the canvas """
        if self.master != None :
            fill = Cell.FILLED_COLOR_BG
            outline = Cell.FILLED_COLOR_BORDER

            if not self.fill:
                fill = Cell.EMPTY_COLOR_BG
                outline = Cell.EMPTY_COLOR_BORDER

            xmin = self.abs * self.size
            xmax = xmin + self.size
            ymin = self.ord * self.size
            ymax = ymin + self.size

            self.master.create_rectangle(xmin, ymin, xmax, ymax, fill = fill, outline = outline)

class CellGrid(Canvas):
    def __init__(self, master, rowNumber, columnNumber, cellSize, *args, **kwargs):
        Canvas.__init__(self, master, width = cellSize * columnNumber , height = cellSize * rowNumber, *args, **kwargs)
        self.parent = master
        self.cellSize = cellSize

        self.g = []
        for row in range(rowNumber):

            line = []
            for column in range(columnNumber):
                line.append(Cell(self, column, row, cellSize))

            self.g.append(line)

        #memorize the cells that have been modified to avoid many switching of state during mouse motion.
        self.switched = []

        #bind click action
        self.bind("<Button-1>", self.handleMouseClick)  
        #bind moving while clicking
        self.bind("<B1-Motion>", self.handleMouseMotion)
        #bind release button action - clear the memory of modified cells.
        self.bind("<ButtonRelease-1>", lambda event: self.switched.clear())

        self.draw()
        self.pack()



    def draw(self):
        for row in self.g:
            for cell in row:
                cell.draw()

    def _eventCoords(self, event):
        row = int(event.y / self.cellSize)
        column = int(event.x / self.cellSize)
        return row, column

    def handleMouseClick(self, event):
        row, column = self._eventCoords(event)
        cell = self.g[row][column]
        cell._switch()
        cell.draw()
        #add the cell to the list of cell switched during the click
        self.switched.append(cell)
        self.parent.coord_var.set(cell.abs)
        # print(self.master.winfo_children())

    def handleMouseMotion(self, event):
        row, column = self._eventCoords(event)
        cell = self.g[row][column]

        if cell not in self.switched:
            cell._switch()
            cell.draw()
            self.switched.append(cell)

class Gui(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.widgets()
    
    def widgets(self):
        self.grid_widget = CellGrid(self, 10, 10, 50)
        self.l1 = ttk.Label(self, text="Coordinates")
        self.coord_var = StringVar()
        self.coord_var.set(10)
        self.l2 = ttk.Label(self, textvariable=self.coord_var)
        
        self.grid_widget.grid(row=0, column=0, columnspan=2)
        self.l1.grid(row=1, column=0)
        self.l2.grid(row=1, column=1)

import asyncio
from bleak import discover, BleakClient


address = "A6C01837-C772-4ED8-9984-5A006FA27336"
# address = "C0:98:E5:49:00:00"
LED_STATE_UUID = "32e6118a-2b22-4db5-a914-43ce41986c70"
DISPLAY_UUID = "32e6108a-2b22-4db5-a914-43ce41986c70"

async def run_ble_2(address):
    client = BleakClient(address)
    try:
        print("connecting")
        # buckler = Peripheral(addr)
        await client.connect()
        print("connected")

        while(True):
            choice = input("LED Set or Message?\n")
            if (choice == "LED Set"):
                state = input("On or Off?\n")
                if state == "On":
                    led_state = True
                else:
                    led_state = False
                # led_state = await client.read_gatt_char(LED_STATE_UUID)
                # led_state = bool(int(led_state.hex()))
                # print(led_state)
                await client.write_gatt_char(LED_STATE_UUID, bytes([led_state]))
                print("Done Writing!")
            elif (choice == "Message"):
                # ch = sv.getCharacteristics(DISPLAY_CHAR_UUID)[0]
                # print(ch.read())
                display = input("Enter a message to write to the display:\n")
                # print(bytes(display, 'utf-8'))
                # print(str(bytes(display, 'utf-8')))
                while (len(display) < 15):
                    display += " "
                # print(display)
                await client.write_gatt_char(DISPLAY_UUID, bytes(display, 'utf-8'))
                print("Printed message to display!")
        # Get service
        # sv = buckler.getServiceByUUID(LED_SERVICE_UUID)
        # # Get characteristic
        # ch = sv.getCharacteristics(LED_CHAR_UUID)[0]

        # while True:
        #     input("Press any key to toggle the LED")
        #     led_state = bool(int(ch.read().hex()))
        #     ch.write(bytes([not led_state]))
    finally:
        # buckler.disconnect()
        print("Disconnecting")
        await client.disconnect()
        print("Disconnected")


async def run_ble():
    print("Starting BLE")
    devices = await discover()
    for d in devices:
        print(d)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(run())

async def run_tk(root, interval=0.05):
    '''
    Run a tkinter app in an asyncio event loop.
    '''
    try:
        while True:
            root.update()
            await asyncio.sleep(interval)
    except TclError as e:
        if "application has been destroyed" not in e.args[0]:
            raise

import cv2
import sys
import math
import numpy as np

async def run_cv():
    # define a video capture object
    vid = cv2.VideoCapture(0)
    # width = 600
    # height = 400
    # count = 0
    def onMouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print('x = %d, y = %d'%(x, y))

    # lower_blue = np.array([110, 50, 50])
    # upper_blue = np.array([130, 255, 255])
    # lower_red = np.array([0, 50, 0])
    # upper_red = np.array([60, 255, 255])

    lower_blue = np.array([88, 240, 64])
    upper_blue = np.array([255, 255, 112])

    lower_green = np.array([64, 128, 32])
    upper_green = np.array([96, 255, 128])

    while(True):
        ret, frame = vid.read()

        if frame is not None:

            gaus_blur_frame = cv2.GaussianBlur(frame, (5, 5), 0)

            # Homography correction
            pts_actual = np.array([[47, 20], [47, 390], [560, 20],[560, 390]]) # from top down image
            pts_camera = np.array([[130, 156], [32, 382],[471, 154],[573, 388]]) # from camera feed
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
                for i in blue_circles[0,:]:
                    cv2.circle(homographized, (i[0],i[1]), 2, (0,0,255), 3)
                blue_cen = blue_circles[0,:][0][:2]

            green_grayscale = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
            green_canny = cv2.Canny(green_grayscale, 50, 240)
            green_circles = cv2.HoughCircles(green_canny, cv2.HOUGH_GRADIENT, dp = 1, minDist = 100, param1 = 10, param2 = 20, minRadius = 1, maxRadius = 120)
            green_cen = []

            if green_circles is not None:
                for i in green_circles[0,:]:
                    cv2.circle(homographized, (i[0],i[1]), 2, (255,0,0), 3)
                green_cen = green_circles[0,:][0][:2]

            if ((green_cen != []) and (blue_cen != [])):
                y_dist = green_cen[1] - blue_cen[1]
                x_dist = green_cen[0] - blue_cen[0]
                angle = np.arctan2(y_dist, x_dist) * 180 / np.pi
                print(angle)

            cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
            cv2.setMouseCallback("frame", onMouse)
            cv2.imshow('frame', frame)
            # print(frame[155][378])

            # cv2.imshow("Blue", blue)
            # cv2.imshow("Red", red)
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



async def main():
    root = Gui()
    entry = Entry(root)
    entry.grid()
    
    def spawn_ble_listener():
        print("Spawn BLE")
        return asyncio.ensure_future(run_ble_2(address))

    def spawn_cv_listener():
        print("Spawn CV")
        return asyncio.ensure_future(run_cv())

    Button(root, text='Connect', command=spawn_ble_listener).grid()
    Button(root, text='CV', command=spawn_cv_listener).grid()
    
    await run_tk(root)

if __name__ == "__main__" :
    # gui = Gui()
    # gui.mainloop()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())