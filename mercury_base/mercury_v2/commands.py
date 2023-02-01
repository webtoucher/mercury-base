# coding=utf8
from mercury_base.utils import hex_str
from typing import Optional


def get_serial_number(meter) -> Optional[int]:
    data = meter.send_command(0x00)
    serial_number = hex_str(data[:4])
    return int(serial_number, 16)


def get_info(meter) -> dict:
    model = 'unknown'
    features = []
    return {
        'model': model,
        'features': features,
    }
