import matplotlib.pyplot as plt
import pylab
import matplotlib

matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg

import pygame
import numpy as np
from PIL import Image
from sys import platform


### todo move that away




class Rectangular_object():
    _corners = None

    def __init__(self, GUI, pos, size, **kwargs):
        self.GUI = GUI
        self.add2GUI()
        self.screen = GUI.screen
        self.pos = np.array(pos)
        self.size = np.array(size)
        self.visible = True if kwargs.get("visible") is None else kwargs.get("visible")

    def add2GUI(self):
        self.GUI.drawables.append(self)

    def removefromGUI(self):
        print("Remove",self)
        self.GUI.drawables.remove(self)

    #def __del__(self):
    #    if self in self.GUI.drawables:
    #        print("Delete", self.__class__.__name__, "from drawables")
    #        ###todo I am unsure about this
    #        self.GUI.drawables.remove(self)
    #    else:
    #        print("Couldnt remove ", self)


    def draw(self):
        if not self.visible:
            return
        pygame.draw.rect(self.screen, (150, 150, 150) if self.mouseover else (170, 170, 170),
                         (self.pos[0], self.pos[1], self.size[0], self.size[1]), 0)

    def click(self):
        pass

    @property
    def corners(self):
        if self._corners is not None:
            return self._corners
        self._corners = np.concatenate(([self.pos], [self.pos + self.size]))
        return self._corners

    @property
    def mouseover(self):
        mouse = self.GUI.mouse_pos
        corn = self.corners
        if mouse[0] < corn[0, 0]:
            return False
        if mouse[0] > corn[1, 0]:
            return False
        if mouse[1] < corn[0, 1]:
            return False
        if mouse[1] > corn[1, 1]:
            return False
        return True


class Plot_object(Rectangular_object):
    _surface = None
    fig = None
    ax = None

    def __init__(self, GUI, pos, size, **kwargs):
        ###todo update size
        super(Plot_object, self).__init__(GUI,pos,size,**kwargs)
        self.setup()

    def setup(self):
        self.fig, self.ax = plt.subplots()

    def plot(self, xdata = None, ydata=None,**kwargs):
        self._surface = None
        if xdata is not None and ydata is not None:
            self.ax.plot(xdata,ydata,**kwargs)
        elif xdata is not None:
            self.ax.plot(xdata, **kwargs)


    @property
    def surface(self):
        """
        rendering the plot for pygame
        Make sure you delete the surface when updating a plot
        :return:
        """
        if self._surface is not None:
            return self._surface
        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        self._surface = pygame.image.frombuffer(raw_data,size,"RGB")
        return self._surface

    def draw(self):
        self.screen.blit(self.surface, self.pos)

class RectImage(Rectangular_object):
    def __init__(self, GUI, pos, image):
        image = Image.open(image)
        size = image.size
        mode = image.mode
        data = image.tobytes()
        self.image = pygame.image.frombuffer(data, size, mode)
        super(RectImage, self).__init__(GUI, pos, size)

    def draw(self):
        self.GUI.screen.blit(self.image, self.pos)


class RectImageSeries(Rectangular_object):
    index = 0

    def __init__(self, GUI, pos, images):
        images = [Image.open(image) for image in images]
        size = images[0].size
        mode = images[0].mode
        datasets = [image.tobytes() for image in images]
        self.images = [pygame.image.frombuffer(data, size, mode) for data in datasets]
        super(RectImageSeries, self).__init__(GUI, pos, size)

    def draw(self):
        if self.mouseover:
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.GUI.screen.blit(self.images[self.index], self.pos)


class Button(Rectangular_object):
    active = False

    def __init__(self, GUI, pos, size, text, **kwargs):
        super(Button, self).__init__(GUI, pos, size, **kwargs)
        self.text = text
        self.text_surface = GUI.myfont.render(text, False, (0, 0, 0))
        self.command = kwargs.get("command")

    def add2GUI(self):
        super().add2GUI()
        self.GUI.clickables.append(self)

    def removefromGUI(self):
        super().removefromGUI()
        self.GUI.clickables.remove(self)

    #def __del__(self):
    #    if self in self.GUI.buttons:   ###todo I am unsure about this
    #        self.GUI.buttons.remove(self)
    #    super(Button, self).__del__()


    def draw(self):
        super(Button, self).draw()
        pygame.draw.rect(self.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        self.screen.blit(self.text_surface, (
            self.pos[0] + self.size[0] / 2 - len(self.text[2:]) * 4.5, self.pos[1] + self.size[1] / 2 - 12))

    def click(self):
        if self.mouseover:
            self.action()

    def action(self):
        if self.command is not None:
            self.command()
