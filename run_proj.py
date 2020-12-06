import asyncio
from threading import Thread
import argparse

from tkinter import *

from cv.cv_detection import CV_Detector
from gui.gui import Gui
from ble.ble_comm import BleComm

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
    data = {'target_pos': []}
    root = Gui(data)
    entry = Entry(root)
    entry.grid()
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
