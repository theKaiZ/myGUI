from myGUI.Slide import Slide, Presenter
from myGUI.Rect import Button, Rectangular_object, ScrollTextfeld, Plot_object
import numpy as np
import pygame
from numba import njit, prange


class golpanel(Rectangular_object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dx = self.size[0] // self.cells.shape[0]
        self.dy = self.size[1] // self.cells.shape[1]
        self.xmax = self.cells.shape[0] * self.dx
        self.ymax = self.cells.shape[1] * self.dy
        self.grid = False

    @property
    def cells(self):
        return self.parent.cells

    def draw_grid(self):
        for x in range(self.cells.shape[0] + 1):
            for y in range(self.cells.shape[1] + 1):
                pygame.draw.line(self.screen, (255, 255, 255), self.pos + (x * self.dx, 0),
                                 self.pos + (x * self.dx, self.ymax))
                pygame.draw.line(self.screen, (255, 255, 255), self.pos + (0, y * self.dy),
                                 self.pos + (self.xmax, y * self.dy))

    def draw_rect(self):
        pygame.draw.line(self.screen, (255, 255, 255), self.pos, self.pos + (self.xmax, 0))
        pygame.draw.line(self.screen, (255, 255, 255), self.pos, self.pos + (0, self.ymax))
        pygame.draw.line(self.screen, (255, 255, 255), self.pos + (0, self.ymax), self.pos + (self.xmax, self.ymax))
        pygame.draw.line(self.screen, (255, 255, 255), self.pos + (self.xmax, 0), self.pos + (self.xmax, self.ymax))

    def draw_cells(self):
        for x in range(self.cells.shape[0]):
            for y in range(self.cells.shape[1]):
                if self.cells[x, y]:
                    pygame.draw.rect(self.screen, (255, 255, 255),
                                     (self.pos[0] + x * self.dx, self.pos[1] + y * self.dy, self.dx, self.dy))

    def draw(self):
        if self.grid:
            self.draw_grid()
        else:
            self.draw_rect()
        self.draw_cells()


@njit(cache=True, parallel=True)
def next_generation(cells, newgen):
    xmax = cells.shape[0]
    ymax = cells.shape[1]
    for x in prange(xmax):
        for y in prange(ymax):
            dasum = cells[x - 1, y - 1] + cells[x - 1, y] + cells[x - 1, (y + 1) % ymax] + \
                    cells[x, y - 1] + cells[x, (y + 1) % ymax] + \
                    cells[(x + 1) % xmax, y - 1] + cells[(x + 1) % xmax, y] + cells[(x + 1) % xmax, (y + 1) % ymax]
            if cells[x, y]:
                if dasum < 2 or dasum > 3:
                    newgen[x, y] = 0
                else:
                    newgen[x, y] = 1
            elif dasum == 3:
                newgen[x, y] = 1


class GoLSlide(Slide):
    _buffer = None
    draw_grid = False

    def manual_init(self):
        s = self.parent.dim
        self.differenzen = []

        Button(self, (10, 10), (80, 30), "random", command=lambda: self.fill_random())
        self.plot = Plot_object(self, (650, 50), (400, 400))
        ax = self.plot.ax
        self.line = ax.plot(range(1))[0]
        self.line2 = ax.plot(range(1), color="black", linestyle="dotted")[0]
        self.cells = np.zeros((s, s), dtype=int)
        golpanel(parent=self, pos=(10, 50), size=(600, 600))
        self.fill_random()
        self.parent.toggle_update = True

    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = np.zeros(self.cells.shape, dtype=int)
        return self._buffer

    def fill_random(self):
        np.random.seed(self.parent.seed)
        self.cells = (np.random.random(self.cells.shape) * 1.2).astype(int)

    def update(self):
        next_generation(self.cells, self.buffer)
        differenz = (self.cells | self.buffer) - (self.cells & self.buffer)
        self.differenzen.append(differenz.sum() / self.cells.shape[0] ** 2)
        self.plot.ax.set_ylim(0, min(1, max(self.differenzen) * 1.2))
        if len(self.differenzen) % 10 == 0:
            self.line2.set_ydata([self.differenzen[0], self.differenzen[0]])
            self.line2.set_xdata([0, len(self.differenzen)])
            self.line.set_ydata(self.differenzen)
            self.line.set_xdata(range(len(self.differenzen)))
            self.plot.ax.set_xlim(0, len(self.differenzen))
            self.plot._surface = None

        self.cells[:] = self.buffer
        self.parent.toggle_update = True


class GOLGUI(Presenter):
    FPS = 20
    _seed = 1
    _dim = 100
    size = np.array([1280, 800])
    color = (100, 100, 100)

    def manual_init(self):
        ScrollTextfeld(self, self.size - (550, 30), (50, 30), "dim", 1, [10, 200])
        ScrollTextfeld(self, self.size - (600, 30), (50, 30), "seed", 1, [0, 10000])
        ScrollTextfeld(self, self.size - (500, 30), (50, 30), "FPS", 1, [1, 50])
        self.slides = [lambda: GoLSlide(self)]

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, value):
        self._seed = value
        self.next

    @property
    def dim(self):
        return self._dim

    @dim.setter
    def dim(self, value):
        self._dim = value
        self.next


if __name__ == '__main__':
    GOLGUI().run()
