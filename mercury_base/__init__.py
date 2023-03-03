# coding=utf8
"""
Toolkit for communicating with Incotex Mercury meters via RS485/CAN bus
Copyright (c) 2023 webtoucher
Distributed under the BSD 3-Clause license. See LICENSE for more info.
"""
import mercury_base.mercury_v1
import mercury_base.mercury_v2
import re
import serial
import time

from abc import ABC, abstractmethod
from event_bus import EventBus
from mercury_base.utils import hex_str
from modbus_crc import add_crc, check_crc
from operator import itemgetter
from pathlib import Path
from simple_socket_client import SimpleSocketClient, SimpleSocketClientException
from typing import Optional


class ConnectError(Exception):
    pass


class TransportError(Exception):
    pass


class CommunicationError(Exception):
    pass


class UnexpectedAddress(CommunicationError):
    pass


class UnexpectedCommand(CommunicationError):
    pass


class CheckSumError(CommunicationError):
    pass


class DataTransport(ABC):
    def __init__(self):
        self.port = None

    @abstractmethod
    def ask(self, package: bytes):
        pass


class SerialDataTransport(DataTransport):
    def __init__(self, port: str, baudrate=9600, parity=serial.PARITY_NONE, bytesize=8, stopbits=1, timeout=0.05):
        super().__init__()
        self.port = port
        try:
            self.__connection = serial.Serial(port=port, baudrate=baudrate, parity=parity,
                                              bytesize=bytesize, stopbits=stopbits, timeout=timeout)
        except serial.serialutil.SerialException as err:
            if len(err.args) > 1:
                raise TransportError(port, err.args[1]) from err
            raise TransportError(port, err.args[0]) from err

    def ask(self, package: bytes):
        buffer_size = 1024
        attempts = 5
        answer = None
        self.__connection.write(package)
        while not answer and attempts:
            attempts -= 1
            time.sleep(0.1)
            answer = self.__connection.read(buffer_size)
        return answer


class TcpDataTransport(DataTransport):
    def __init__(self, host: str, port: int, timeout=5):
        super().__init__()
        self.port = '%s:%s' % (host, port)
        self.__connection = SimpleSocketClient(host, port)
        try:
            self.__connection.connect(timeout=timeout)
        except SimpleSocketClientException as err:
            raise TransportError(self.port, err.args[0]) from err

    def ask(self, package: bytes):
        try:
            return self.__connection.ask(package)
        except TimeoutError:
            return None


class Meter(object):
    def __init__(self, address: int, transport: DataTransport, event_bus: Optional[EventBus] = None):
        self.__transport = transport
        self.__event_bus = event_bus
        self.__address = None
        self.__serial_number = None
        self.__model = None
        self.__features = []

        self.__check_meter(mercury_v1, address) or self.__check_meter(mercury_v2, address)

        if not self.__serial_number:
            raise ConnectError('Meter at address %s did not respond or not supported' % address)
        if self.__event_bus:
            self.__event_bus.emit('connect', self)

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

    def send_package(self, package: bytes) -> bytes:
        """ Send raw data to the meter """
        if not check_crc(package):
            raise CheckSumError('Outgoing package is incorrect')
        if self.__event_bus:
            self.__event_bus.emit('request', self, package)
        answer = self.__driver.cache.get(package, self.__transport.ask(package))
        if answer:
            if not check_crc(answer):
                raise CheckSumError('Incoming package is incorrect')
            address = self.__driver.extract_address(answer)
            if address != self.__driver.extract_address(package):
                raise UnexpectedAddress(address)
            command = self.__driver.extract_command(answer)
            if command and command != self.__driver.extract_command(package):
                raise UnexpectedCommand(command)
            if self.__event_bus:
                self.__event_bus.emit('answer', self, answer)
        return answer

    def send_command(self, *params) -> Optional[bytes]:
        address = self.__driver.format_address(self.__address)
        package = add_crc(address + bytes(params))
        received_package = self.send_package(package)
        if received_package:
            return self.__driver.extract_data(received_package)


class Meters(object):
    """ Collection of connected meters """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.__meters: list[Meter] = []
        self.__event_bus = event_bus

    def connect_meter(self, address: int, transport: DataTransport, **kwarg) -> bool:
        """ Connect a meter and add it to the collection """
        params = {'event_bus': self.__event_bus}
        params.update(kwarg)
        try:
            self.add_meter(Meter(address, transport, **params))
            return True
        except ConnectError as err:
            if self.__event_bus:
                self.__event_bus.emit('failed_connect', address, transport.port, err.args[0])
            return False

    def connect_meter_by_port(self, address: int, port: str, **kwarg) -> bool:
        """ Connect a meter by port string and add it to the collection """
        try:
            matched = re.search(r"^(?P<host>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(?P<port>\d+)$", port)
            if matched:
                transport = TcpDataTransport(matched.group('host'), int(matched.group('port')))
            elif Path(port).is_char_device():
                transport = SerialDataTransport(port)
            else:
                raise TransportError(port, 'Port is invalid')
        except TransportError as err:
            if self.__event_bus:
                self.__event_bus.emit('failed_connect', address, port, err.args[1])
            return False

        return self.connect_meter(address, transport, **kwarg)

    def add_meter(self, meter: Meter) -> None:
        """ Add a meter to the collection """
        self.__meters.append(meter)

    @property
    def meters(self) -> list[Meter]:
        return self.__meters

    def find_by_serial_number(self, serial_number: int) -> Optional[Meter]:
        return next((meter for meter in self.__meters if meter.serial_number == serial_number), None)

    def find_by_package(self, package: bytes) -> Optional[Meter]:
        return next((meter for meter in self.__meters if meter.test_package(package)), None)


if __name__ == '__main__':
    pass
