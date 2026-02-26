import serial
import time


def touch():
    com.write("1".encode())


# Open serial
with serial.Serial(port='COM7', baudrate=115200) as com:
    print(com.name)

    while True:
        # Wait for input
        input()
        touch()

