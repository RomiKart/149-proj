import asyncio
from bleak import BleakClient, discover
import struct

address = "C0:98:E5:49:00:00"
CURRENT_POS_UUID = "32e6108a-2b22-4db5-a914-43ce41986c70"
TARGET_POS_UUID = "32e6108b-2b22-4db5-a914-43ce41986c70"
CURRENT_ORIENT_UUID = "32e6108c-2b22-4db5-a914-43ce41986c70"

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
                choice = input("Current Pos or Target Pos or Orient?\n")
                if (choice == "Current Pos"):
                    x = float(input("X Coord:\n"))
                    y = float(input("Y Coord:\n"))
                    # current_pos = x
                    # bx = bytearray(struct.pack("f", x))
                    # by = bytearray(struct.pack("f", y))
                    current_pos = [x, y]
                    # led_state = await client.read_gatt_char(LED_STATE_UUID)
                    # led_state = bool(int(led_state.hex()))
                    # print(led_state)
                    print(current_pos)
                    # ba = bytearray(struct.pack("<2f", current_pos))
                    ba = bytearray(struct.pack("<2f", x, y))
                    await self.client.write_gatt_char(CURRENT_POS_UUID, ba)
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
                    await self.client.write_gatt_char(DISPLAY_UUID, bytes(display, 'utf-8'))
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
            await self.client.disconnect()
            print("Disconnected")


if __name__ == "__main__" :
    ble_comm = BleComm(address)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ble_comm.run_ble())