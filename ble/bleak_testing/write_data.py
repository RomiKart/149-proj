import asyncio
from bleak import BleakClient
import struct

address = "C0:98:E5:49:00:00"
CURRENT_DATA_UUID = "32e6108a-2b22-4db5-a914-43ce41986c70"
TARGET_DATA_UUID = "32e6108b-2b22-4db5-a914-43ce41986c70"

async def run(address):
    client = BleakClient(address)
    try:
        print("connecting")
        await client.connect()
        print("connected")

        while(True):
            choice = input("Current or Target?\n")
            if (choice == "Current"):
                x = float(input("X Coord:\n"))
                y = float(input("Y Coord:\n"))
                orient = float(input("Orientation:\n"))

                ba = bytearray(struct.pack("<3f", x, y, orient))
                await client.write_gatt_char(CURRENT_DATA_UUID, ba)
                print("Done Writing!")
            elif (choice == "Target"):
                x = float(input("X Coord:\n"))
                y = float(input("Y Coord:\n"))
                
                ba = bytearray(struct.pack("<2f", x, y))
                await client.write_gatt_char(TARGET_DATA_UUID, ba)
                print("Done Writing!")
    finally:
        # buckler.disconnect()
        print("Disconnecting")
        await client.disconnect()
        print("Disconnected")

# async def run(address):
#     async with BleakClient(address) as client:
#         led_state = await client.read_gatt_char(MODEL_NBR_UUID)
#         print(led_state)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))