import asyncio
import utils
import threading
from bleak import BleakScanner

thread_BLE_running = False
received_data = 0


def start_BLE_scanning():
    while thread_BLE_running:
        asyncio.run(scan_BLE_devices())

async def scan_BLE_devices():
    global received_data
    device = await BleakScanner.find_device_by_address(device_identifier=utils.CUBE_MAC_ADDRESS, timeout=600)
    rec_data = str(device).split(" ")
    received_data = int(rec_data[1])
    print("recieved BLE data:" + str(received_data))

def start_BLE_thread():
    global thread_BLE_running
    if thread_BLE_running == True:
        return 1
    if thread_BLE_running == False:
        thread_BLE_running = True
        thread3 = threading.Thread(target=start_BLE_scanning, daemon=True)
        thread3.start()
        print ("BLE Thread Initialized...")
        return 0
    return 1

def stop_BLE_thread():
    global thread_BLE_running
    if thread_BLE_running == True:
        thread_BLE_running = False
    return 0

def get_new_mode():
    global received_data
    return received_data