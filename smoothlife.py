import pygame
from myGUI.gameoflife import GOLGUI, GoLSlide, ScrollTextfeld, golpanel, Button, Plot_object
from functools import lru_cache
import numpy as np
from myGUI import Textfeld, Rect_with_text
from numba import njit, prange
from time import time
import random

animaldict = np.load("animals.npy", allow_pickle=True).item()
bell =  lambda x, m, s:np.exp(-((x-m)/s)**2 / 2)



class golpanel2(golpanel):
    _colorkey = None
    def click(self):
        if self.mouseover:
            pos_on_panel = self.parent.mouse_pos-self.pos
            gridsize = self.parent.dim
            pos_on_grid = (pos_on_panel/self.size*gridsize).astype(int)
            for i in range(15):
                p = pos_on_grid + np.random.randint(-5,5, 2)
                if p[0]>=gridsize:
                    p[0]-= gridsize
                if p[1]>=gridsize:
                    p[1]-=gridsize
                self.parent.cells[p[0],p[1]] += np.random.random()
                self.parent.cells[p[0],p[1]] = np.clip(self.parent.cells[p[0],p[1]],0,1)


    def get_color(self, im):
        im += .3
        im = 255 * (im / im.max()) ** 2
        w, h = im.shape
        ret = np.empty((w, h, 3), dtype=np.uint8)
        ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
        ret[:, :, 0] = ret[:, :, 0] / 2
        return ret

    @property
    def colorkey(self):
        return self._colorkey


    @property
    def surface(self):
        if self._surface is not None:
            return self._surface

        surf = pygame.surfarray.make_surface(self.get_color(self.cells*255/self.cells.max()))
        surf = pygame.transform.scale(surf, tuple(self.size))
        if self._colorkey is not None:
            surf.set_colorkey((0,0,0))
        self._surface = surf
        return self._surface


class gol2slide(GoLSlide):
    generation = 0
    animal_name=None
    _sigma = 0.063
    _mu = 0.57  ### growth rate
    _R = 27  # cells per kernel radius
    _T = 10  ###steps per time unit
    _dim = 160
    _kernel = None
    _growth_fun = None
    _seed = 22
    _b = np.array([1])
    TOT = False
    TOT_panel=None

    def manual_init(self):
        self.gen_text = Textfeld(self, (50,900), (100,30), "generation")
        self.differenzen = []
        self.name_fied = Textfeld(self,(250,30), size=(300,0), key="animal_name", text_size=30)
        self.cells = np.zeros((self.dim, self.dim))#, dtype="float32")
        self.golpanel = golpanel2(parent=self, pos=(10, 50), size=(800, 800))
        self.fill_random()

        self.plot_kernel = Plot_object(self, pos=(800,100),size=(300,300), remove_background=True)
        self.plot_kernel.ax.imshow(self.kernel)
        self.plot_kernel.ax.axis("off")

        self.plot_growth_fun = Plot_object(self,pos=(1150,100), size=(300,300), remove_background=True)
        self.plot_growth_fun.ax.plot(*self.growth_fun)

        self.parent.toggle_update = True


        Rect_with_text(self,(890,465), "R", text_size=20)
        Rect_with_text(self,(890,515), "T", text_size=20)
        ScrollTextfeld(self, (900, 450), (50, 30), "R", 1, [3, 30], text_size=20)
        ScrollTextfeld(self, (900, 500), (50, 30), "T", 1, [1, 100], text_size=20)


        Rect_with_text(self,(1250,465), "sigma", text_size=20)
        ScrollTextfeld(self, (1300,450), (100, 30), "sigma", 0.001, [0.001, 12], text_size=20)

        Rect_with_text(self,(1250,515), "µ", text_size=20)

        ScrollTextfeld(self, (1300,500), (100, 30), "mu", .01, [0.01, 1], text_size=20)
        Rect_with_text(self,(1250,565), "dim", text_size=20)
        ScrollTextfeld(self, (1300,550), (50, 30), "dim", 20, [10, 600], text_size=20)
        Rect_with_text(self,(1250,615), "seed", text_size=20)
        ScrollTextfeld(self, (1300,600), (50, 30), "seed", 1, [0, 10000], text_size=20)



    @property
    def buffer(self):
        if self._buffer is None:
            self._buffer = np.zeros(self.cells.shape)#,dtype="float32")
        return self._buffer

    def fill_random(self):
        self.generation=0
        np.random.seed(self.seed)
        self.cells = (np.random.random((self.dim,self.dim)))#.astype("float32"))

    def load_pattern(self, name="random"):
        self.cells = np.zeros(self.cells.shape)#,dtype="float32")
        if name == "random":
            name = random.choice(list(animaldict.keys()))
        animal = animaldict[name]
        self.animal_name = name
        self.name_fied._text_surface = None
        cells = np.array(animal["cells"])
        self.R = animal["R"]
        self.T = animal["T"]
        self.mu = animal["m"]
        self.sigma = animal["s"]
        self.b = animal["b"]

        if cells.shape[0] >=self.cells.shape[0] or cells.shape[1]>=self.cells.shape[1]:
            self.load_pattern("random")
            return
        xoff, yoff = (self.cells.shape[0]-cells.shape[0])//2,(self.cells.shape[1]-cells.shape[1])//2
        self.cells[xoff:xoff+cells.shape[0],yoff:yoff+cells.shape[1]] = cells

    def update_kernel_plot(self):
        self.plot_kernel.ax.imshow(self.kernel)
        self.plot_kernel._surface=None
        #self.fill_random()

    def update_growth_fun(self):
        self.plot_growth_fun.ax.get_children()[0].set_ydata(self.growth_fun[1])
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
        for d in self.updateables:
            d.update()
        self.gen_text.update()
        if self.cells.sum()==0 and self.TOT==False:
            print("tot")
            self.TOT = True
            self.TOT_panel =Rect_with_text(self,pos=(400,450), text="TOT", text_color=(255,0,0), text_size=100)
            return
        if self.cells.sum()==0:
            return
        if self.TOT_panel is not None:
            self.TOT_panel.removefromGUI()
            self.TOT_panel = None
            self.TOT=False
        #if self.generation < 300:
        #    print(self.generation)
        #    np.save(f"data/gen{self.generation:04}.npy",self.cells)
        self.generation += 1
        #x, y = self.parent.growth_fun
        #t = time()
        #next_generation(self.cells, self.buffer,x, y, self.parent.kernel)
        def grow(U):
            return bell(U, self.mu, self.sigma)*2-1
        t  =time()
        buffer = np.real(np.fft.ifft2(self._fkernel*np.fft.fft2(self.cells)))
        self.cells = np.clip(self.cells + 1/self.T * grow(buffer), 0,1)
        #print(time() - t)

        self.parent.toggle_update = True

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
        self.update_growth_fun()

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
        self.update_kernel_plot()

    @property
    def mu(self):
        return self._mu

    @mu.setter
    def mu(self, value):
        if self._mu == value:
            return
        self._mu = value
        self._growth_fun = None
        self.update_growth_fun()

    @property
    def dim(self):
        return self._dim

    @dim.setter
    def dim(self, value):
        if self._dim==value:
            return
        type(self)._dim = value
        self._kernel = None
        self._fkernel=None
        self.kernel
        self.parent.next

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, value):
        self._seed = value




class gol2gui(GOLGUI):
    FPS = 100
    size=np.array([1780,900])

    def manual_init(self):
        self.slides = [lambda: gol2slide(self)]
        ScrollTextfeld(self, self.size - (500, 30), (50, 30), "FPS", 1, [1, 100])




if __name__ == '__main__':
    gol2gui().run()
