# coding=utf8
from mercury_base.utils import chunk_string, hex_str, to_datetime
from typing import Optional


def get_serial_number(meter) -> Optional[int]:
    data = meter.send_command(0x2F)
    serial_number = hex_str(data)
    return int(serial_number, 16)


def get_info(meter) -> dict:
    model = None
    features = []
    data = meter.send_command(0x86, 255)
    if data[1] == 2:
        model = '200'
    elif data[1] == 4:
        model = '203.2T'
        if data[2] == 1:
            features.append('relay')
        elif data[2] == 3:
            features.append('100(L)')
    elif data[1] == 6:
        model = '203.2TR'
        if data[2] == 1:
            features.append('relay')
        elif data[2] == 3:
            features.append('100(L)')
    elif data[1] == 8:
        model = '206'
        if data[2] in [1, 2, 4]:
            features.append('RS485')
        if data[2] in [3, 5]:
            features.append('PLC')
        if data[2] in [2, 3, 4, 5]:
            features.append('relay')
            if data[2] in [4, 5]:
                features.append('auto power on')
    elif data[1] == 10:
        model = '201.8TLO'
        if data[2] == 3:
            features.append('relay')
    return {
        'model': model,
        'features': features,
    }


def get_group_address(meter):
    data = meter.send_command(0x20)
    return hex_str(data)


def get_datetime(meter):
    data = meter.send_command(0x21)
    return to_datetime(data[2:], '%H%M%S%d%m%y', '%Y-%m-%d %H:%M:%S')


def get_power_limit(meter):
    data = meter.send_command(0x22)
    return int(hex_str(data)) / 100.


def get_month_energy_limit(meter):
    data = meter.send_command(0x23)
    return int(hex_str(data)) / 100.


def get_is_seasonal_time(meter):
    data = meter.send_command(0x24)
    return data[0] != 0


def get_time_correction(meter):
    data = meter.send_command(0x25)
    return data[0]


def get_load_power(meter):
    data = meter.send_command(0x26)
    return int(hex_str(data)) / 100.


def get_energy_accumulators(meter):
    data = meter.send_command(0x27)
    return [
        int(hex_str(data[0:4])) / 100.,
        int(hex_str(data[4:8])) / 100.,
        int(hex_str(data[8:12])) / 100.,
        int(hex_str(data[12:16])) / 100.,
    ]


def get_firmware_info(meter):
    data = meter.send_command(0x28)
    return {
        'version': str(int(hex_str(data[0:1]))) + '.' + str(int(hex_str(data[1:2]))),
        'date': to_datetime(data[3:6], '%d%m%y', '%Y-%m-%d'),
    }


def get_battery_voltage(meter):
    data = meter.send_command(0x29)
    return int(hex_str(data)) / 100.


def get_display_filters(meter):
    data = meter.send_command(0x2A)
    return format(list(data)[0], '0>8b')


def get_last_stop_datetime(meter):
    data = meter.send_command(0x2B)
    return to_datetime(data[1:], '%H%M%S%d%m%y', '%Y-%m-%d %H:%M:%S')


def get_last_start_datetime(meter) -> str:
    data = meter.send_command(0x2C)
    return to_datetime(data[1:], '%H%M%S%d%m%y', '%Y-%m-%d %H:%M:%S')


def get_output_optocoupler_function(meter) -> int:
    data = meter.send_command(0x2D)
    return int(hex_str(data))


def get_tariffs_count(meter) -> int:
    data = meter.send_command(0x2E)
    return data[0]


def get_holidays(meter) -> list:
    holidays = []
    for part in [0, 1]:
        data = meter.send_command(0x30, part)
        for chunk in chunk_string(data, 2):
            chunk_data = hex_str(chunk)
            if chunk_data != 'FFFF':
                holidays.append(to_datetime(chunk, '%d%m', '%m-%d'))
    return holidays


def get_vcp(meter) -> dict:
    data = meter.send_command(0x63)
    return {
        'voltage': int(hex_str(data[0:2])) / 10.,
        'current': int(hex_str(data[2:4])) / 100.,
        'power': int(hex_str(data[4:7])) / 1000.,
    }


def get_tariff(meter) -> int:
    data = meter.send_command(0x60)
    return data[0]


def get_is_relay_on(meter) -> bool:
    data = meter.send_command(0x86, 1)
    return hex_str(data[1:]) == '55'


def get_full_power_and_cos_fi(meter) -> dict:
    data = meter.send_command(0x86, 2)
    cos_fi_bytes = hex_str(data[1:3])
    cos_fi = int(cos_fi_bytes[1:]) / 1000.
    if cos_fi_bytes[:1] != '0':
        cos_fi *= -1
    return {
        'cos_fi': cos_fi,
        'full_power': int(hex_str(data[3:6])) / 1000.,
    }
