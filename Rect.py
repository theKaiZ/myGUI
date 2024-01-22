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
    _pos = None
    _size = None
    _color = None
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.add2GUI()
        self.pos = kwargs.get("pos")
        self.size = kwargs.get("size")
        self.color = kwargs.get("color")
        self.visible = True if kwargs.get("visible") is None else kwargs.get("visible")

    @property
    def pos(self):
        return self._pos

    @property
    def event(self):
        return self.parent.event

    @pos.setter
    def pos(self, value):
        if value is None:
            self._pos = self.parent.pos
        else:
            self._pos = self.parent.pos + np.array(value)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if value is None:
            self._size = self.parent.size
        else:
            self._size = np.array(value)

    @property
    def screen(self):
        return self.parent.screen

    def add2GUI(self):
        if hasattr(self, "click"):
            self.parent.clickables.append(self)
        if hasattr(self, "draw"):
            self.parent.drawables.append(self)
        if hasattr(self, "update"):
            self.parent.updateables.append(self)

    def removefromGUI(self):
        if hasattr(self, "draw"):
            self.parent.drawables.remove(self)
        if hasattr(self, "click"):
            self.parent.clickables.remove(self)
        if hasattr(self, "update"):
            self.parent.updateables.remove(self)

    def draw(self):
        if not self.visible:
            return
        pygame.draw.rect(self.screen, self.color if self.mouseover else self.color+(20,20,20),
                         (self.pos[0], self.pos[1], self.size[0], self.size[1]), 0)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value is None:
            self._color = np.array([150, 150, 150])
        else:
            self._color=np.array(value)

    @property
    def corners(self):
        if self._corners is not None:
            return self._corners
        self._corners = np.concatenate(([self.pos], [self.pos + self.size]))
        return self._corners

    @property
    def mouseover(self):
        mouse = self.parent.mouse_pos
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

    #def __del__(self):
    #    print("delte",self,"from",self.parent)


class Plot_object(Rectangular_object):
    _surface = None
    fig = None
    ax = None

    def __init__(self, parent, pos, size, **kwargs):
        ###todo update size
        super(Plot_object, self).__init__(parent=parent, pos=pos, size=size, **kwargs)
        self.setup()

    def setup(self):
        self.fig, self.ax = plt.subplots()

    def plot(self, xdata=None, ydata=None, **kwargs):
        self._surface = None
        if xdata is not None and ydata is not None:
            self.ax.plot(xdata, ydata, **kwargs)
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
        self._surface = pygame.image.frombuffer(raw_data, size, "RGB")
        return self._surface

    def draw(self):
        if not self.visible:
            return
        self.screen.blit(self.surface, self.pos)


class RectImage(Rectangular_object):
    def __init__(self, parent, pos, image, **kwargs):
        image = Image.open(image)
        size = image.size
        mode = image.mode
        data = image.tobytes()
        self.image = pygame.image.frombuffer(data, size, mode)
        super(RectImage, self).__init__(parent, pos, size)

    def draw(self):
        self.screen.blit(self.image, self.pos)


class RectImageSeries(Rectangular_object):
    index = 0

    def __init__(self, parent, pos, images):
        images = [Image.open(image) for image in images]
        size = images[0].size
        mode = images[0].mode
        datasets = [image.tobytes() for image in images]
        self.images = [pygame.image.frombuffer(data, size, mode) for data in datasets]
        super(RectImageSeries, self).__init__(parent, pos, size)

    def draw(self):
        if not self.visible:
            return
        if self.mouseover:
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.screen.blit(self.images[self.index], self.pos)


class Button(Rectangular_object):
    active = False

    def __init__(self, parent, pos, size, text, **kwargs):
        super(Button, self).__init__(parent, pos=pos, size=size, **kwargs)
        self.text = text
        self.text_surface = parent.myfont.render(text, False, (0, 0, 0))
        self.command = kwargs.get("command")

    def draw(self):
        if not self.visible:
            return
        super(Button, self).draw()
        pygame.draw.rect(self.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        self.screen.blit(self.text_surface,
                         (self.pos[0] + self.size[0] / 2 - self.text_surface.get_width() /2,
                          self.pos[1] + self.size[1] / 2 - self.text_surface.get_height()/2))
    def click(self):
        if self.mouseover and self.parent.event.button==1:
            self.action()

    def action(self):
        if self.command is not None:
            self.command()


class Textfeld(Rectangular_object):
    _text_surface = None

    def __init__(self, parent, pos, size, value):
        super().__init__(parent, pos=pos, size=size)
        self.value = value

    def draw(self):
        if not self.visible:
            return
        pygame.draw.rect(self.screen, (150, 150, 150), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 0)
        pygame.draw.rect(self.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        self.screen.blit(self.text_surface,
                         (self.pos[0] + self.size[0] / 2 - self.text_surface.get_width() /2,
                          self.pos[1] + self.size[1] / 2 - self.text_surface.get_height()/2))

    @property
    def text_surface(self):
        if self._text_surface is not None:
            return self._text_surface
        wert = getattr(self.parent, self.value)
        if isinstance(wert, float):
            wert = "{0:.3f}".format(wert)
        self.text = str(wert)
        self._text_surface = self.parent.myfont.render(self.text, False, (0, 0, 0))
        return self._text_surface

    def update(self):
        self._text_surface = None


class ScrollTextfeld(Textfeld):
    def __init__(self, parent, pos, size, value, change_value, limits=None, operator="+"):
        super().__init__(parent=parent, pos=pos, size=size, value=value)
        self.change_value = change_value
        self.limits = limits
        self.operator = operator

    def click(self):
        if self.mouseover:
            self.scroll_add()

    def scroll_add(self):
        old_value = getattr(self.parent, self.value)
        if self.parent.event.button == 4:
            if self.operator == "+":
                new_value = old_value + self.change_value
            elif self.operator == "*":
                new_value = old_value * self.change_value
        elif self.parent.event.button == 5:
            if self.operator == "+":
                new_value = old_value - self.change_value
            elif self.operator == "*":
                new_value = old_value / self.change_value
        else:
            return
        if self.limits is not None:
            if new_value < self.limits[0]:
                new_value = self.limits[0]
            if new_value > self.limits[1]:
                new_value = self.limits[1]
        setattr(self.parent, self.value, new_value)
        self._text_surface = None
        self.parent.toggle_update=True
