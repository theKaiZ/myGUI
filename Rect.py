import matplotlib.pyplot as plt
import matplotlib
from os import listdir
from os.path import join
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pygame
import numpy as np
from PIL import Image


class Rect():
    _corners = None
    _pos = None
    _size = None
    _color = None
    _offset = None

    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.add2GUI()
        self.pos = kwargs.get("pos") if kwargs.get("pos") is not None else np.array([0, 0])
        self.size = kwargs.get("size")
        self.color = kwargs.get("color") if kwargs.get("color") is not None else np.array([150, 150, 150])

    @property
    def pos(self):
        if self._offset is not None:
            return self._pos + self.parent.pos + self._offset
        return self._pos + self.parent.pos

    @pos.setter
    def pos(self, value):
        self._pos = np.array(value)

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
        if hasattr(self, "keydown"):
            self.parent.keypressables.append(self)

    def removefromGUI(self):
        if hasattr(self, "draw"):
            self.parent.drawables.remove(self)
        if hasattr(self, "click"):
            self.parent.clickables.remove(self)
        if hasattr(self, "update"):
            self.parent.updateables.remove(self)
        if hasattr(self, "keydown"):
            self.parent.keypressables.remove(self)

    def draw(self):
        pygame.draw.rect(self.screen, self.color,
                         (self.pos[0], self.pos[1], self.size[0], self.size[1]), 0)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if isinstance(value, float):
            value = np.array([value,value,value])
        value = np.array(value)
        if np.isnan(value).sum():
            value[np.isnan(value)]=0
        self._color = value


    @property
    def corners(self):
        if self._corners is not None:
            return self._corners
        self._corners = np.concatenate(([self.pos], [self.pos + self.size]))
        return self._corners


class Rectangular_object(Rect):

    def __init__(self, parent, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.visible = True if kwargs.get("visible") is None else kwargs.get("visible")

    @property
    def event(self):
        return self.parent.event

    def draw(self):
        if not self.visible:
            return
        super().draw()

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

    # def __del__(self):
    #    print("delte",self,"from",self.parent.__class__.__name__)


class Plot_object(Rectangular_object):
    _surface = None
    fig = None
    ax = None

    def __init__(self, parent, pos, size, **kwargs):
        ###todo update size
        super(Plot_object, self).__init__(parent=parent, pos=pos, size=size, **kwargs)
        self.setup()

    def setup(self):
        self.fig, self.ax = plt.subplots(1,1,figsize=self.size//100)

    def plot(self, xdata=None, ydata=None, **kwargs):
        self._surface = None
        if xdata is not None and ydata is not None:
            return self.ax.plot(xdata, ydata, **kwargs)
        elif xdata is not None:
            return self.ax.plot(xdata, **kwargs)

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

    def removefromGUI(self):
        super().removefromGUI()
        plt.close(self.fig)


class RectImage(Rectangular_object):
    def __init__(self, parent, pos, image, **kwargs):
        image = Image.open(image)
        size = image.size
        mode = image.mode
        data = image.tobytes()
        self.image = pygame.image.frombuffer(data, size, mode)
        super(RectImage, self).__init__(parent=parent, pos=pos, size=size, **kwargs)

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
        super(RectImageSeries, self).__init__(parent=parent, pos=pos, size=size)

    def draw(self):
        if not self.visible:
            return
        if self.mouseover:
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.screen.blit(self.images[self.index], self.pos)


class ImgOnLoad():
    _img = None
    _Image = None

    def __init__(self, path, **kwargs):
        self.path = path
        self.scale = kwargs.get("scale")

    @property
    def img(self):
        if self._img is not None:
            return self._img
        img = Image.open(self.path)
        size = img.size
        mode = img.mode
        data = img.tobytes()
        self._img = pygame.image.frombuffer(data, size, mode)
        return self._img

    @property
    def size(self):
        return self.Image.size

    @property
    def Image(self):
        if self._Image is not None:
            return self._Image
        self._Image = Image.open(self.path)
        return self._Image


class VideoRect(Rectangular_object):
    _index = 0

    def __init__(self, parent, folder, **kwargs):
        self.images = [ImgOnLoad(join(folder, image), **kwargs) for image in sorted(listdir(folder))]
        super(VideoRect, self).__init__(parent=parent, size=self.images[0].size, **kwargs)
        self.border = kwargs.get("border") if kwargs.get("border") is not None else True
        self.loop = kwargs.get("loop") if kwargs.get("loop") is not None else False

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        n_images = len(self.images)
        if value <0 and self.loop:
            self._index = n_images - value
        if value >= n_images:
            if self.loop:
                self._index = value % n_images
        else:
            self._index = value


    def draw(self):
        if not self.visible:
            return
        self.screen.blit(self.images[self.index].img, self.pos)
        self.index += 1
        if not self.border:
            return
        pygame.draw.rect(self.screen, (255, 255, 255), (self.pos[0], self.pos[1], self.size[0], self.size[1]),
                             width=1)


class Rect_with_text(Rectangular_object):
    _text_surface = None
    _text_color = None

    def __init__(self, parent, pos, size, text, **kwargs):
        super().__init__(parent=parent, pos=pos, size=size, **kwargs)
        self.text = text
        self.text_color = kwargs.get("text_color") or (0, 0, 0)
        self.text_size = kwargs.get("text_size") or 15

    @property
    def font(self):
        return self.parent.myfonts[self.text_size]

    @property
    def text_surface(self):
        if self._text_surface is None:
            self._text_surface = self.font.render(self.text, False, self.text_color)
        return self._text_surface

    @property
    def text_color(self):
        if self._text_color is None:
            return (0,0,0)
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = value


class Button(Rect_with_text):
    active = False

    def __init__(self, parent, pos, size, text, **kwargs):
        self.command = kwargs.get("command")
        super(Button, self).__init__(parent=parent, pos=pos, size=size, text=text, **kwargs)
        self.panel = True if kwargs.get("panel") is None else kwargs.get("panel")


    def draw(self):
        if not self.visible:
            return
        if self.panel:
            super(Button, self).draw()
            pygame.draw.rect(self.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        self.screen.blit(self.text_surface,
                         (self.pos[0] + self.size[0] / 2 - self.text_surface.get_width() / 2,
                          self.pos[1] + self.size[1] / 2 - self.text_surface.get_height() / 2))

    def click(self):
        if self.mouseover and self.parent.event.button == 1:
            self.action()

    def action(self):
        if self.command is not None:
            self.command()


class Textfeld(Rect_with_text):

    def __init__(self, parent, pos, size, key, **kwargs):
        super().__init__(parent=parent, pos=pos, size=size, text="")
        self.key = key
        self.index = kwargs.get("index")
        self.text_color = kwargs.get("text_color")

    def draw(self):
        if not self.visible:
            return
        pygame.draw.rect(self.screen, (150, 150, 150), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 0)
        pygame.draw.rect(self.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        self.screen.blit(self.text_surface,
                         (self.pos[0] + self.size[0] / 2 - self.text_surface.get_width() / 2,
                          self.pos[1] + self.size[1] / 2 - self.text_surface.get_height() / 2))

    @property
    def value(self):
        if self.index is None:
            return getattr(self.parent, self.key)
        return getattr(self.parent,self.key)[self.index]

    @value.setter
    def value(self, val):
        if self.index is None:
            setattr(self.parent, self.key, val)
            return
        getattr(self.parent, self.key)[self.index] = val



    @property
    def text_surface(self):
        if self._text_surface is not None:
            return self._text_surface
        wert = self.value
        if isinstance(wert, float) or isinstance(wert, np.float32):
            wert = "{0:.3f}".format(wert)

        self.text = str(wert)
        self._text_surface = self.parent.myfont.render(self.text, False, self.text_color)
        return self._text_surface

    def update(self):
        self._text_surface = None


class ScrollTextfeld(Textfeld):
    def __init__(self, parent, pos, size, key, change_value, limits=None, operator="+", **kwargs):
        super().__init__(parent=parent, pos=pos, size=size, key=key, **kwargs)
        self.change_value = change_value
        self.limits = limits
        self.operator = operator

    def click(self):
        if not self.mouseover:
            return
        if self.event.button == 4:   ### Scroll wheel up
            self.increase()
        elif self.event.button == 5:  ### Scroll wheel down
            self.decrease()
        else:
            return
        self._text_surface = None
        self.parent.toggle_update = True

    def keydown(self):
        if not self.mouseover:
            return
        if self.event.key == pygame.K_UP:
            self.increase()
        elif self.event.key == pygame.K_DOWN:
            self.decrease()
        else:
            return
        self._text_surface = None
        self.parent.toggle_update = True


    def increase(self):
        if self.operator == "+":
            new_value = self.value + self.change_value
        elif self.operator == "*":
            new_value = self.value * self.change_value
        if self.limits is not None:
            if new_value > self.limits[1]:
                new_value = self.limits[1]
        self.value = new_value

    def decrease(self):
        if self.operator == "+":
            new_value = self.value - self.change_value
        elif self.operator == "*":
            new_value = self.value / self.change_value
        if self.limits is not None:
            if new_value < self.limits[0]:
                new_value = self.limits[0]
        self.value = new_value


