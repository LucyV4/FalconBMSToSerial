import serial
import asyncio
import threading
from typing import List
from memreader import BMSMemReader

memReader = BMSMemReader()

class SerialSender:
	def __init__(self, port_names: List[str]):
		self.serial_ports: List[serial.Serial] = []
		self.port_names = port_names
	
	def init_ports(self):
		ports_initialized = [port.port for port in self.serial_ports]
		ports_to_initialize = [port_name for port_name in self.port_names if port_name not in ports_initialized]
  
		for port_name in ports_to_initialize:
			try:
				port = serial.Serial(port_name, 115200)
				self.serial_ports.append(port)
				print(f"Connected to {port_name}")
			except serial.SerialException as e:
				if "FileNotFoundError" in str(e): print(f"Error connecting to {port_name}: Serial device does not exist. Retrying in 5 seconds.")
				elif "PermissionError" in str(e): print(f"Error connecting to {port_name}: No permission. Retrying in 5 seconds.")
				else: print(f"Error connecting to {port_name}: \"{e}\". Retrying in 5 seconds")
    
 
	def start(self, frequency: int = 250):
		print(f"STARTING SERIAL COMMUNICATION")
		self.frequency = frequency
  
		# Runs it asynchronously in a separate thread
		self.loop = asyncio.new_event_loop()
		self.t = threading.Thread(target=self.start_loop)
		self.t.start()
  
		self.task = asyncio.run_coroutine_threadsafe(self.send(), self.loop)
	
	def stop(self):
		print(f"STOPPING SERIAL COMMUNICATION")

		# Stops the task safely
		self.task.cancel()
		self.loop.call_soon_threadsafe(self.loop.stop)
		self.t.join()

		for port in self.serial_ports:
			port.close()
		self.serial_ports.clear()
	
	def start_loop(self):
		asyncio.set_event_loop(self.loop)
		self.loop.run_forever()

	async def send(self):
		self.init_ports()

		time_passed = 0
		invalid_ports = []
		while True:
			data = memReader.create_package()
			ports_to_remove = []
			for port in self.serial_ports:
				try:
					port.write(data)
				except Exception as e:
					print(f"Error writing to {port.port}: {e}")
					ports_to_remove.append(port)
			
			for port in ports_to_remove: self.serial_ports.remove(port)

			await asyncio.sleep(self.frequency/1000)

			if time_passed >= 5000:
				time_passed -= 5000
				self.init_ports()
			else: time_passed += self.frequency