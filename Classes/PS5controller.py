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
        # DO NOT call pygame.event.* here

        lx = self.joy.get_axis(0)
        ly = self.joy.get_axis(1)
        rx = self.joy.get_axis(2)
        ry = self.joy.get_axis(3)
        lt = self.joy.get_axis(4)
        rt = self.joy.get_axis(5)


        cross = self.joy.get_button(0)
        circle = self.joy.get_button(1)
        square = self.joy.get_button(2)
        triangle = self.joy.get_button(3)
        l1 = None
        r1 = self.joy.get_button(10)

        # USE THIS FOR LOOP TO FIND BUTTON NUMBER
        # for i in range(self.joy.get_numbuttons()):
        #     if self.joy.get_button(i):
        #         print(f"Button {i} pressed")

        return lx, ly, lt, l1, rx, ry, rt, r1, cross, circle, square, triangle

    
