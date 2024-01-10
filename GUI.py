from Rect import *
from time import time
import pygame.locals
class myGUI():
    timestamp = 0
    pos = None
    running = True
    left_click = right_click = False
    update = True
    drawables = []

    def __init__(self):
        pygame.init()
        window = pygame.display.set_mode((960, 720), pygame.locals.DOUBLEBUF)
        self.myfont = pygame.font.SysFont("Comic Sans MS", 15 if 'win' in platform else 15)
        self.screen = pygame.display.get_surface()
        self.buttons = []
        self.plots = []
        self.setup_buttons()
        self.setup_plots()
        self.manual_init()
        self.timer = time()

    def manual_init(self):
        ### only for inheritance
        pass

    def click(self):
        for button in self.buttons:
            button.click()

    def draw(self):
        for obj in self.drawables:
            obj.draw()

    def setup_plots(self):
        pass

    def setup_buttons(self):
        self.buttons = []
        for i in range(5):
            self.buttons.append(
                Button(self, (100, 100 + 50 * i), (50, 50), "Test", command=lambda x=i: print(f"Hallo {x}")))
        # self.buttons.append(RectImageSeries(self, (200, 200), [f"state{i}.png" for i in range(9)]))

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
            self.update = True
            self.timer = time()

        for event in pygame.event.get():
            self.event = event
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.click()
            elif event.type == pygame.MOUSEBUTTONUP:
                pass

        if self.update and time() - self.timestamp > 0.2:
            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()
            self.update = False
        return True

