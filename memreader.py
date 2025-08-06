import ctypes
from falcon_memreader import falcon_memreader
from logger import log_error

def check_game_active() -> bool:
	data = falcon_memreader.read_shared_memory_stringdata()
	if data == None:
		log_error("Problem when accessing game memory")
		return False
	return str(data.BmsExe) != ""

def get_game_version() -> str:
	data = falcon_memreader.read_shared_memory(falcon_memreader.FlightData2)
	return f"{data.BMSVersionMajor}.{data.BMSVersionMinor}.{data.BMSVersionMicro}"

def create_package() -> bytes:
	flightdata: ctypes.Structure = falcon_memreader.read_shared_memory(falcon_memreader.FlightData)
	flightdata2: ctypes.Structure = falcon_memreader.read_shared_memory(falcon_memreader.FlightData2)
	
	flightdata_bytes = ctypes.string_at(ctypes.byref(flightdata), ctypes.sizeof(flightdata))
	flightdata2_bytes = ctypes.string_at(ctypes.byref(flightdata2), ctypes.sizeof(flightdata2))

	data = flightdata_bytes + flightdata2_bytes
	return data