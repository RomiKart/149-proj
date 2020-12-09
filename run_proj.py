import asyncio
from threading import Thread
import argparse

from tkinter import *
from tkinter import ttk

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

async def main_async(root, ble_comm, ble_debug=False):
    
    def spawn_ble_listener():
        print("Spawn BLE")
        if ble_debug:
            return asyncio.ensure_future(ble_comm.test_ble(data))
        else:
            return asyncio.ensure_future(ble_comm.send_msg(data))

    def spawn_cv_listener():
        print("Spawn CV")
        cv_dec = CV_Detector(data)
        return asyncio.ensure_future(cv_dec.run_cv())

    ttk.Button(root, text='Connect', command=spawn_ble_listener).grid()
    ttk.Button(root, text='CV', command=spawn_cv_listener).grid()
    await run_tk(root)

if __name__ == "__main__" :
    data = Data([150, 41], [540, 386])
    address = "C0:98:E5:49:00:00"
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--thread', action='store_true', default=False)
    parser.add_argument('--ble_debug', action='store_true', default=False)
    parser.add_argument('--gui_debug', action='store_true', default=False)
    args = parser.parse_args()

    root = Gui(data, args.gui_debug)
    ble_comm = BleComm(address)

    if not args.thread:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_async(root, ble_comm, args.ble_debug))

    else:
        cv_client = CV_Detector(data)
        t1 = Thread(target=cv_client.run_cv)
        t1.setDaemon(True)
        t1.start()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_async(root, ble_comm, args.ble_debug))
        t1.join()
