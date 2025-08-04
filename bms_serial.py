import serial
from serial.tools import list_ports
import time
import threading
from typing import List
from logger import log_info, log_error, log_warning
from memreader import create_package

class SerialSender:
	def __init__(self, port_names: List[str]):
		self.port_names = port_names
		self.serial_ports: List[serial.Serial] = []
		self.running = False
		self.thread = None
		self.frequency = 250  # default

	def init_ports(self):
		ports_initialized = [port.port for port in self.serial_ports]
		ports_to_initialize = [p for p in self.port_names if p not in ports_initialized]

		for port_name in ports_to_initialize:
			try:
				port = serial.Serial(port_name, 115200)
				self.serial_ports.append(port)
				log_info(f"Connected to {port_name}")
			except serial.SerialException as e:
				port_not_initialized = True
				if "FileNotFoundError" in str(e):
					log_warning(f"Cannot connect to {port_name}: Device not found. Retrying in 5 seconds")
				elif "PermissionError" in str(e):
					log_warning(f"Cannot connect to {port_name}: Permission denied. Retrying in 5 seconds")
				else:
					log_error(f"Error connecting to {port_name}: \"{e}\"")

	def start(self, frequency: int = 250):
		log_info("Starting serial communication")
		self.frequency = frequency
		self.running = True
		self.thread = threading.Thread(target=self._run_loop, daemon=True)
		self.thread.start()

	def _run_loop(self):
		time_passed = 0
		self.init_ports()

		while self.running:
			data = create_package()
			ports_to_remove = []

			for port in self.serial_ports:
				try:
					port.write(data)
				except Exception as e:
					log_error(f"Error writing to {port.port}: {e}")
					ports_to_remove.append(port)

			for port in ports_to_remove:
				try:
					port.close()
				except:
					pass
				self.serial_ports.remove(port)

			if time_passed >= 5000:
				time_passed = 0
				self.init_ports()
			else:
				time_passed += self.frequency

			time.sleep(self.frequency / 1000.0)

	def stop(self):
		log_info("Stopping serial communication")
		self.running = False
		if self.thread and self.thread.is_alive():
			self.thread.join(timeout=1)
		for port in self.serial_ports:
			try:
				port.close()
			except:
				pass
		self.serial_ports.clear()
  
def detect_serial_ports() -> List[str]:
	def port_is_valid(port) -> bool:
		return (port.pid != None and port.vid != None)

	ports = list_ports.comports()
	ports_used = [port.device for port in ports if port_is_valid(port)]

	return ports_used