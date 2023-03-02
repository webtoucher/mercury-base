# coding=utf8
from mercury_base.utils import dec_str, to_datetime


def get_serial_number_and_date_of_manufacture(meter) -> dict:
    data = meter.send_command(0x08, 0x00)
    return {
        'serial_number': int(dec_str(data[:4])),
        'date_of_manufacture': to_datetime(dec_str(data[4:7]), '%d%m%y', '%Y-%m-%d'),
    }


def get_passport(meter) -> dict:
    data = meter.send_command(0x08, 0x0100)
    result = {
        'serial_number': int(dec_str(data[:4])),
        'date_of_manufacture': to_datetime(dec_str(data[4:7]), '%d%m%y', '%Y-%m-%d'),
        'firmware_version': '.'.join('%d' % b for b in data[7:10]),
        'meter_version': '.'.join('%d' % b for b in data[18:20]),
    }
    result.update(_parse_version(data[10:16]))
    return result


def _parse_version(data) -> dict:
    return {}


def get_transformation_ratios(meter) -> dict:
    data = meter.send_command(0x08, 0x02)
    return {
        'voltage': int(dec_str(data[:2])),
        'current': int(dec_str(data[2:4])),
    }


def get_firmware_version(meter) -> str:
    data = meter.send_command(0x08, 0x03)
    return '.'.join('%d' % b for b in data)


def get_additional_timeout_multiplier(meter) -> int:
    data = meter.send_command(0x08, 0x04)
    return int(dec_str(data))


def get_main_timeout_multiplier(meter) -> int:
    data = meter.send_command(0x08, 0x1D)
    return int(dec_str(data))


def get_info(meter) -> dict:
    model = 'unknown'
    features = []
    data = meter.send_command(0x08, 0x12, 0)
    """ TODO: parse answer """
    return {
        'model': model,
        'features': features,
    }
