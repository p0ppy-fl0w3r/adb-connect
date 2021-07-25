import time
import os
import sys

from ppadb.client import Client


def connect_device(unlock):

    # Run adb on the computer.
    os.system('adb devices')

    client = Client()

    try:
        device = client.devices()[0]
    except IndexError:
        # The list of devices will be emptly if the the device isn't connected properly
        print("The device might not be connected properly")
        time.sleep(2)
        sys.exit()

    try:
        if device:
            
            unlock_device(device, unlock)

            # See if stay awake is on
            awake_status = device.shell("settings get global stay_on_while_plugged_in")\
                        .strip()
            
            if awake_status == "7":
                print("Stay awake seems to be on.")
            # Enable stay awake
            else:
                print("Stay awake isn't on")
                device.shell("settings put global stay_on_while_plugged_in 7")
                print("Stay awake is enabled.")

            # See if the device is connected to an wifi. It's connected get the ip address.
            wlan0 = device.shell("ip addr show wlan0 | grep inet").strip()
            if wlan0 == '''Device "wlan0" does not exist.''':
                print("Wifi not connected\n")
            # If the wifi is not connected try and connect to the wifi
            # This just turns on the wifi.
            # Works only if the device has a saved wifi network.
            device.shell("svc wifi enable")

            bias = 0

            # If the device is connected to wifi the first 5 chars will be 'inet '
            while wlan0[:5] != "inet ":
                
                # If the wifi does not connect in 45 seconds, ask the user to manually connect-
                # to a network
                if bias > 45:
                    print('Failed to connect to a network.')
                    print('Please connect to a network and try again.')
                    sys.exit()

                # Loop until the device is connected to the wifi.
                wlan0 = device.shell("ip addr show wlan0 | grep inet").strip()
                time.sleep(1)
                bias += 1
            print("Connected to wifi.")

            os.system("adb tcpip 5555")
            ip_address = wlan0.split(" ")[1][:13]
            print("Ip address: " + ip_address)
            client.remote_connect(ip_address, 5555)
            print("Connected!!\n")
            os.system("adb devices")
            time.sleep(2)

    except RuntimeError:
        print("The device seems to be offline")
        time.sleep(2)


def unlock_device(device ,unlock):
    """
    Wakes the device and unlocks it.
    """

    if unlock:
        # To wake and unlock device
        # Presses menu
        device.shell("input keyevent 82")
        # Swipes up
        device.shell("input touchscreen swipe 520 1200 520 700")

        # Touch the device @position to get rid of the usb prompt.
        device.shell("input touchscreen tap 520 180")
    else:
        print("Skipping device unlock.")

def show_help():
    print("Pass no arguments to unlock device and connet.")
    print(" h\tShows help.\n u\tDoes not wake or unlock the device.")

if __name__ == '__main__':
    m_args = sys.argv

    if len(m_args) < 3:

        if len(m_args) == 1:
            connect_device(True)

        else:
            if m_args[1] == 'h':
                show_help()
            
            elif m_args[1] == 'u':
                connect_device(False)
    else:
        print("Incorrect arguments.")
        show_help()
        sys.exit()

    
    