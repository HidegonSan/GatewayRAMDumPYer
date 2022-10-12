import os
import struct


class GatewayRAMDumper(object):


	def __init__(self, file_path: str) -> None:
		if os.path.exists(file_path) and os.path.isfile(file_path):
			with open(file_path, "rb") as fr:
				self.__bytes = fr.read()
		else:
			raise FileNotFoundError("No such file " + file_path)
		self.__regions = self.__read_header()


	def __read_header(self) -> list:
		regions = []
		regions_count = struct.unpack("I", self.__bytes[0:4])[0]
		for i in range(regions_count):
			# 8  : regions_count + padding
			# 0xC: StartAddress, FileOffset, RegionSize
			region_offset = 8 + i*0xC
			start_address = struct.unpack("I", self.__bytes[ (region_offset + 0x0) : (region_offset + 0x4) ])[0]
			file_offset   = struct.unpack("I", self.__bytes[ (region_offset + 0x4) : (region_offset + 0x8) ])[0]
			region_size   = struct.unpack("I", self.__bytes[ (region_offset + 0x8) : (region_offset + 0xC) ])[0]
			end_address   = start_address + region_size
			regions.append((start_address, end_address, file_offset))
		return regions


	def __is_valid_address(self, address: int, size: int) -> bool:
		for region in self.__regions:
			if (region[0] <= address <= region[1]):
				return address + size <= region[1]
		return False


	def __address_to_file_offset(self, address: int) -> int:
		if (self.__is_valid_address(address, 4)):
			for region in self.__regions:
				if (region[0] <= address <= region[1]):
					return region[2] + (address - region[0])
		return -1


	def __read(self, address: int, size: int) -> int:
		if (self.__is_valid_address(address, size)):
			file_offset = self.__address_to_file_offset(address)
			return struct.unpack(
				{ "1": "B", "2": "H", "4": "I", "8": "Q", "-1": "f", "-2": "d" }[str(size)],
				self.__bytes[
					file_offset : file_offset + (size if 0 < size else { "-1": 4, "-2": 8 }[str(size)])
				])[0]
		return -1


	def read8(self, address: int) -> int:
		return self.__read(address, 1)


	def read16(self, address: int) -> int:
		return self.__read(address, 2)


	def read32(self, address: int) -> int:
		return self.__read(address, 4)


	def read64(self, address: int) -> int:
		return self.__read(address, 8)


	def read_float(self, address: int) -> int:
		return self.__read(address, -1)


	def read_double(self, address: int) -> int:
		return self.__read(address, -2)


	def read_string(self, address: int, size: int, format: str="utf-8") -> str:
		if (self.__is_valid_address(address, size)):
			address = self.__address_to_file_offset(address)
			return self.__bytes[address : address + size].decode(format)
		return ""
