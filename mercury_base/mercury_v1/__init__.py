# coding=utf8
from mercury_base.meter import ADDRESS_FMT
from struct import unpack


def extract_address(message: bytes) -> int:
    address = unpack(ADDRESS_FMT, message[:4])[0]
    return address


def extract_command(message: bytes) -> bytes:
    command = list(message[4:5])[0]
    return command


def extract_data(message: bytes) -> list[bytes]:
    data = list(message[5:-2])
    return data
