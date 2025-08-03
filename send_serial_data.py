import os, time
import serial

serial_port = serial.Serial("/dev/ttyACM0", 115200)

test_package = bytes(3184)
test_package = os.urandom(3184)

while True:
	serial_port.write(test_package)
	time.sleep(0.5)
 
	print(f"{len(test_package)} bytes sent")