import os, sys
import importlib.util
import ctypes

file_path = os.path.abspath("./falcon_memreader/falcon-memreader.py")
module_name = "falcon_memreader"
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

class BMSMemReader:
	def create_package(self) -> bytes:
		flightdata: ctypes.Structure = module.read_shared_memory(module.FlightData)
		flightdata2: ctypes.Structure = module.read_shared_memory(module.FlightData2)
		
		flightdata_bytes = ctypes.string_at(ctypes.byref(flightdata), ctypes.sizeof(flightdata))
		flightdata2_bytes = ctypes.string_at(ctypes.byref(flightdata2), ctypes.sizeof(flightdata2))
		
		data = flightdata_bytes + flightdata2_bytes
		return data