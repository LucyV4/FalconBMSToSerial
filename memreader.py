import os, sys
import importlib.util
import ctypes

from falcon_memreader import falcon_memreader

class BMSMemReader:
	def create_package(self) -> bytes:
		flightdata: ctypes.Structure = falcon_memreader.read_shared_memory(falcon_memreader.FlightData)
		flightdata2: ctypes.Structure = falcon_memreader.read_shared_memory(falcon_memreader.FlightData2)
		
		flightdata_bytes = ctypes.string_at(ctypes.byref(flightdata), ctypes.sizeof(flightdata))
		flightdata2_bytes = ctypes.string_at(ctypes.byref(flightdata2), ctypes.sizeof(flightdata2))
		
		data = flightdata_bytes + flightdata2_bytes
		return data