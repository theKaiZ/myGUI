from myGUI.Rect import *
from time import time
import pygame.locals
from sys import platform


def add(obj, var, val):
    setattr(obj, var, getattr(obj, var) + val)


class myGUI():
    timestamp = 0
    FPS = 60
    running = True
    drawables = []
    clickables = []
    updateables = []
    keypressables = []  ####todo find a better name for that
    rand = 0.3
    keyboard = {}
    mouse = {}
    toggle_update = False
    pos = np.array([0, 0])
    size = np.array([1800, 900])
    mode = pygame.locals.DOUBLEBUF
    color = (255, 255, 255)
    myfonts = {}
    def __init__(self):
        pygame.init()
        pygame.display.set_mode(self.size, self.mode)
        self.myfont = pygame.font.SysFont("Comic Sans MS", 15 if 'win' in platform else 30)
        self.screen = pygame.display.get_surface()
        self.plots = []
        self.manual_init()
        self.setup_buttons()
        self.setup_plots()
        self.timer = time()

    def get_font(self, fontsize):
        if self.myfonts.get(fontsize) is None:
            self.myfonts[fontsize] = pygame.font.SysFont("Arial", size=fontsize)
        return self.myfonts[fontsize]

    def background(self):
        self.screen.fill(self.color)

    def manual_init(self):
        self.test1 = 1
        self.test2 = 100
        ### only for inheritance
        self.test3 = np.array([1, 2, 3])

    def click(self):
        for obj in self.clickables:
            obj.click()

    def draw(self):
        for obj in self.drawables:
            obj.draw()

    def update(self):
        self.toggle_update = False
        for obj in self.updateables:
            obj.update()

    def setup_plots(self):
        pass

    def setup_buttons(self):
        for i in range(5):
            Button(self, (100, 100 + 50 * i), (50, 50), "Test", command=lambda x=i: print(f"Hallo {x}"))
        Textfeld(self, (400, 100), (100, 100), "rand")
        Button(self, (400, 200), (50, 50), "+", command=lambda: add(self, "rand", 0.1))
        ScrollTextfeld(self, (500, 200), (50, 50), "test1", 1, limits=[1, 100], operator="+")
        ScrollTextfeld(self, (500, 250), (50, 50), "test2", 1.1, limits=[1, 100], operator="*")
        Button(self, (500, 500), (100, 100), "print", command=lambda: self.print(), hover_color=(1,255,30))

        ScrollTextfeld(self, (0, 0), (100, 100), "test3", change_value=1, limits=[1, 10], operator="+", index=0)
        Circle(self, (600,100), 30, filled=True, hover_color=(255,255,0))
        AnimatedCircle(self, (450,50), 40, filled=True, color=(255,0,0))
        #CircleButton(self, (600,150), 30, filled=True, command=lambda:print("true"))
    def run(self):
        while self.mainloop():
            pass
        self.exit_game()
        pygame.quit()

    def exit_game(self):
        pass

    @property
    def mouse_pos(self):
        ### todo find out if it is worth to store the information
        return pygame.mouse.get_pos()

    def keydown(self):
        for obj in self.keypressables:
            obj.keydown()

    def mainloop(self):
        if time() - self.timer > 1 / 10:
            self.timer = time()

        for event in pygame.event.get():
            self.event = event
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.keydown()
                if self.event.key == pygame.K_ESCAPE:
                    return False
                self.keyboard[event.key] = True
            elif event.type == pygame.KEYUP:
                self.keyboard[event.key] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse[event.button] = True
                self.click()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse[event.button] = False

        if time() - self.timestamp > 1 / self.FPS:
            self.timestamp = time()
            self.background()
            self.draw()
            self.update()
            if self.toggle_update:
                self.update()
            pygame.display.flip()
        return True

    def print(self):
        print("Drawables", self.drawables)
        print("Clickables", self.clickables)
        print("Updatteables", self.updateables)
        print("Keypressables", self.keypressables)


def main():
    myGUI().run()


if __name__ == '__main__':
    main()
