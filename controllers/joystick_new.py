import joystick as jo

class Joystick:
    def __init__(self):
        pass

    def map_value(self, value):
        return int((value - 511) * 100 / 511)

    @property
    def x(self):
        x, _ = jo.get_xy()
        return self.map_value(x)

    @property
    def y(self):
        _, y = jo.get_xy()
        return self.map_value(y)

    @property
    def xy(self):
        x, y = jo.get_xy()
        return self.map_value(x), self.map_value(y)

    @property
    def up(self):
        return self.y > 10

    @property
    def down(self):
        return self.y < -10

    @property
    def left(self):
        return self.x < -10

    @property
    def right(self):
        return self.x > 10
    
    @property
    def buttonA(self):
        return jo.is_button_pressed(jo.BUTTON_A)
    
    @property
    def buttonB(self):
        return jo.is_button_pressed(jo.BUTTON_B)
    
    @property
    def buttonC(self):
        return jo.is_button_pressed(jo.BUTTON_C)
        
    @property
    def buttonD(self):
        return jo.is_button_pressed(jo.BUTTON_D)


joystick = Joystick()