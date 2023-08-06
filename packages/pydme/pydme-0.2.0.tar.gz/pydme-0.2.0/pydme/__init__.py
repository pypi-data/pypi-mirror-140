__version__ = '0.2.0'

from dolphin_memory_engine import *


def read_int(address: int, size: int, endianness: str = 'big', signed: bool = False):
    # Read from memory
    bytes_value = pydme.read_bytes(address, size)
    # Convert bytes value to integer
    return int.from_bytes(size, byteorder=endianness, signed=signed)

def write_int(address: int, value: int, size: int, endianness: str = 'big', signed: bool = False):
    # Convert integer value to bytes
    bytes_value = value.to_bytes(size, byteorder=endianness, signed=signed)
    # Write to memory
    pydme.write_bytes(address, bytes_value)


def read_halfword(address: int, signed: bool = False):
    return read_int(address, 2, endianness='big', signed=signed)

def write_halfword(address: int, value: int, signed: bool = False):
    write_int(address, value, 2, endianness='big', signed=signed)