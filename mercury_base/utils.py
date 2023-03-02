# coding=utf8
from typing import Union
from datetime import datetime


def hex_str(byte_string, splitter='') -> str:
    r"""
    >>> dec_str('\x29\x4A\x00\x31', ' ')
    '29 4A 00 31'
    """
    return splitter.join('%02X' % byte for byte in byte_string)


def dec_str(byte_string, splitter='') -> str:
    r"""
    >>> dec_str('\x29\x4A\x00\x31', ' ')
    '41 74 00 49'
    """
    return splitter.join('%02d' % byte for byte in byte_string)


def to_datetime(from_string: Union[str, bytes], from_format, to_format) -> str:
    r"""
    >>> to_datetime('160123', '%d%m%y', '%Y-%m-%d')
    '2023-01-16'
    >>> to_datetime(b'\x16\x01\x23', '%d%m%y', '%Y-%m-%d')
    '2023-01-16'
    >>> to_datetime(b'\x13\x57\x43\x16\x01\x23', '%H%M%S%d%m%y', '%Y-%m-%d %H:%M:%S')
    '2023-01-16 13:57:43'
    """
    if isinstance(from_string, bytes):
        from_string = hex_str(from_string)
    parsed_datetime = datetime.strptime(from_string, from_format)
    return parsed_datetime.strftime(to_format)


def chunk_string(string, length) -> iter:
    return (string[0 + i:length + i] for i in range(0, len(string), length))
