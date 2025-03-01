import pygame
from gameoflife import GOLGUI, GoLSlide, ScrollTextfeld, golpanel, Button, Plot_object
from functools import lru_cache
import numpy as np
from myGUI import Textfeld
from numba import njit, prange
from time import time
from load_animal import animaldict
import random


@njit(cache=True, fastmath=True)
def bell(x, m, s):
    return np.exp(-((x-m)/s)**2 / 2)
bell =  lambda x, m, s:np.exp(-((x-m)/s)**2 / 2)

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
    g = gauss_jit(z=z, z0=z0, sigma=sigma, d=d) +  gauss_jit(z=z, z0 = z0+5*sigma, sigma=sigma*3.5, d=d)
    return z, g / g.max()


@lru_cache()
def get_color(value):
    x = int(255 * value)
    x = min(x, 255)
    x = max(0, x)
    return (x, x, x)


@njit(cache=True)#, parallel=True, fastmath=True)
def next_generation(c, newgen, z, grow_fun, kernel):
    xmax = c.shape[0]
    ymax = c.shape[1]
    n = kernel.shape[0]//2
    for x in prange(xmax):
        for y in prange(ymax):
            dasum = 0
            for i in prange(-n, n):
                for j in prange(-n, n):
                    dasum += c[(x + i) % xmax, (y + j) % ymax]*kernel[i+n,j+n]

            newgen[x, y] = grow_fun[min((z <= dasum).sum(),199)]


class golpanel2(golpanel):
    @staticmethod
    @lru_cache(maxsize=255)
    def get_color(value):
        if abs(value) > 1:
            value=1
        if np.isnan(value):
            value = 1
        c = 255 * abs(value)
        return (c//5, c//1, c//2)

    def click(self):
        if self.mouseover:
            pos_on_panel = self.parent.mouse_pos-self.pos
            gridsize = self.parent.parent.dim
            pos_on_grid = (pos_on_panel/self.size*gridsize).astype(int)
            for i in range(15):
                p = pos_on_grid + np.random.randint(-5,5, 2)
                if p[0]>=gridsize:
                    p[0]-= gridsize
                if p[1]>=gridsize:
                    p[1]-=gridsize
                self.parent.cells[p[0],p[1]] += np.random.random()
                self.parent.cells[p[0],p[1]] = np.clip(self.parent.cells[p[0],p[1]],0,1)


    @property
    def surface(self):
        if self._surface is not None:
            return self._surface
        t = time()
        #surf = self.surf
        #nx, ny = self.cells.shape
        #for x in range(nx):
        #    for y in range(ny):
        #        try:
        #            surf.set_at((x, y), self.get_color(self.cells[x,y]))
        #        except:
        #            print(self.get_color(self.cells[x,y]))
        #            print(self.cells[x,y])
        #            assert 0,""
        def gray(im):
            im +=.3
            im = 255 * (im / im.max())**2
            w, h = im.shape
            ret = np.empty((w, h, 3), dtype=np.uint8)
            ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
            ret[:,:,0]=ret[:,:,0]/2
            return ret
        surf = pygame.surfarray.make_surface(gray(self.cells*255/self.cells.max()))
        #self._surface = pygame.transform.smoothscale(surf, tuple(self.size))
        #if self.s >1:
        surf = pygame.transform.scale(surf, tuple(self.size))
        surf.set_colorkey((0,0,0))
        self._surface = surf
        #self.real_fps = 1/(time()-t)
        #print(f"{self.real_fps:.1f} FPS, {self.cells.shape}")
        return self._surface
class gol2slide(GoLSlide):
    generation = 0
    animal_name=None


    def manual_init(self):
        self.gen_text = Textfeld(self, (50,850), (100,30), "generation")
        s = self.parent.dim
        self.differenzen = []

        Button(self, (10, 10), (80, 30), "random", command=lambda: self.fill_random())
        self.name_fied = Textfeld(self,(150,30), size=(300,0), key="animal_name")
        self.cells = np.zeros((s, s))#, dtype="float32")
        golpanel2(parent=self, pos=(10, 50), size=(800, 800))
        self.fill_random()

        self.plot_kernel = Plot_object(self, pos=(800,100),size=(300,300), remove_background=True)
        self.plot_kernel.ax.imshow(self.parent.kernel)
        self.plot_kernel.ax.axis("off")

        self.plot_growth_fun = Plot_object(self,pos=(1150,100), size=(300,300), remove_background=True)
        self.plot_growth_fun.ax.plot(*self.parent.growth_fun)

        self.parent.toggle_update = True

    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = np.zeros(self.cells.shape)#,dtype="float32")
        return self._buffer

    def fill_random(self):
        self.generation=0
        np.random.seed(self.parent.seed)
        self.cells = (np.random.random((self.parent.dim,self.parent.dim)))#.astype("float32"))

    def load_pattern(self, name="random"):
        self.cells = np.zeros(self.cells.shape)#,dtype="float32")
        if name == "random":
            name = random.choice(list(animaldict.keys()))
        animal = animaldict[name]
        self.animal_name = name
        self.name_fied._text_surface = None
        cells = np.array(animal["cells"])
        self.parent.R = animal["R"]
        self.parent.T = animal["T"]
        self.parent.mu = animal["m"]
        self.parent.sigma = animal["s"]
        self.parent.b = animal["b"]

        if cells.shape[0] >=self.cells.shape[0] or cells.shape[1]>=self.cells.shape[1]:
            self.load_pattern("random")
            return
        xoff, yoff = (self.cells.shape[0]-cells.shape[0])//2,(self.cells.shape[1]-cells.shape[1])//2
        self.cells[xoff:xoff+cells.shape[0],yoff:yoff+cells.shape[1]] = cells

    def update_kernel_plot(self):
        self.plot_kernel.ax.imshow(self.parent.kernel)
        self.plot_kernel._surface=None
        #self.fill_random()

    def update_growth_fun(self):
        self.plot_growth_fun.ax.get_children()[0].set_ydata(self.parent.growth_fun[1])
        self.plot_growth_fun._surface=None
        #self.fill_random()

    def keydown(self):
        if self.parent.event.key== pygame.K_F2:
            if self.animal_name is not None:
                self.load_pattern(self.animal_name)
                return
            self.fill_random()
            return

        if self.parent.event.key==pygame.K_r:
            self.animal_name = None
            self.fill_random()

        if self.parent.event.key== pygame.K_o:
            self.load_pattern("random")
            self.generation=0

        if self.parent.event.key== pygame.K_g:
            self.load_pattern("geminium")
            self.generation=0

    @property
    def zl(self):
        return 0

    @property
    def zr(self):
        return 100

    def update(self):
        self.gen_text.update()
        if self.cells.sum()==0:
            print("tot")
            return
        if self.generation < 300:
            print(self.generation)
            np.save(f"data/gen{self.generation:04}.npy",self.cells)
        self.generation += 1
        #x, y = self.parent.growth_fun
        #t = time()
        #next_generation(self.cells, self.buffer,x, y, self.parent.kernel)
        def grow(U):
            return bell(U, self.parent.mu, self.parent.sigma)*2-1
        t  =time()
        buffer = np.real(np.fft.ifft2(self.parent._fkernel*np.fft.fft2(self.cells)))
        self.cells = np.clip(self.cells + 1/self.parent.T * grow(buffer), 0,1)
        #print(time() - t)

        self.parent.toggle_update = True




class gol2gui(GOLGUI):
    FPS = 100
    _sigma = 0.063
    _mu = 0.57  ### growth rate
    _R = 27 #cells per kernel radius
    _T = 10 ###steps per time unit
    _dim = 600
    _kernel = None
    _growth_fun = None
    _seed = 22
    size=np.array([1780,900])
    _b = np.array([1])

    def manual_init(self):
        self.slides = [lambda: gol2slide(self)]
        ScrollTextfeld(self, (1000,450), (100, 30), "sigma", 0.001, [0.001, 12])
        ScrollTextfeld(self, (900, 450), (50, 30), "R", 1, [3, 30])
        ScrollTextfeld(self, (950, 450), (50, 30), "T", 1, [1, 100])
        ScrollTextfeld(self, (1100,450), (100, 30), "mu", .01, [0.01, 1])
        ScrollTextfeld(self, self.size - (550, 30), (50, 30), "dim", 20, [10, 600])
        ScrollTextfeld(self, self.size - (600, 30), (50, 30), "seed", 1, [0, 10000])
        ScrollTextfeld(self, self.size - (500, 30), (50, 30), "FPS", 1, [1, 100])


    @property
    def growth_fun(self):
        if self._growth_fun is not None:
            return self._growth_fun
        x = np.linspace(0,1,100)
        self._growth_fun =  x, 2*bell(x, self.mu, self.sigma)-1
        return self._growth_fun

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        self._b = np.array(value)
        self._kernel = None
        self._fkernel = None
        self.kernel

    @property
    def kernel(self):
        if self._kernel is not None:
            return self._kernel
        R = self.R

        mid = self.dim//2
        #D = np.linalg.norm(np.asarray(np.ogrid[-mid:mid, -mid:mid], dtype=object) + 1) / R
        #K = (D < 1) * bell(D, 0.5, 0.12)

        b = self.b
        D = np.linalg.norm(np.ogrid[-mid:mid, -mid:mid]) / R * len(b)
        K = (D < len(b)) * b[np.minimum(D.astype(int), len(b) - 1)] * bell(D % 1, 0.5, 0.15)

        self._fkernel = np.real(np.fft.fft2(np.fft.fftshift(K/np.sum(K))))
        K = K / np.sum(K)
        self._kernel=K.copy()
        return self._kernel

    @property
    def sigma(self):
        return self._sigma

    @sigma.setter
    def sigma(self, value):
        self._sigma = value
        self._growth_fun=None
        self.active_slide.update_growth_fun()

    @property
    def T(self):
        return self._T

    @T.setter
    def T(self, val:int):
        if self._T ==  val:
            return
        self._T = val

    @property
    def R(self):
        return self._R

    @R.setter
    def R(self, val):
        if self._R == val:
            return
        self._R = val
        self._kernel = None
        self.active_slide.update_kernel_plot()

    @property
    def mu(self):
        return self._mu

    @mu.setter
    def mu(self, value):
        if self._mu == value:
            return
        self._mu = value
        self._growth_fun = None
        self.active_slide.update_growth_fun()

    @property
    def dim(self):
        return self._dim

    @dim.setter
    def dim(self, value):
        if self._dim==value:
            return
        self._dim = value
        self._kernel = None
        self._fkernel=None
        self.kernel
        self.next

if __name__ == '__main__':
    gol2gui().run()
