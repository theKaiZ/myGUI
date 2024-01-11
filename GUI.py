from Rect import *
from time import time
import pygame.locals


def add(obj, var, val):
    setattr(obj, var, getattr(obj, var) + val)


class myGUI():
    timestamp = 0
    pos = None
    running = True
    drawables = []
    clickables = []
    updateables = []
    rand = 0.3
    keyboard = {}

    def __init__(self):
        pygame.init()
        window = pygame.display.set_mode((960, 720), pygame.locals.DOUBLEBUF)
        self.myfont = pygame.font.SysFont("Comic Sans MS", 15 if 'win' in platform else 15)
        self.screen = pygame.display.get_surface()
        self.plots = []
        self.setup_buttons()
        self.setup_plots()
        self.manual_init()
        self.timer = time()

    def manual_init(self):
        ### only for inheritance
        pass

    def click(self):
        print(self.event)
        for obj in self.clickables:
            obj.click()

    def draw(self):
        for obj in self.drawables:
            obj.draw()

    def update(self):
        for obj in self.updateables:
            obj.update()

    def setup_plots(self):
        pass

    def setup_buttons(self):
        for i in range(5):
            Button(self, (100, 100 + 50 * i), (50, 50), "Test", command=lambda x=i: print(f"Hallo {x}"))
        Textfeld(self, (400, 100), (100, 100), "rand")
        Button(self, (400, 200), (50, 50), "+", command=lambda: add(self, "rand", 0.1))

    def run(self):
        while self.mainloop():
            pass
        pygame.quit()

    @property
    def mouse_pos(self):
        ### todo find out if it is worth to store the information
        return pygame.mouse.get_pos()

    def mainloop(self):
        if time() - self.timer > 1 / 10:
            self.timer = time()

        for event in pygame.event.get():
            self.event = event
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                self.keyboard[event.key] = True

            elif event.type == pygame.KEYUP:
                self.keyboard[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.click()
            elif event.type == pygame.MOUSEBUTTONUP:
                pass

        if time() - self.timestamp > 0.2:
            self.screen.fill((0, 0, 0))
            self.draw()
            self.update()
            pygame.display.flip()
        return True


def main():
    myGUI().run()


if __name__ == '__main__':
    main()
