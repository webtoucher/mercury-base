# coding=utf8
from mercury_base.mercury_v2 import commands
from struct import pack, unpack

ADDRESS_FORMAT = '!B'  # 1 byte in network order


def prepare_address(address: int) -> int:
    address %= 1000
    if address > 239:
        address %= 100
        if address == 0:
            address = 1
    return address


def format_address(address: int) -> bytes:
    return pack(ADDRESS_FORMAT, address)


def extract_address(message: bytes) -> int:
    address = unpack(ADDRESS_FORMAT, message[:1])[0]
    return address


def extract_command(message: bytes) -> bytes:
    command = list(message[1:2])[0]
    return command


def extract_data(message: bytes) -> list[bytes]:
    data = list(message[2:-2])
    return data
