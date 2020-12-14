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
        self.gui_bottom_right = (0, 0)
        self.target_pos = []
        self.current_pos = [200.5, 200.5]
        self.angle = 0
        self.width = bottom_right[0] - top_left[0]
        self.height = bottom_right[1] - top_left[1]
        self.obstacle_pos = []
        self.obs_detection = False

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
    cv_det = CV_Detector(data)
    def spawn_ble_listener():
        print("Spawn BLE")
        root.reroute()
        if ble_debug:
            return asyncio.ensure_future(ble_comm.test_var(data))
        else:
            return asyncio.ensure_future(ble_comm.send_msg(data))

    def spawn_cv_listener():
        print("Spawn CV")
        return asyncio.ensure_future(cv_det.run_cv())
    
    def spawn_obs_listener():
        cv_det.detect_obstacles()
        root.display_obstacles()
        print(root.obstacle_grid)
    
    def spawn_corner_listener():
        print("Detecting corners")
        cv_det.detect_corners()

    content = ttk.Frame(root)
    # content = ttk.Frame(root, padding=(12,12,12,12))
    ttk.Button(content, text='Reset', command=root.reset).grid(row=0, column=4, padx=10)
    ttk.Button(content, text='Connect', command=spawn_ble_listener).grid(row=0, column=3, padx=10)
    ttk.Button(content, text='Detect Romi', command=spawn_cv_listener).grid(row=0, column=2, padx=10)
    ttk.Button(content, text='Detect Obstacles', command=spawn_obs_listener).grid(row=0, column=1, padx=10)
    ttk.Button(content, text='Calibrate', command=spawn_corner_listener).grid(row=0, column=0, padx=10)
    content.grid(row=3, column=0, columnspan=2)
    await run_tk(root)

if __name__ == "__main__" :
    data = Data([150, 41], [540, 386])
    # address = "A6C01837-C772-4ED8-9984-5A006FA27336"
    # address = "0880E3E7-E6A4-4367-A655-9C6E130303A9"
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
