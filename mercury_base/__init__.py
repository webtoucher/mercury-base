# coding=utf8
"""
Toolkit for communicating with Incotex Mercury meters via RS485/CAN bus
Copyright (c) 2023 webtoucher
Distributed under the BSD 3-Clause license. See LICENSE for more info.
"""
import importlib
import serial
import time

from mercury_base.utils import hex_str
from modbus_crc import add_crc, check_crc
from struct import pack
from typing import Final


class ConnectError(Exception):
    pass


class CommunicationError(Exception):
    pass


class UnexpectedAddress(CommunicationError):
    pass


class UnexpectedCommand(CommunicationError):
    pass


class CheckSumError(CommunicationError):
    pass


ADDRESS_FMT: Final[str] = '!I'  # unsigned integer in network order

TYPE_200: Final[str] = '200'
TYPE_201: Final[str] = '201'
TYPE_203: Final[str] = '203'
TYPE_206: Final[str] = '206'
TYPE_203_2TD: Final[str] = '203.2TD'
TYPE_204: Final[str] = '204'
TYPE_208: Final[str] = '208'
TYPE_230: Final[str] = '230'
TYPE_231: Final[str] = '231'
TYPE_234: Final[str] = '234'
TYPE_236: Final[str] = '236'
TYPE_238: Final[str] = '238'

TYPES_V1: Final[list] = [
    TYPE_200,
    TYPE_201,
    TYPE_203,
    TYPE_206,
]

TYPES_V2: Final[list] = [
    TYPE_203_2TD,
    TYPE_204,
    TYPE_208,
    TYPE_230,
    TYPE_231,
    TYPE_234,
    TYPE_236,
    TYPE_238,
]


class Meter(object):
    def __init__(self, meter_type: str, address: int, port: str, logger=None,
                 baudrate=9600, parity=serial.PARITY_NONE, bytesize=8, stopbits=1, timeout=0.05):
        self.__type = meter_type
        self.__address = address
        self.__port = port
        self.__logger = logger
        self.__serial_number = None

        if meter_type in TYPES_V1:
            module = 'mercury_v1'
        elif meter_type in TYPES_V2:
            raise ConnectError('Meter Mercury %s is not supported yet' % meter_type)
        else:
            raise ConnectError('Meter Mercury %s is not supported' % meter_type)

        self.__driver = importlib.import_module('.%s' % module, __package__)
        self.__connection = serial.Serial(port=port, baudrate=baudrate, parity=parity,
                                          bytesize=bytesize, stopbits=stopbits, timeout=timeout)
        self.__serial_number = self.command('get_serial_number')
        if not self.__serial_number:
            raise ConnectError('Meter at address %s did not respond' % self.__address)
        if self.__logger:
            self.__logger.info('Meter with serial number %s is connected', self.__serial_number)

    @property
    def type(self):
        return self.__type

    @property
    def serial_number(self):
        return self.__serial_number

    def has_command(self, command) -> bool:
        """ Check if command exists """
        return hasattr(self.__driver.commands, command)

    def command(self, command, *params):
        """ Send command to the meter """
        command_method = getattr(self.__driver.commands, command)
        return command_method(self, *params)

    def send_package(self, package: bytes, attempts=3):
        """ Send raw data to the meter """
        buffer_size = 1024
        answer = None
        if not check_crc(package):
            raise CheckSumError('Outgoing package is incorrect')
        while not answer and attempts:
            attempts -= 1
            self.__connection.write(package)
            if self.__logger:
                self.__logger.debug('--> [%s]\t%s', self.__serial_number or 'new meter', hex_str(package, ' '))
            time.sleep(0.1)
            answer = self.__connection.read(buffer_size)
            if answer:
                if not check_crc(answer):
                    raise CheckSumError('Incoming package is incorrect')
                address = self.__driver.extract_address(answer)
                if address != self.__driver.extract_address(package):
                    raise UnexpectedAddress(address)
                command = self.__driver.extract_command(answer)
                if command != self.__driver.extract_command(package):
                    raise UnexpectedCommand(command)
                if self.__logger:
                    self.__logger.debug('<-- [%s]\t%s', self.__serial_number or 'new meter', hex_str(answer, ' '))
        return answer

    def send_command(self, *params, attempts=3):
        address = pack(ADDRESS_FMT, self.__address)
        package = add_crc(address + bytes(params))
        received_package = self.send_package(package, attempts=attempts)
        return self.__driver.extract_data(received_package)


if __name__ == '__main__':
    pass
