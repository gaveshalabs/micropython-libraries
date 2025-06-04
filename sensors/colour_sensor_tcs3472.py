# colour_sensor.py
# A MicroPython library for the TCS3472 light sensing chip
#
# https://github.com/gaveshalabs/micropython-libraries
# Copyright (c) 2024 Gavesha Labs
# Licensed under the MIT License

import struct
from machine import SoftI2C, Pin;
import time

class ColourSensor:
    def __init__(self, scl, sda, address=0x29):
        self._bus = SoftI2C(scl=Pin(scl), sda=Pin(sda))
        self._i2c_address = address
        self._last_read_time = 0

        self._bus.start()
        self._bus.writeto(self._i2c_address, b'\x80\x03')
        self._bus.writeto(self._i2c_address, b'\x81\x2b')
    
    @property
    def rgb(self):
        time_now = time.ticks_ms()
        if time.ticks_diff(time_now, self._last_read_time) > 10:
            self._rgb = tuple(int(x * 255) for x in self.scaled())
            self._last_read_time = time_now
        return self._rgb

    @property
    def red(self):
        return self.rgb[0]
    
    @property
    def green(self):
        return self.rgb[1]
    
    @property
    def blue(self):
        return self.rgb[2]

    def scaled(self):
        crgb = self.raw()
        if crgb[0] > 0:
            return tuple(float(x) / crgb[0] for x in crgb[1:])

        return (0,0,0)

    def light(self):
        return self.raw()[0]
    
    def brightness(self, level=65.535):
        return int((self.light() / level))

    def valid(self):
        self._bus.writeto(self._i2c_address, b'\x93')
        return self._bus.readfrom(self._i2c_address, 1)[0] & 1

    def raw(self):
        self._bus.writeto(self._i2c_address, b'\xb4')
        return struct.unpack("<HHHH", self._bus.readfrom(self._i2c_address, 8))