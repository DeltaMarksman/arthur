import serial
import time
import threading

from pydantic import PositiveInt

"""
Arthur Control Protocol
ArCo Protocol

PPPS XXXX
P - Peripheral to control (LED, MOTOR_A, etc.)
S - Sign of value
X - Value to write to peripheral

Special codes
1111 0000           Serial Mode NOT ACTIVE

Message TX          Action
--------------------------------
0000 1111           Turns on LED
0000 0001           Turns off LED
001S XXXX           Throttle Write  /   Motor 1 Read
010S XXXX           Steering Write  /   Motor 2 Read


"""

LED_ON              = 0b00001111
LED_OFF             = 0b00000001
SERIAL_INACTIVE     = 0b11110000
THROTTLE            = 0b00100000
STEERING            = 0b01000000
POSITIVE            = 0b00000000
NEGATIVE            = 0b00010000


# Send input
def send_input():
    while True:
        # Wait for input
        user_input = input()

        match user_input:
            case "l":
                print("Sending LED_ON")
                com.write(bytes([LED_ON]))
                com.flush()
            case "o":
                print("Sending LED_OFF")
                com.write(bytes([LED_OFF]))
                com.flush()
            case "8":
                print("Setting Throttle to positive")
                com.write(bytes([LED_OFF]))
                com.flush()

def print_received():
    # Read line
    while True:
        rx = com.readline()
        if not rx:
            print("No response")
            continue

        # Process the received data
        try:
            decoded_response = rx.decode('utf-8').strip()  # Decode and remove whitespace
            print(f"{decoded_response}")

        # see if its a status byte
        except UnicodeDecodeError:
            rx = rx[0]
            print(rx)
            if rx == SERIAL_INACTIVE:
                print("Activating serial mode")
                com.write(bytes([LED_ON]))
                com.flush()



# Open serial
#/dev/ttyACM0 for RPi port
with serial.Serial(port='COM7', baudrate=9800) as com:
    time.sleep(2)  # wait for Arduino auto-reset to finish
    com.reset_input_buffer()


    print(com.name)
    threading.Thread(target=print_received).start()
    send_input()



