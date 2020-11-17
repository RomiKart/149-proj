import asyncio
from bleak import BleakClient

address = "C0:98:E5:49:00:00"
LED_STATE_UUID = "32e6108a-2b22-4db5-a914-43ce41986c70"
DISPLAY_UUID = "32e6108b-2b22-4db5-a914-43ce41986c70"

async def run(address):
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

# async def run(address):
#     async with BleakClient(address) as client:
#         led_state = await client.read_gatt_char(MODEL_NBR_UUID)
#         print(led_state)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))