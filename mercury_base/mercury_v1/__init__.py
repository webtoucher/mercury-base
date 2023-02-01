# coding=utf8
from mercury_base.mercury_v1 import commands
from struct import pack, unpack


ADDRESS_FORMAT = '!I'  # 4 bytes in network order


def prepare_address(address: int) -> int:
    address %= 100000000
    return address


def format_address(address: int) -> bytes:
    return pack(ADDRESS_FORMAT, address)


def extract_address(message: bytes) -> int:
    address = unpack(ADDRESS_FORMAT, message[:4])[0]
    return address


def extract_command(message: bytes) -> bytes:
    command = list(message[4:5])[0]
    return command


def extract_data(message: bytes) -> list[bytes]:
    data = list(message[5:-2])
    return data
