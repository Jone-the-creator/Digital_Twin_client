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
        rx = self.joy.get_axis(2)   # Right stick X
        ry = self.joy.get_axis(3)   # Right stick Y

        return lx, ly, rx, ry
    
