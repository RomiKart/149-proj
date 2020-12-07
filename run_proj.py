import asyncio
from threading import Thread
import argparse

from tkinter import *

from cv.cv_detection import CV_Detector
from gui.gui import Gui
from ble.ble_comm import BleComm

class Data():
    def __init__(self, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.target_pos = []
        self.current_pos = [200, 200]
        self.angle = 0
        self.width = bottom_right[0] - top_left[0]
        self.height = bottom_right[1] - top_left[1]

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

async def main_async():
    data = Data([150, 41], [540, 386])
    root = Gui(data)
    # entry = Entry(root)
    # entry.grid()
    address = "C0:98:E5:49:00:00"
    ble_comm = BleComm(address)
    
    def spawn_ble_listener():
        print("Spawn BLE")
        return asyncio.ensure_future(ble_comm.test_var(data))

    Button(root, text='Connect', command=spawn_ble_listener).grid()
    await run_tk(root)

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument('--no_cv', action='store_true')
    args = parser.parse_args()

    if args.no_cv:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_async())

    else:
        cv_client = CV_Detector()
        t1 = Thread(target=cv_client.run_cv)
        t1.setDaemon(True)
        t1.start()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_async())
        t1.join()
