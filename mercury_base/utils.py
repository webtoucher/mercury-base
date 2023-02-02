# coding=utf8
from typing import Union
from datetime import datetime


def upper_hex(byte: Union[str, bytes, int]) -> str:
    r"""
    >>> upper_hex('\x00')
    '00'
    >>> upper_hex(0x0)
    '00'
    >>> upper_hex(5)
    '05'
    >>> upper_hex(b'\x01')
    '01'
    >>> upper_hex('')
    Traceback (most recent call last):
    ...
    ValueError: expected single byte
    >>> upper_hex(b'')
    Traceback (most recent call last):
    ...
    ValueError: expected single byte
    >>> upper_hex('\x00\x01')
    Traceback (most recent call last):
    ...
    ValueError: expected single byte
    >>> upper_hex(b'\x00\x01')
    Traceback (most recent call last):
    ...
    ValueError: expected single byte
    """
    if isinstance(byte, (str, bytes)):
        if len(byte) != 1:
            raise ValueError('expected single byte')
        if isinstance(byte, str):
            byte = ord(byte)
        elif isinstance(byte, bytes):
            byte = byte[0]
    return '%02X' % byte


def hex_str(byte_string, splitter='') -> str:
    r"""
    >>> hex_str('Python', ' ')
    '50 79 74 68 6F 6E'
    >>> hex_str('\x00\xa1\xb2', ' ')
    '00 A1 B2'
    >>> hex_str([1, 2, 3, 5, 8, 13], ' ')
    '01 02 03 05 08 0D'
    """
    return splitter.join(upper_hex(c) for c in byte_string)


def to_datetime(byte_string, from_format, to_format) -> str:
    r"""
    >>> to_datetime(b'\x16\x01\x23', '%d%m%y', '%Y-%m-%d')
    '2023-01-16'
    >>> to_datetime(b'\x13\x57\x43\x16\x01\x23', '%H%M%S%d%m%y', '%Y-%m-%d %H:%M:%S')
    '2023-01-16 13:57:43'
    """
    from_string = hex_str(byte_string)
    parsed_datetime = datetime.strptime(from_string, from_format)
    return parsed_datetime.strftime(to_format)


def chunk_string(string, length) -> iter:
    return (string[0 + i:length + i] for i in range(0, len(string), length))
