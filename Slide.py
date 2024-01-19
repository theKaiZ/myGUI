from myGUI.Rect import Button, Rectangular_object
from myGUI.GUI import myGUI
import pygame
import numpy as np
class Slide():
    _pos = None
    _size = None
    def __init__(self, parent):
        self.actions = []  # actions taken on clicks
        self.drawables = []
        self.updateables = []
        self.clickables = []
        self.parent = parent
        parent.active_slide = self
        self.pos = parent.pos+[0,80]
        self.size = parent.size-[0,80+50]
        self.manual_init()
        self.add2GUI()

    def manual_init(self):
        pass

    @property
    def pos(self):
        if self._pos is None:
            return self.parent.pos
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = np.array(value)

    @property
    def size(self):
        if self._size is None:
            return self.parent.size -self.pos
        return self._size

    @size.setter
    def size(self, value):
        self._size = np.array(value)

    @property
    def next(self):
        if len(self.actions):
            self.actions.pop(0)()
            return True
        return False

    @property
    def screen(self):
        return self.parent.screen

    def add2GUI(self):
        self.parent.drawables.append(self)
        self.parent.updateables.append(self)
        self.parent.clickables.append(self)

    @property
    def myfont(self):
        return self.parent.myfont

    @property
    def mouse_pos(self):
        return self.parent.mouse_pos

    def click(self):
        for obj in self.clickables:
            obj.click()

    def update(self):
        for obj in self.updateables:
            obj.update()

    def draw(self):
        pygame.draw.rect(self.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        for obj in self.drawables:
            obj.draw()

    def removefromGUI(self):
        for obj in self.drawables[::-1]:
            obj.removefromGUI()
        for obj in self.updateables[::-1]:
            obj.removefromGUI()
        for obj in self.clickables[::-1]:
            obj.removefromGUI()
        self.parent.drawables.remove(self)
        self.parent.updateables.remove(self)
        self.parent.clickables.remove(self)


class S1(Slide):
    def manual_init(self):
        Rectangular_object(self, pos=(00, 00), size=(50, 50))
        R = Rectangular_object(self, pos=(100, 200), size=(50, 50))
        Button(self, (260,100), (50,50), "Hallo",command=lambda:R.__setattr__("color", np.random.randint((235,235,235))))
        # P =Plot_object(self.parent,(0,00),(300,300))
        self.actions.append(lambda: R.__setattr__("color",(10,50,30)))


class S2(Slide):
    def manual_init(self):
        R1 = Rectangular_object(self, pos= (300, 100), size= (50, 50))
        R2 = Rectangular_object(self, pos=(300, 200), size=(50, 50))

        self.actions.append(lambda:R1.__setattr__("color",(50,30,10)))
        self.actions.append(lambda:R2.__setattr__("color",(150,60,80)))


class S3(Slide):
    def manual_init(self):
        Rectangular_object(self, pos=(350, 100), size=(50, 50))
        Rectangular_object(self, pos=(350, 200), size=(50, 50))


class Presenter(myGUI):
    active_slide = None
    num_slide = 0
    size=np.array((1920,1080))
    mode = pygame.locals.FULLSCREEN
    def manual_init(self):
        self.slides = [lambda: S1(self),
                       lambda: S2(self),
                       lambda: S3(self)]

    def setup_buttons(self):
        Button(self, self.size -(100, 50), (100, 50), "NEXT", command=lambda: self.next)

    @property
    def next(self):
        if self.active_slide is None: ###load new slide
            self.active_slide = self.slides[self.num_slide]()
            self.num_slide += 1
            if self.num_slide > len(self.slides) - 1:
                self.num_slide = 0
            return
        if self.active_slide.next:
            return
        self.active_slide.removefromGUI()
        self.active_slide = None
        self.next


if __name__ == "__main__":
    Presenter().run()
