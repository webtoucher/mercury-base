# coding=utf8
from mercury_base import Meter
from mercury_base.utils import chunk_string, hex_str, to_datetime


def get_serial_number(meter: Meter) -> int:
    data = meter.send_command(0x00)
    serial_number = hex_str(data[:4])
    return int(serial_number, 16)


def get_info(meter: Meter) -> dict:
    model = 'unknown'
    features = []
    return {
        'model': model,
        'features': features,
    }
