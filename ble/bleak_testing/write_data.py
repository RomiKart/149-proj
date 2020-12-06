import asyncio
from bleak import BleakClient
import struct

#address = "C0:98:E5:49:00:00"
address = "2A3BDD95-BECD-4344-9ACA-40F62BDB59A7"
CURRENT_DATA_UUID = "32e6108a-2b22-4db5-a914-43ce41986c70"
TARGET_DATA_UUID = "32e6108b-2b22-4db5-a914-43ce41986c70"

async def run(address):
    client = BleakClient(address)
    try:
        print("connecting")
        await client.connect()
        print("connected")

        ind = 0
        test_pos = [[0, 0, 270], [0, 1, 270], [0, 2, 270], [0, 3, 270], [0, 3, 180], [1, 3, 180], [2, 3, 180], [3, 3, 180], [3, 3, 270], [3, 4, 270], [3, 5, 270], [3, 5, 360], [2, 5, 360], [2, 5, 90], [2, 4, 90], [2, 3, 90], [2, 2, 90], [2, 1, 90],[2, 0, 90], [2, 0, 360], [1, 0, 360], [0, 0, 360]]
        targs = [[0, 3], [1, 3], [3, 3], [3, 5], [2, 5], [2, 0], [0, 0]]

        ba = bytearray(struct.pack("<14f", targs[0][0], targs[0][1], targs[1][0], targs[1][1],targs[2][0], targs[2][1],targs[3][0], targs[3][1],targs[4][0], targs[4][1],targs[5][0], targs[5][1],targs[6][0], targs[6][1]))
        await client.write_gatt_char(TARGET_DATA_UUID, ba)
        print("Done Writing Target Positions!")

        while(True):
            choice = input("n for next position?\n")
            if (choice == "n"):
                x = test_pos[ind][0]
                y = test_pos[ind][1]
                orient = test_pos[ind][2]
                ind += 1

                ba = bytearray(struct.pack("<3f", x, y, orient))
                await client.write_gatt_char(CURRENT_DATA_UUID, ba)
                print("Done Writing Current Position!")
                print(x, y, orient)
    finally:
        print("Disconnecting")
        await client.disconnect()
        print("Disconnected")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
