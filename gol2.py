from gameoflife import GOLGUI, GoLSlide, ScrollTextfeld, golpanel, Button, Plot_object
from functools import lru_cache
import numpy as np
from numba import njit, prange
from time import time


@njit(cache=1)
def skewed_gauss(z=np.linspace(-14, -3, 200), z0=-10, sigma=0.5, d=1 / 3):
    sigma_fast = sigma * (1 - d)
    sigma_slow = sigma * (1 + d)
    theta = np.zeros(z.shape[0])
    theta[z < z0] = ((1 - d) / (sigma_fast * np.sqrt(2 * np.pi)) * np.exp(-(z - z0) ** 2 /
                                                                          (2 * sigma_fast ** 2)))[:(z < z0).sum()]
    theta[z >= z0] = ((1 + d) / (sigma_slow * np.sqrt(2 * np.pi)) * np.exp(-(z - z0) ** 2
                                                                           / (2 * sigma_slow ** 2)))[(z < z0).sum():]
    return theta


@njit(cache=True)
def gauss_jit(z, z0, sigma, d):
    if d:
        return skewed_gauss(z, z0, sigma, d)
    return np.exp(-(z - z0) ** 2 / (2 * sigma ** 2)) / np.sqrt(2 * np.pi * sigma ** 2)


@lru_cache()
def gauss(zl=-14, zr=-3, zn=200, z0=-10, sigma=2, d=0):
    """

    :param z:       np.array() with len of 200, logarithmix scale usually form -14 to -3 for the timescale
    :param z0:      the amplitde of the motion (between -14 and -3)
    :param sigma:   sigma of the gaussian dist
    :param d:       skewing the distibution, if needed
    :return:
    """
    z = np.linspace(zl, zr, zn)
    assert (z < z0).sum() and (z > z0).sum(), f"z0 must be between {z[0]} and {z[-1]}, not {z0}"
    g = gauss_jit(z=z, z0=z0, sigma=sigma, d=d) + gauss_jit(z=z, z0 = z0+25, sigma=sigma*1.5, d=d)
    return z, g / g.max()


@lru_cache()
def get_color(value):
    x = int(255 * value)
    x = min(x, 255)
    x = max(0, x)
    return (x, x, x)


@njit(cache=True, parallel=True)
def next_generation(c, newgen, z, gau):
    xmax = c.shape[0]
    ymax = c.shape[1]
    n = 3  ## should be smaller than 7
    for x in prange(xmax):
        for y in prange(ymax):
            dasum = 0
            for i in range(-n, n + 1):
                for j in range(-n, n + 1):
                    dasum += c[(x + i) % xmax, (y + j) % ymax]
            newgen[x, y] = gau[(z <= dasum).sum()]


class golpanel2(golpanel):
    @staticmethod
    @lru_cache(maxsize=255)
    def get_color(value):
        c = 255 * value
        return (c, c, c)


class gol2slide(GoLSlide):
    def manual_init(self):
        s = self.parent.dim
        self.differenzen = []

        Button(self, (10, 10), (80, 30), "random", command=lambda: self.fill_random())
        self.cells = np.zeros((s, s), dtype=int)
        golpanel2(parent=self, pos=(10, 50), size=(600, 600))
        self.fill_random()
        self.plot = Plot_object(self, pos=(650, 50),size= (400, 400), remove_background=False)
        self.line = self.plot.ax.plot(np.ones(50))[0]
        self.plot.ax.set_xlim(self.zl, self.zr)
        self.plot.ax.set_ylim(-0.05, 1.05)
        self.change_plot()
        self.parent.toggle_update = True

    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = np.zeros(self.cells.shape)
        return self._buffer

    def fill_random(self):
        np.random.seed(self.parent.seed)
        self.cells = (np.random.random(self.cells.shape))

    def change_plot(self):
        z, g = gauss(self.zl, self.zr, 300, self.parent.z0, sigma=self.parent.sigma, d=self.parent.d)
        self.line.set_xdata(z)
        self.line.set_ydata(g)
        self.plot._surface = None
        self.fill_random()

    @property
    def zl(self):
        return 0

    @property
    def zr(self):
        return 100

    def update(self):
        z, g = gauss(self.zl, self.zr, 300, self.parent.z0, sigma=self.parent.sigma, d=self.parent.d)
        #t = time()
        next_generation(self.cells, self.buffer, z, g)
        self.cells[:] = self.buffer
        #print(time() - t)

        self.parent.toggle_update = True


class gol2gui(GOLGUI):
    FPS = 5
    _sigma = 3.05
    _d = 0.99
    _z0 = 7.25

    def manual_init(self):
        self.slides = [lambda: gol2slide(self)]
        ScrollTextfeld(self, self.size - (800, 30), (50, 30), "z0", 0.25, [1, 100])
        ScrollTextfeld(self, self.size - (850, 30), (50, 30), "sigma", 0.05, [0.05, 12])
        ScrollTextfeld(self, self.size - (900, 30), (50, 30), "d", 0.01, [-.99, .99])
        ScrollTextfeld(self, self.size - (550, 30), (50, 30), "dim", 10, [10, 300])
        ScrollTextfeld(self, self.size - (600, 30), (50, 30), "seed", 1, [0, 10000])
        ScrollTextfeld(self, self.size - (500, 30), (50, 30), "FPS", 1, [1, 50])

    @property
    def sigma(self):
        return self._sigma

    @sigma.setter
    def sigma(self, value):
        self._sigma = value
        self.active_slide.change_plot()

    @property
    def d(self):
        return self._d

    @d.setter
    def d(self, value):
        self._d = value
        self.active_slide.change_plot()

    @property
    def z0(self):
        return self._z0

    @z0.setter
    def z0(self, value):
        self._z0 = value
        self.active_slide.change_plot()


if __name__ == '__main__':
    gol2gui().run()
