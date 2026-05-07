import pygame

class PS5Controller:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No controller detected")

        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()

        print(f"Controller connected: {self.joy.get_name()}")

    def read(self):
        pygame.event.pump()  # IMPORTANT

        # Axes values are in [-1.0, +1.0]
        lx = self.joy.get_axis(0)   # Left stick X
        ly = self.joy.get_axis(1)   # Left stick Y
        lt = self.joy.get_axis(4)   # Left trigger
        rx = self.joy.get_axis(2)   # Right stick X
        ry = self.joy.get_axis(3)   # Right stick Y
        rt = self.joy.get_axis(5)   # Right trigger
        square = self.joy.get_button(2) # Square button

        return lx, ly, lt, rx, ry, rt, square
    
