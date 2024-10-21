'''
bmp180 is a micropython module for the Bosch BMP180 sensor. It measures
temperature as well as pressure, with a high enough resolution to calculate
altitude.
Breakoutboard: http://www.adafruit.com/products/1603  
data-sheet: http://ae-bst.resource.bosch.com/media/products/dokumente/
bmp180/BST-BMP180-DS000-09.pdf

The MIT License (MIT)
Copyright (c) 2014 Sebastian Plamauer, oeplse@gmail.com
Copyright (c) 2022 Lihini Senanayake for Gavesha Labs
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from ustruct import unpack as unp
from machine import I2C, Pin
import math
import time

delays = (5, 8, 14, 25)

def init_bmp180(scl_pin, sda_pin, freq=100000):
    i2c = I2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)
    return BMP180(i2c)

# BMP180 class
class BMP180():
    '''
    Module for the BMP180 pressure sensor.
    '''

    _bmp_addr = 119             # adress of BMP180 is hardcoded on the sensor

    # init
    def __init__(self, i2c_bus, fail_silently=True):

        # create i2c obect
        _bmp_addr = self._bmp_addr
        self._bmp_i2c = i2c_bus
        
        if self.is_ready():
            self.chip_id = self._bmp_i2c.readfrom_mem(_bmp_addr, 0xD0, 2)
            # read calibration data from EEPROM
            self._AC1 = unp('>h', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xAA, 2))[0]
            self._AC2 = unp('>h', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xAC, 2))[0]
            self._AC3 = unp('>h', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xAE, 2))[0]
            self._AC4 = unp('>H', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xB0, 2))[0]
            self._AC5 = unp('>H', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xB2, 2))[0]
            self._AC6 = unp('>H', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xB4, 2))[0]
            self._B1 = unp('>h', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xB6, 2))[0]
            self._B2 = unp('>h', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xB8, 2))[0]
            self._MB = unp('>h', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xBA, 2))[0]
            self._MC = unp('>h', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xBC, 2))[0]
            self._MD = unp('>h', self._bmp_i2c.readfrom_mem(_bmp_addr, 0xBE, 2))[0]

            # settings to be adjusted by user
            self.oversample_setting = 3
            self.baseline = 101325.0

            # output raw
            self.UT_raw = None
            self.B5_raw = None
            self.MSB_raw = None
            self.LSB_raw = None
            self.XLSB_raw = None
        elif fail_silently:
            print("Error: BMP180 sensor is not available")
        else:
            raise RuntimeError("BMP180 sensor is not available")

    def is_ready(self):
        try:
            self._bmp_i2c.readfrom(self._bmp_addr, 1)
            return True
        except ValueError:
            return False

    def compvaldump(self):
        '''
        Returns a list of all compensation values
        '''
        return [self._AC1, self._AC2, self._AC3, self._AC4, self._AC5, self._AC6, 
                self._B1, self._B2, self._MB, self._MC, self._MD, self.oversample_setting]


    @property
    def oversample_sett(self):
        return self.oversample_setting

    @oversample_sett.setter
    def oversample_sett(self, value):
        if value in range(4):
            self.oversample_setting = value
        else:
            print('oversample_sett can only be 0, 1, 2 or 3, using 3 instead')
            self.oversample_setting = 3

    @property
    def temperature(self):
        '''
        Temperature in degree C.
        '''
        self._read_raw_temp()
        try:
            MSB = unp('B', self.UT_MSB_raw)[0]
            LSB = unp('B', self.UT_LSB_raw)[0]
            UT = (MSB << 8)+LSB
        except:
            return None
        X1 = (UT-self._AC6)*self._AC5/2**15
        X2 = self._MC*2**11/(X1+self._MD)
        self.B5_raw = X1+X2
        return (((X1+X2)+8)/2**4)/10

    @property
    def pressure(self):
        '''
        Pressure in mbar.
        '''
        if not self.temperature:  # Populate self.B5_raw
            return None
        self._read_raw_pressure()
        try:
            MSB = unp('B', self.MSB_raw)[0]
            LSB = unp('B', self.LSB_raw)[0]
            XLSB = unp('B', self.XLSB_raw)[0]
        except:
            return None
        UP = ((MSB << 16)+(LSB << 8)+XLSB) >> (8-self.oversample_setting)
        B6 = self.B5_raw-4000
        X1 = (self._B2*(B6**2/2**12))/2**11
        X2 = self._AC2*B6/2**11
        X3 = X1+X2
        B3 = ((int((self._AC1*4+X3)) << self.oversample_setting)+2)/4
        X1 = self._AC3*B6/2**13
        X2 = (self._B1*(B6**2/2**12))/2**16
        X3 = ((X1+X2)+2)/2**2
        B4 = abs(self._AC4)*(X3+32768)/2**15
        B7 = (abs(UP)-B3) * (50000 >> self.oversample_setting)
        if B7 < 0x80000000:
            pressure = (B7*2)/B4
        else:
            pressure = (B7/B4)*2
        X1 = (pressure/2**8)**2
        X1 = (X1*3038)/2**16
        X2 = (-7357*pressure)/2**16
        return pressure+(X1+X2+3791)/2**4

    @property
    def altitude(self):
        '''
        Altitude in m.
        '''
        try:
            p = 44330 * (1 - pow(self.pressure/self.baseline, 1/5.255))
        except:
            p = 0.0
        return p
    
    def _read_raw_temp(self):
        self._bmp_i2c.writeto_mem(self._bmp_addr, 0xF4, bytearray([0x2E]))
        time.sleep_ms(5)
        
        try:
            self.UT_MSB_raw = self._bmp_i2c.readfrom_mem(self._bmp_addr, 0xF6, 1)
            self.UT_LSB_raw = self._bmp_i2c.readfrom_mem(self._bmp_addr, 0xF7, 1)
            return True
        except Exception as e:
            return None
        
    def _read_raw_pressure(self):
        self._bmp_i2c.writeto_mem(self._bmp_addr, 0xF4, bytearray([0x34+(self.oversample_setting << 6)]))
        t_pressure_ready = delays[self.oversample_setting]
        t_start = time.ticks_ms()
        while (time.ticks_ms() - t_start) <= t_pressure_ready:
            time.sleep_ms(1)
            
        try:
            self.MSB_raw = self._bmp_i2c.readfrom_mem(self._bmp_addr, 0xF6, 1)
            self.LSB_raw = self._bmp_i2c.readfrom_mem(self._bmp_addr, 0xF7, 1)
            self.XLSB_raw = self._bmp_i2c.readfrom_mem(self._bmp_addr, 0xF8, 1)
            return True
        except Exception as e:
            return None
