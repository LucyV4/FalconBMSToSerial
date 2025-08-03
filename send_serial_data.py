import os, time, sys
import importlib.util
import serial

# Full absolute path to your file
file_path = os.path.abspath("./falcon-memreader/falcon-memreader.py")

# Give it a valid Python module name (replace dash with underscore for convenience)
module_name = "falcon_memreader"

spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

module.examples()

serial_port = serial.Serial("/dev/ttyACM0", 115200)

test_package = bytes(3184)
test_package = os.urandom(3184)


while True:
	serial_port.write(test_package)
	time.sleep(0.5)
 
	print(f"{len(test_package)} bytes sent")