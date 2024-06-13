from myGUI.Rect import Button, Rect, Rect_with_text
from myGUI.Plots import Plot_object
from myGUI.GUI import myGUI
import pygame
import numpy as np
from time import time

class Slide(Rect):
    _pos = None
    _size = None
    last_item = None
    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.actions = []  # actions taken on clicks
        self.drawables = []
        self.updateables = []
        self.clickables = []
        self.keypressables = []
        if hasattr(self.parent, "active_slide"):
            if self.parent.active_slide is not None:
                self.parent.active_slide.removefromGUI()
            self.parent.active_slide = self
        self.pos = parent.pos+ kwargs.get("pos") if kwargs.get("pos") else [0,0]
        self.size = kwargs.get("size") if kwargs.get("size") is not None else  parent.size
        self.borders = kwargs.get("borders") or False
        self.manual_init()

    def manual_init(self):
        pass

    @property
    def toggle_update(self):
        return self.parent.toggle_update

    @toggle_update.setter
    def toggle_update(self, value):
        self.parent.toggle_update=value

    @property
    def event(self):
        return self.parent.event



    @property
    def next(self):
        if len(self.actions):
            self.actions.pop(0)()
            return True
        return False

    @property
    def screen(self):
        return self.parent.screen

    def get_font(self, fontsize):
        return self.parent.get_font(fontsize)

    @property
    def mouse_pos(self):
        return self.parent.mouse_pos


    def keydown(self):
        for obj in self.keypressables:
            obj.keydown()

    def click(self):
        for obj in self.clickables:
            obj.click()

    def update(self):
        for obj in self.updateables:
            obj.update()

    def draw(self):
        if self.borders:
            pygame.draw.rect(self.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        for obj in self.drawables:
            obj.draw()

    def removefromGUI(self):
        super().removefromGUI()
        for obj in self.drawables[::-1]:
            obj.removefromGUI()
        for obj in self.updateables[::-1]:
            obj.removefromGUI()
        for obj in self.clickables[::-1]:
            obj.removefromGUI()
        for obj in self.keypressables[::-1]:
            obj.removefromGUI()


class myPlot(Plot_object):
    do = None
    def manual_init(self):
        self.x = np.linspace(0,4*np.pi,200)
        self.y = np.sin(self.x)
        self.ax.set_xlim(0,np.pi*4)
        self.ax.plot(self.x,self.y)
        self.fill = self.ax.fill_between(self.x,self.y,alpha=0.0)

    def update(self):
        if self.do is not None:
            self.do()
            self.parent.parent.toggle_update=True

    def anim(self):
        a = self.fill.get_alpha()
        if a >=1:
            self.do = None
            return
        a+=0.05
        self.fill.set_alpha(min(1,a))
        self._surface=None
        self.parent.toggle_update=True




class S1(Slide):
    def manual_init(self):
        Rect(self, pos=(00, 00), size=(50, 50))
        p = myPlot(self, pos=(300,300),size=(400,200))
        self.R = Rect(self, pos=(100, 200), size=(50, 50))
        Button(self, (260,100), (50,50), "Hallo",command=lambda:self.R.__setattr__("color", np.random.randint((235,235,235))))
        Rect_with_text(self, (400,50), f"{self.parent.time//60}:{str(self.parent.time).zfill(2)}")
        # P =Plot_object(self.parent,(0,00),(300,300))
        self.actions.append(lambda: setattr(p,"do",p.anim))
        self.actions.append(lambda: self.R.__setattr__("color",(10,150,30)))

    def start_timer(self):
        if self.parent.timer is None:
            self.parent.timer = time()


class S2(Slide):
    def manual_init(self):
        R1 = Rect(self, pos= (300, 100), size= (50, 50))
        #R2 = Rect(self, pos=(300, 200), size=(50, 50))


class S3(Slide):
    def manual_init(self):
        Rect(self, pos=(350, 100), size=(50, 50))
        Rect(self, pos=(350, 200), size=(50, 50))


class Presenter(myGUI):
    active_slide = None
    num_slide = -1
    FPS=25
    size=np.array((800,800))
    color=(50,50,100)
    _color_rect=None
    _time = None
    #mode = pygame.locals.FULLSCREEN
    @property
    def time(self):
        """the time function is supposed to be called when the first slide is opened"""
        if self._time is None:
            self._time = time()
        return int(self._time)

    @property
    def min(self):
        """returns the time in minutes since the first slide was opened"""
        return int(time()-self.time)//60

    @property
    def time_str(self):
        return f"{self.min}:{str((int(time()-self.time))%60).zfill(2)}"

    def manual_init(self):
        self.slides = [lambda: S1(self),
                       lambda: S2(self),
                       #lambda: S3(self)
                       ]

    def setup_buttons(self):
        Button(self, self.size -(100, 50), (100, 50), "NEXT", command=lambda: self.next, text_size=20, hover_color=(0,255,0))

    def keydown(self):
        super().keydown()
        if self.event.key == pygame.K_LEFT:
            self.last
        elif self.event.key == pygame.K_RIGHT:
            self.next

    @property
    def last(self):
        if self.num_slide == -1:
            self.next
            return
        if self.active_slide is not None:
            self.active_slide.removefromGUI()
            self.active_slide = None
            if  self.num_slide:
                self.num_slide -= 1
            else:
                self.num_slide = len(self.slides)-1
        self.slides[self.num_slide]()

    @property
    def next(self):
        if self.active_slide is None:  ###load new slide
            self.num_slide += 1
            if self.num_slide > len(self.slides) - 1:
                self.num_slide = 0
            self.slides[self.num_slide]()
            return
        if self.active_slide.next:
            self.toggle_update=True
            return
        self.num_slide += 1
        if self.num_slide > len(self.slides)-1:
            self.num_slide = 0
        self.slides[self.num_slide]()

    @property
    def color_rect(self):
        if self._color_rect is not None:
            return self._color_rect
        left_colour = (255,255,255)#(30, 60, 150)
        right_colour = (100,180,250)#(50, 90, 250)
        colour_rect = pygame.Surface((2, 2))  # tiny! 2x2 bitmap
        pygame.draw.line(colour_rect, left_colour, (0, 0), (0, 1))  # left colour line
        pygame.draw.line(colour_rect, right_colour, (1, 0), (1, 1))  # right colour line
        self._color_rect = pygame.transform.smoothscale(colour_rect, (self.size[0], self.size[1]))
        return self._color_rect

    def background(self):
        self.screen.blit(self.color_rect, (self.pos[0], self.pos[1], self.size[0], self.size[1]))


if __name__ == "__main__":
    Presenter().run()
