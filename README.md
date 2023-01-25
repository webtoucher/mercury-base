# Набор инструментов для взаимодействия со счётчиками Инкотекс Меркурий

![License](https://img.shields.io/badge/License-BSD%203--Clause-green)
[![Downloads](https://img.shields.io/pypi/dm/mercury-base.svg?color=orange)](https://pypi.python.org/pypi/mercury-base)
[![Latest Version](https://img.shields.io/pypi/v/mercury-base.svg)](https://pypi.python.org/pypi/mercury-base)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/mercury-base.svg)](https://pypi.python.org/pypi/mercury-base)

Этот набор инструментов предназначен для управления счётчиками марки [Инкотекс](https://www.incotexcom.ru/)
Меркурий, подключенных к серверу через последовательную шину (RS485/CAN).

## Установка

Установите при помощи pip:

```shell
$ pip install mercury-base
```

Либо добавьте в файл requirements.txt вашего проекта на python в качестве зависимости:

```
mercury-base~=1.0a1
```

## Использование

Вот пример вывода на экран текущей мощности в нагрузке для счётчика Меркурий 206
с сетевым адресом 12345678 (по умолчанию совпадает с серийным номером счётчика),
подключенного к последовательному порту /dev/ttyACM0:

```python
from mercury_base import Meter, TYPE_206

if __name__ == '__main__':
    meter = Meter(TYPE_206, 12345678, '/dev/ttyACM0')
    current_power = meter.command('get_power')
    print('Текущая мощность в нагрузке - %s кВт' % current_power)
```

## Команды

Со списком доступных команд можно ознакомиться в документации соответствующего протокола:

- [Mercury V1](mercury_base/mercury_v1/README.md) (для однофазных счётчиков Меркурий 200, 201, 203 и 206)