# coding=utf8
from mercury_base.utils import hex_str
from typing import Optional


def get_serial_number(meter) -> Optional[int]:
    data = meter.send_command(0x08, 0x0)
    serial_number = hex_str(data[:4])
    return int(serial_number, 16)


def get_info(meter) -> dict:
    model = 'unknown'
    features = []
    data = meter.send_command(0x08, 0x12, 0)
    """ TODO: parse answer """
    return {
        'model': model,
        'features': features,
    }
