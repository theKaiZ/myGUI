import pygame
from myGUI.Rect import ScrollTextfeld, Rect
from myGUI.Slide import Presenter, Slide
import numpy as np
from time import time
from PIL import Image
from numba import njit, prange


def generate_ruleset(number):
    binstring = ""
    n = number
    while len(binstring) < 8:
        binstring = str(number % 2) + binstring
        number //= 2
    print(n, binstring)
    binarray = np.zeros(8, dtype=int)
    for i in range(8):
        binarray[i] = int(binstring[i])
    return binarray




@njit(cache=True)
def next_generation(cells, rulset, gen):
    nx = cells.shape[0]
    old_cell = cells[:, gen - 1]
    for i in range(nx):
        # triple = f"{cells[i-1,old]}{cells[i,old]}{cells[(i+1)%nx,old]}"
        triple = 4 * old_cell[i - 1] + 2 * old_cell[i] + old_cell[(i + 1) % nx]
        cells[i, gen] = rulset[triple]


class ca_image(Rect):
    _surface = None
    def __init__(self, parent, cells, size, **kwargs):
        pos = (0, 0)
        self.s = size
        # size = parent.size
        super().__init__(parent=parent, pos=pos)
        self.cells = cells

    @property
    def surface(self):
        if self._surface is not None:
            return self._surface
        t = time()
        surf = pygame.Surface(self.cells.shape)
        nx, ny = self.cells.shape
        for x in range(nx):
            for y in range(ny):
                surf.set_at((x, y), (0, 0, 0) if self.cells[x, y] else (255, 255, 255))
        #self._surface = pygame.transform.smoothscale(surf, tuple(self.size))
        if self.s >1:
            surf = pygame.transform.scale(surf, tuple(self.size))
        self._surface = surf
        print(f"{time() - t:.2f}, {self.cells.shape}")
        return self._surface

    def draw(self):
        self.screen.blit(self.surface, (self.pos[0], self.pos[1], self.size[0], self.size[1]))


class CA_Slide(Slide):
    def manual_init(self):
        #t = time()
        self.nx = self.size[0] // self.s
        self.ny = self.size[1] // self.s
        self.cells = np.zeros((self.nx, self.ny), dtype=int)
        self.gen = self.ny

        for i in range(1, self.num_p + 1):
            self.cells[self.nx // (self.num_p + 1) * i, 0] = 1
        self.ruleset = generate_ruleset(self.parent.rule)
        for i in range(1, self.ny):
            next_generation(self.cells, self.ruleset, i)

        # self.plot_gen()
        ca_image(self, self.cells, self.s)
        #print(time() - t)
        self.toggle_update = True

    @property
    def s(self):
        return self.parent.box_size

    @property
    def num_p(self):
        return self.parent.num_p

    def update(self):
        if self.gen < self.ny:
            self.gen += 1
            self.parent.toggle_update = True


class CA_Presenter(Presenter):
    _rule = 198
    size = np.array([1200, 800])
    _box_size = 5
    _num_p = 1

    def manual_init(self):
        self.slides = [lambda: CA_Slide(self, pos=(0,0), size=self.size-[0,80])]

    def setup_buttons(self):
        super().setup_buttons()
        ScrollTextfeld(self, self.size - (200, 50), (100, 50), "rule", 1, [0, 255])
        ScrollTextfeld(self, self.size - (300, 50), (100, 50), "box_size", 1, [1, 20])
        ScrollTextfeld(self, self.size - (400, 50), (100, 50), "num_p", 1, [1, 30])

    @property
    def box_size(self):
        return self._box_size

    @box_size.setter
    def box_size(self, value):
        self._box_size = value
        self.next

    @property
    def num_p(self):
        return self._num_p

    @num_p.setter
    def num_p(self, value):
        self._num_p = value
        self.next

    def keydown(self):
        if self.event.key == pygame.K_UP:
            self.rule += 1
        if self.event.key == pygame.K_DOWN:
            self.rule -= 1
        self.toggle_update = True

    def update(self):
        super().update()

    @property
    def rule(self):
        return self._rule

    @rule.setter
    def rule(self, value):
        if value < 0 or value > 255:
            return
        self._rule = value
        self.next


if __name__ == '__main__':
    CA_Presenter().run()
