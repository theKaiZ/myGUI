import pygame
from myGUI.Rect import ScrollTextfeld, Rectangular_object
from myGUI.Slide import Presenter,Slide
import numpy as np
from time import time

def generate_ruleset(number):
    binstring = ""
    n = number
    while len(binstring)<8:
        binstring = str(number%2) + binstring
        number//=2
    print(n, binstring)
    binarray = np.zeros(8,dtype=int)
    for i in range(8):
        binarray[i]=int(binstring[i])
    return binarray

    ruledict = {}
    for i in range(2):
        for j in range(2):
            for k in range(2):

                ruledict[f"{i}{j}{k}"] = binstring[4*i+2*j+k]
    return ruledict


from numba import njit,prange
@njit(cache=True)
def next_generation(cells, rulset, gen):
    nx = cells.shape[0]
    old_cell = cells[:,gen-1]
    for i in range(nx):
        #triple = f"{cells[i-1,old]}{cells[i,old]}{cells[(i+1)%nx,old]}"
        triple = 4*old_cell[i-1] +2* old_cell[i]+ old_cell[(i+1)%nx]
        cells[i,gen] = rulset[triple]


class ca_image(Rectangular_object):
    def __init__(self, parent,cells, **kwargs):
        pos = parent.pos
        size = parent.size
        super().__init__(parent=parent, pos=pos, size=size)
        self.cells = cells

    def draw(self):
        nx, ny = self.cells.size
        s = self.size[0]//nx
        for x in range(nx):
            for y in range(ny):
                pass
                ### todo
                #pygame.draw.rect(self.screen, )


class CA_Slide(Slide):
    def plot_gen(self):
        for gen in range(self.ny):
          for i in range(self.nx):
            Rectangular_object(self, pos=(i * self.s, gen * self.s), size=(self.s, self.s),
                               color=(0, 0, 0) if self.cells[i,gen] == 0 else (235, 235, 235))

    def manual_init(self):
        t = time()
        self.s = 5  ###box size
        self.nx = self.size[0]//self.s
        self.ny = self.size[1]//self.s
        self.cells = np.zeros((self.nx,self.ny),dtype=int)
        self.gen = 0
        self.cells[self.nx//4,0] = 1
        self.cells[self.nx//4*2,0] = 1
        self.cells[self.nx//4*3,0] = 1
        self.ruleset = generate_ruleset(self.parent.rule)
        for i in range(1,self.ny):
            next_generation(self.cells, self.ruleset, i)

        self.plot_gen()
        print(time()-t)




class CA_Presenter(Presenter):
    _rule = 198
    size = np.array([1200,800])
    def manual_init(self):
        self.slides = [lambda:CA_Slide(self)]

    def setup_buttons(self):
        super().setup_buttons()
        ScrollTextfeld(self,pos=self.size-(200,50),size=(100,50), value="rule", change_value=1, limits=[0,255])

    def keydown(self):
        if self.event.key == pygame.K_UP:
            self.rule += 1
        if self.event.key == pygame.K_DOWN:
            self.rule -= 1
        self.toggle_update=True

    def update(self):
        super().update()

    @property
    def rule(self):
        return self._rule

    @rule.setter
    def rule(self, value):
        if value <0 or value > 255:
            return
        self._rule = value
        self.next


if __name__ == '__main__':
    CA_Presenter().run()
