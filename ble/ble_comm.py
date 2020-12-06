import asyncio
from bleak import BleakClient, discover
import struct

address = "C0:98:E5:49:00:00"
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

    async def run_ble(self):
        try:
            print("connecting")
            await self.client.connect()
            print("connected")

            while(True):
                choice = input("Current or Target?\n")
                if (choice == "Current"):
                    x = float(input("X Coord:\n"))
                    y = float(input("Y Coord:\n"))
                    orient = float(input("Orientation:\n"))

                    ba = bytearray(struct.pack("<3f", x, y, orient))
                    await self.client.write_gatt_char(CURRENT_DATA_UUID, ba)
                    print("Done Writing!")
                elif (choice == "Target"):
                    x = float(input("X Coord:\n"))
                    y = float(input("Y Coord:\n"))
                    
                    ba = bytearray(struct.pack("<2f", x, y))
                    await self.client.write_gatt_char(TARGET_DATA_UUID, ba)
                    print("Done Writing!")
        finally:
            # buckler.disconnect()
            print("Disconnecting")
            await self.client.disconnect()
            print("Disconnected")

    async def test_var(self, data):
        while True:
            print(data['target_pos'])
            await asyncio.sleep(5)


if __name__ == "__main__" :
    ble_comm = BleComm(address)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ble_comm.run_ble())