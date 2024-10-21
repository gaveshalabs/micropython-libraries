from machine import Pin, PWM

class Servo:
    # these defaults work for the standard TowerPro SG90
    __servo_pwm_freq = 50
    __min_u10_duty = 20		# should be offsetted to fit the servo
    __max_u10_duty = 130	# should be offsetted to fit the servo
    min_angle = 0
    max_angle = 180
    current_angle = 0.001


    def __init__(self, pin):
        self.__pin = pin
        self.__initialise(pin)


    def update_settings(self, servo_pwm_freq=50, min_duty=20, max_duty=130, min_angle=0, max_angle=180, pin=-1):
        self.__servo_pwm_freq = servo_pwm_freq
        self.__min_u10_duty = min_duty
        self.__max_u10_duty = max_duty
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.__initialise(pin if pin > -1 else self.__pin)


    def move(self, angle):
        # round to 2 decimal places, so we have a chance of reducing unwanted servo adjustments
        angle = round(angle, 2)
        # do we need to move?
        if angle == self.current_angle:
            return
        self.current_angle = angle
        # calculate the new duty cycle and move the motor
        duty_u10 = self.__angle_to_u10_duty(angle)
        self.__motor.duty(duty_u10)

    def __angle_to_u10_duty(self, angle):
        return int((angle - self.min_angle) * self.__angle_conversion_factor) + self.__min_u10_duty


    def __initialise(self, pin):
        self.current_angle = -0.001
        self.__angle_conversion_factor = (self.__max_u10_duty - self.__min_u10_duty) / (self.max_angle - self.min_angle)
        self.__motor = PWM(Pin(pin))
        self.__motor.freq(self.__servo_pwm_freq)
    