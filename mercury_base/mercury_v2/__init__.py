# coding=utf8
from mercury_base.mercury_v2 import commands
from struct import unpack


def extract_address(message: bytes) -> int:
    address = unpack('!I', message[:1])[0]
    return address


def extract_command(message: bytes) -> bytes:
    command = list(message[1:2])[0]
    return command


def extract_data(message: bytes) -> list[bytes]:
    data = list(message[2:-2])
    return data
