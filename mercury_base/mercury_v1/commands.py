# coding=utf8
from mercury_base import Meter
from mercury_base.utils import chunk_string, hex_str, to_datetime


def get_group_address(meter: Meter):
    data = meter.send_command(0x20)
    return hex_str(data)


def get_datetime(meter: Meter):
    data = meter.send_command(0x21)
    return to_datetime(data, '01%H%M%S%d%m%y', '%Y-%m-%d %H:%M:%S')


def get_power_limit(meter: Meter):
    data = meter.send_command(0x22)
    return int(hex_str(data)) / 100.


def get_month_energy_limit(meter: Meter):
    data = meter.send_command(0x23)
    return int(hex_str(data)) / 100.


def get_is_seasonal_time(meter: Meter):
    data = meter.send_command(0x24)
    return data != 0x0


def get_time_correction(meter: Meter):
    data = meter.send_command(0x25)
    return data[0]


def get_power(meter: Meter):
    data = meter.send_command(0x26)
    return int(hex_str(data)) / 100.


def get_energy_accumulators(meter: Meter):
    data = meter.send_command(0x27)
    return [
        int(hex_str(data[0:4])) / 100.,
        int(hex_str(data[4:8])) / 100.,
        int(hex_str(data[8:12])) / 100.,
        int(hex_str(data[12:16])) / 100.,
    ]


def get_firmware_info(meter: Meter):
    data = meter.send_command(0x28)
    return {
        'version': str(int(hex_str(data[0:2]))) + '.' + str(int(hex_str(data[0:2]))),
        'date': to_datetime(data[2:6], '%d%m%y', '%Y-%m-%d'),
    }


def get_battery_voltage(meter: Meter):
    data = meter.send_command(0x29)
    return int(hex_str(data)) / 100.


def get_display_filters(meter: Meter):
    data = meter.send_command(0x2A)
    return format(list(data)[0], '0>8b')


def get_last_stop_datetime(meter: Meter):
    data = meter.send_command(0x2B)
    return to_datetime(data, '01%H%M%S%d%m%y', '%Y-%m-%d %H:%M:%S')


def get_last_start_datetime(meter: Meter) -> str:
    data = meter.send_command(0x2C)
    return to_datetime(data, '01%H%M%S%d%m%y', '%Y-%m-%d %H:%M:%S')


def get_output_optocoupler_function(meter: Meter) -> int:
    data = meter.send_command(0x2D)
    return int(hex_str(data))


def get_tariffs_count(meter: Meter) -> int:
    data = meter.send_command(0x2E)
    return int(hex_str(data))


def get_serial_number(meter: Meter) -> int:
    data = meter.send_command(0x2F)
    serial_number = hex_str(data)
    return int(serial_number, 16)


def get_holidays(meter: Meter) -> list:
    holidays = []
    for part in [0, 1]:
        data = meter.send_command(0x30, part)
        for chunk in chunk_string(data, 2):
            chunk_data = hex_str(chunk)
            if chunk_data != 'FFFF':
                holidays.append(to_datetime(chunk, '%d%m', '%m-%d'))
    return holidays


def get_vcp(meter: Meter) -> dict:
    data = meter.send_command(0x63)
    return {
        'voltage': int(hex_str(data[0:2])) / 10.,
        'current': int(hex_str(data[2:4])) / 100.,
        'power': int(hex_str(data[4:7])) / 1000.,
    }


def get_tariff(meter: Meter) -> int:
    data = meter.send_command(0x60)
    return int(hex_str(data))


def set_display_filters(meter: Meter, params) -> bool:
    """
    TODO
    """
    return True
