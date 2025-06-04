from machine import PWM, Pin
import time

try:
    import board
    __GBOARD = board.GBOARD__
except:
    __GBOARD = None

class RobomaticsGearMotor:

    rotating_clockwise = False
    pinmap = [23,22,21,19,18,5 ,17,16,4 ,15,13,39,36,34,35,32,33,25,26,27]

    def __init__(self, pin1, pin2):
        self.pins = [pin1, pin2]

        if isinstance(pin1, Pin):
            pin1obj = pin1
        elif __GBOARD == 'ROBO-KIT':
            pin1obj = Pin(self.pinmap[pin1])
        else:
            pin1obj = Pin(pin1)
        self.in1 = PWM(pin1obj, freq=50, duty=1023)

        if isinstance(pin2, Pin):
            pin2obj = pin2
        elif __GBOARD == 'ROBO-KIT':
            pin2obj = Pin(self.pinmap[pin2])
        else:
            pin2obj = Pin(pin2)
        self.in2 = PWM(pin2obj, freq=50, duty=1023)
        
        self._fine_motor_control = True
        self._mirror = False

    def lock(self):
        self.in1.duty(1023)
        self.in2.duty(1023)

    def neutral(self):
        self.in1.duty(0)
        self.in2.duty(0)

    @property
    def fine_motor_control(self):
        return self._fine_motor_control
    
    @fine_motor_control.setter
    def fine_motor_control(self, value):
        self._fine_motor_control = bool(value)
    
    @property
    def mirror(self):
        return self._mirror
    
    @mirror.setter
    def mirror(self, value):
        self._mirror = bool(value)

    @property
    def speed(self):
        if self.in2.duty() > 0:
            if not self.mirror:
                return self.in2.duty()/10
            else:
                return (-self.in2.duty())/10
        elif self.in1.duty() > 0:
            if not self.mirror:
                return (-self.in1.duty())/10
            else:
                return self.in1.duty()/10
        else:
            return 0
    

    @speed.setter
    def speed(self, new_speed):
        new_speed = max(int(new_speed), -100)  
        new_speed = min(new_speed, 100)
        if self.fine_motor_control:
            #Rotating_clockwise
            if new_speed > 0:
                if not self._mirror:
                    if new_speed < -10:
                        for i in range(new_speed, -10, +int(new_speed/10)):
                            self.in1.duty(i)
                            time.sleep_ms(1)
                    self.in1.duty(0)
                    self.in2.duty(new_speed * 10)
                else:
                    if new_speed < -10:
                        for i in range(new_speed, -10, +int(new_speed/10)):
                            self.in2.duty(i)
                            time.sleep_ms(1)
                    self.in2.duty(0)
                    self.in1.duty(new_speed * 10)

            #neutral
            elif new_speed == 0:
                self.in1.duty(1023)
                self.in2.duty(1023)

            #Rotating_counterclockwise 
            else:
                if not self._mirror:
                    if new_speed > 10:
                        for i in range(new_speed, 10, -int(new_speed/10)):
                            self.in2.duty(i)
                            time.sleep_ms(1)
                    self.in2.duty(0)
                    self.in1.duty((-new_speed) * 10)
                else:
                    if new_speed > 10:
                        for i in range(new_speed, 10, -int(new_speed/10)):
                            self.in1.duty(i)
                            time.sleep_ms(1)
                    self.in1.duty(0)
                    self.in2.duty((-new_speed) * 10)

        else:
            #Rotating_clockwise 
            if new_speed > 0:
                if not self._mirror:
                    if new_speed < -10:
                        for i in range(new_speed, -10, +int(new_speed/10)):
                            self.in1.duty(i)
                            time.sleep_ms(1)
                    self.in1.duty(0)
                    self.in2.duty(new_speed * 10)
                else:
                    if new_speed < -10:
                        for i in range(new_speed, -10, +int(new_speed/10)):
                            self.in2.duty(i)
                            time.sleep_ms(1)
                    self.in2.duty(0)
                    self.in1.duty(new_speed * 10)

            #neutral
            elif new_speed == 0:
                self.in1.duty(0)
                self.in2.duty(0)

            #Rotating_counterclockwise
            else:
                if not self._mirror:
                    if new_speed > 10:
                        for i in range(new_speed, 10, -int(new_speed/10)):
                            self.in2.duty(i)
                            time.sleep_ms(1)
                    self.in2.duty(0)
                    self.in1.duty((-new_speed )* 10)
                else:
                    if new_speed > 10:
                        for i in range(new_speed, 10, -int(new_speed/10)):
                            self.in1.duty(i)
                            time.sleep_ms(1)
                    self.in1.duty(0)
                    self.in2.duty((-new_speed) * 10)

    def __str__(self):
        return "RobomaticsGearMotor(pins = {self.pins}, speed = {self.speed}, mirror = {self.mirror})"
    