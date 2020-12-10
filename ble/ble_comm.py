import asyncio
from bleak import BleakClient, discover
import struct
import numpy as np

CURRENT_DATA_UUID = "32e6108a-2b22-4db5-a914-43ce41986c70"
TARGET_DATA_UUID = "32e6108b-2b22-4db5-a914-43ce41986c70"

class BleComm():
    def __init__(self, address):
        print("Connecting to address: {}".format(address))
        self.client = BleakClient(address)

    async def scan(self):
        print("Running scan")
        while True:
            devices = await discover()
            for d in devices:
                print(d)

    async def test_ble(self, data):
        try:
            print("connecting")
            await self.client.connect()
            print("connected")
            counter = 0

            while(True):
                x = data.current_pos[0]
                y = data.current_pos[1]
                target_orient = np.arctan2(data.target_pos[0][1] - y, data.target_pos[0][0] - x) * 180 / np.pi
                counter += 1 
                if (data.angle <= 0):
                    orient = data.angle + 360
                else:
                    orient = data.angle

                ba = bytearray(struct.pack("<3f", x, y, counter))
                print("Before:", counter)
                await self.client.write_gatt_char(CURRENT_DATA_UUID, ba)
                print("After:", counter)
                if counter == 30000:
                    break
                await asyncio.sleep(.2)
        finally:
            print("Disconnecting")
            await self.client.disconnect()
            print("Disconnected")

    # async def test_var(self, data):
    #     while True:
    #         print(data.target_pos)
    #         await asyncio.sleep(5)

    async def send_msg(self, data):
        try:
            print("connecting")
            await self.client.connect()
            print("connected")
            print(data.target_pos)
            targs = data.target_pos
            flattened = np.ravel(targs)
            ba = bytearray(struct.pack('{}f'.format(len(flattened)), *flattened))
            await self.client.write_gatt_char(TARGET_DATA_UUID, ba)
            print("Done Writing Target Positions!")

            while(True):
                x = data.current_pos[0]
                y = data.current_pos[1]
                target_orient = np.arctan2(data.target_pos[0][1] - y, data.target_pos[0][0] - x) * 180 / np.pi
                if (data.angle <= 0):
                    orient = data.angle + 360
                else:
                    orient = data.angle

                ba = bytearray(struct.pack("<3f", x, y, orient))
                await self.client.write_gatt_char(CURRENT_DATA_UUID, ba)
                # print("Done Writing Current Position!")
                print(x, y, orient, target_orient)
                await asyncio.sleep(.2)
        finally:
            print("Disconnecting")
            await self.client.disconnect()
            print("Disconnected")


if __name__ == "__main__" :
    address = "C0:98:E5:49:00:00"
    
    ble_comm = BleComm(address)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ble_comm.run_ble())