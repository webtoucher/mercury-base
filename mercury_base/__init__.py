# coding=utf8
"""
Toolkit for communicating with Incotex Mercury meters via RS485/CAN bus
Copyright (c) 2023 webtoucher
Distributed under the BSD 3-Clause license. See LICENSE for more info.
"""
import mercury_base.mercury_v1
import mercury_base.mercury_v2
import serial
import time

from mercury_base.utils import hex_str
from modbus_crc import add_crc, check_crc
from operator import itemgetter
from typing import Optional


class ConnectError(Exception):
    pass


class MetersEventListener(object):
    def __init__(self):
        self.__listeners = {
            'connect': [],
            'request': [],
            'answer': [],
        }

    @property
    def on_connect(self):
        def decorator(func):
            self.add_listener('connect', func)
            return func

        return decorator

    @property
    def on_request(self):
        def decorator(func):
            self.add_listener('request', func)
            return func

        return decorator

    @property
    def on_answer(self):
        def decorator(func):
            self.add_listener('answer', func)
            return func

        return decorator

    def add_listener(self, name, func):
        if not self.__listeners[name]:
            self.__listeners.update({name: []})
        if func not in self.__listeners[name]:
            self.__listeners[name].append(func)

    def remove_listener(self, name, func):
        if self.__listeners[name] and func in self.__listeners[name]:
            self.__listeners[name].remove(func)

    def trigger(self, name, *args):
        if not self.__listeners[name]:
            return
        for func in self.__listeners[name]:
            func(*args)


class CommunicationError(Exception):
    pass


class UnexpectedAddress(CommunicationError):
    pass


class UnexpectedCommand(CommunicationError):
    pass


class CheckSumError(CommunicationError):
    pass


class Meter(object):
    def __init__(self, address: int, port: str, listener: Optional[MetersEventListener] = None,
                 baudrate=9600, parity=serial.PARITY_NONE,
                 bytesize=8, stopbits=1, timeout=0.05):
        self.__port = port
        self.__listener = listener
        self.__address = None
        self.__serial_number = None
        self.__model = None
        self.__features = []
        self.__connection = serial.Serial(port=port, baudrate=baudrate, parity=parity,
                                          bytesize=bytesize, stopbits=stopbits, timeout=timeout)

        self.__check_meter(mercury_v1, address) or self.__check_meter(mercury_v2, address)

        if not self.__serial_number:
            raise ConnectError('Meter at address %s did not respond or not supported' % address)
        if self.__listener:
            self.__listener.trigger('connect', self)

    def __check_meter(self, driver, address: int) -> bool:
        self.__driver = driver
        self.__address = driver.prepare_address(address)
        self.__serial_number = self.command('get_serial_number')
        if self.__serial_number:
            self.__model, self.__features = itemgetter('model', 'features')(self.command('get_info'))
            return True
        self.__address = None
        self.__driver = None
        return False

    @property
    def model(self) -> str:
        return self.__model

    @property
    def features(self) -> list[str]:
        return self.__features

    @property
    def serial_number(self) -> int:
        return self.__serial_number

    def has_command(self, command: str) -> bool:
        """ Check if command exists """
        return hasattr(self.__driver.commands, command)

    def command(self, command: str, *params) -> any:
        """ Send command to the meter """
        command_method = getattr(self.__driver.commands, command)
        return command_method(self, *params)

    def test_package(self, package: bytes) -> bool:
        """ Check is package correct for this meter """
        try:
            return self.__address == self.__driver.extract_address(package)
        except Exception:
            return False

    def send_package(self, package: bytes, attempts=5) -> bytes:
        """ Send raw data to the meter """
        buffer_size = 1024
        answer = None
        if not check_crc(package):
            raise CheckSumError('Outgoing package is incorrect')
        self.__connection.write(package)
        if self.__listener:
            self.__listener.trigger('request', self, package)
        while not answer and attempts:
            attempts -= 1
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
                if self.__listener:
                    self.__listener.trigger('answer', self, answer)
        return answer

    def send_command(self, *params, attempts=5) -> Optional[bytes]:
        address = self.__driver.format_address(self.__address)
        package = add_crc(address + bytes(params))
        received_package = self.send_package(package, attempts=attempts)
        if received_package:
            return self.__driver.extract_data(received_package)


if __name__ == '__main__':
    pass
