import serial
import time


def touch():
    com.write("1".encode())


# Open serial
with serial.Serial(port='/dev/ttyACM0', baudrate=115200) as com:
    print(com.name)

    while True:
        # Wait for input
        time.sleep(0.1)
        touch()

