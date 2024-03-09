import matplotlib.pyplot as plt
import matplotlib
from os import listdir
from os.path import join

import pygame
import numpy as np
from PIL import Image


class BaseObject():
    _color = None
    _offset = None
    _force = None ###move per frame
    visible = None
    mouseover = False
    def __init__(self, parent, pos, **kwargs):
        self.parent = parent
        self.pos= pos
        for key in kwargs:
            setattr(self, key, kwargs[key])
        if self.visible is None:
            self.visible = True
        self.color = kwargs.get("color")
        self.hover_color = self.set_a_color(kwargs.get("hover_color"))
        self.add2GUI()

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

    @staticmethod
    def set_a_color(value):
        """
        just make sure a color value that is set is in the right format (r,g,b)
        :param value:
        :return:
        """
        if value is None:
            return None
        if isinstance(value, float) or isinstance(value, int):
            value = np.array([value,value,value])
        value = np.array(value)
        if np.isnan(value).sum():
            value[np.isnan(value)]=0
        if (value>255).sum():
            print(f"warning, color value is out of bounds {value} > 255")
        if (value<0).sum():
            print(f"warning, color value is out of bounds {value} < 0")
        return value

    @property
    def force(self):
        return self._force

    @force.setter
    def force(self, value):
        self._force = np.array(value)


    @property
    def pos(self):
        if self._offset is not None:
            return self._pos + self.parent.pos + self._offset
        return self._pos + self.parent.pos

    @pos.setter
    def pos(self, value):
        if value is None:
            value = (0,0)
        self._pos = np.array(value)

    @property
    def screen(self):
        return self.parent.screen

    @property
    def color(self):
        if self.mouseover and self.hover_color is not None:
            return self.hover_color
        return self._color

    @color.setter
    def color(self, value):
        if value is None:
            value = 0
        self._color = self.set_a_color(value)

    @staticmethod
    def distance(p1,p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


class Line(BaseObject):
    _pos2 = None
    _d = None ###distance between pos1 and pos2
    def __init__(self, parent, pos, pos2, **kwargs):
        super().__init__(parent=parent, pos=pos, **kwargs)
        self._pos2 = pos2

    @property
    def pos2(self):
        if self._offset is not None:
            return self._pos2 + self.parent.pos + self._offset
        return self._pos2 + self.parent.pos

    def draw(self):
        if not self.visible:
            return
        pygame.draw.line(self.screen, color=self.color, start_pos=self.pos, end_pos=self.pos2, width=2 if not self.mouseover else 4)
        
    @property
    def d(self):
        if self._d is None:
            self._d = self.distance(self.pos, self.pos2)
        return self._d
    
    @property
    def mouseover(self):
        d1 = self.distance(self.pos, self.parent.mouse_pos)
        d2 = self.distance(self.pos2, self.parent.mouse_pos)
        d = self.d*0.65
        if d1 < d and d2 < d:
            return True
    
class Circle(BaseObject):
    def __init__(self, parent, pos, radius, **kwargs):
        super().__init__(parent=parent, pos=pos, **kwargs)
        self.radius = radius
        self.filled = kwargs.get("filled") if kwargs.get("filled") is not None else False
        self.width = kwargs.get("width") if kwargs.get("width") is not None else 1

    def draw(self):
        if not self.visible:
            return
        pygame.draw.circle(self.screen,color=self.color,center=self.pos, radius=self.radius, width = self.width if not self.filled else 0)
        if self.force is not None:
            self._pos += self.force

    @property
    def mouseover(self):
        mouse_pos = self.parent.mouse_pos
        if self.distance(self.pos, mouse_pos) < self.radius:
            return True
        return False

class CircleButton(Circle):
    def __init__(self, parent, pos, radius, **kwargs):
        super().__init__(parent=parent, pos=pos, radius=radius, **kwargs)
        self.command = kwargs.get("command")

    def action(self):
        if self.command is not None:
            self.command()
    def click(self):
        if self.mouseover:
            self.action()



class Rect(BaseObject):
    _corners = None
    _pos = None
    _size = None
    _offset = None

    def __init__(self, parent,pos=None, **kwargs):
        super().__init__(parent=parent,pos=pos,**kwargs)
        #self.pos = kwargs.get("pos") if kwargs.get("pos") is not None else np.array([0, 0])
        self.size = kwargs.get("size")
        self.filled = kwargs.get("filled")
        self.width=kwargs.get("width") or 0

    @property
    def event(self):
        return self.parent.event
    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if value is None:
            self._size = self.parent.size
            return
        if isinstance(value, int) or isinstance(value, float):
            value = (value, value)   ### now you can initialize the rect with a singular value that is taken twice
        self._size = np.array(value)

    def draw(self):
        if not self.visible:
            return
        pygame.draw.rect(self.screen,
                         self.color,
                         (*self.pos, *self.size),
                         self.width)


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






class RectImage(Rect):
    def __init__(self, parent, pos, image, **kwargs):
        image = Image.open(image)
        size = image.size
        mode = image.mode
        data = image.tobytes()
        self.image = pygame.image.frombuffer(data, size, mode)
        super(RectImage, self).__init__(parent=parent, pos=pos, size=size, **kwargs)
        self.scaling = kwargs.get("scaling") if kwargs.get("scaling") is not None else 1
        self.rotation = kwargs.get("rotation")
        self.border = kwargs.get("border")

    def draw(self):
        if not self.visible:
            return
        img = self.image
        if self.scaling != 1:
            size = (int(self.size[0]*self.scaling), int(self.size[1]*self.scaling))
            img = pygame.transform.scale(img, size)
        if self.rotation is not None:
            img = pygame.transform.rotate(img, self.rotation)
        self.screen.blit(img, self.pos)
        if self.border:
            pygame.draw.rect(self.screen,(0,0,0),(*self.pos,*self.size), width=1)


class RectImageSeries(Rect):
    index = 0

    def __init__(self, parent, pos, images, **kwargs):
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
        self.colorkey = kwargs.get("colorkey")

    @property
    def img(self):
        if self._img is not None:
            return self._img
        img = Image.open(self.path)
        size = img.size
        mode = img.mode
        data = img.tobytes()
        self._img = pygame.image.frombuffer(data, size, mode)
        if self.colorkey is not None:
            self._img.set_colorkey(self.colorkey)
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


class VideoRect(Rect):
    _index = 0

    def __init__(self, parent, folder, **kwargs):
        self.images = [ImgOnLoad(join(folder, image), **kwargs) for image in sorted(listdir(folder))]
        super(VideoRect, self).__init__(parent=parent, size=self.images[0].size, **kwargs)
        self.border = kwargs.get("border") if kwargs.get("border") is not None else True
        self.loop = kwargs.get("loop") if kwargs.get("loop") is not None else False
        self.color = kwargs.get("color") if kwargs.get("color") is not None else (0,0,0)
        self.scaling =kwargs.get("scaling")

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
        if self.scaling is not None:
            size = (int(self.size[0] * self.scaling), int(self.size[1] * self.scaling))
            self.screen.blit(pygame.transform.scale(self.images[self.index].img,size), self.pos)
        else:
            self.screen.blit(self.images[self.index].img, self.pos)
        self.index += 1
        if not self.border:
            return
        pygame.draw.rect(self.screen, self.color, (self.pos[0], self.pos[1], self.size[0], self.size[1]),
                             width=1)


class Rect_with_text(Rect):
    _text_surface = None
    _text_color = None
    _bold = False
    _underline = False
    _text = None
    def __init__(self, parent, pos, text, **kwargs):
        if kwargs.get("size") is None:
            kwargs["size"] = (0,0)
        super().__init__(parent=parent, pos=pos, **kwargs)
        self.text = text
        self.rotate_text = kwargs.get("rotate_text")
        self.text_color = kwargs.get("text_color") if kwargs.get("text_color") is not None else (0, 0, 0)
        self.text_size = kwargs.get("text_size") or 15
        self.underline = kwargs.get("underline")
        self.bold=kwargs.get("bold")
        self.panel = kwargs.get("panel") if kwargs.get("panel") is not None else True

    @property
    def bold(self):
        return self._bold
    @bold.setter
    def bold(self,value):
        if value is None:
            return
        if value == self._bold:
            return
        self._bold = value
        self._text_surface = None

    @property
    def font(self):
        return self.parent.myfonts[self.text_size]

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self,string):
        if string== self.text:
            return
        self._text = string
        self._text_surface = None

    def render_surface(self):
        if self.underline:
            self.font.set_underline(True)
        if self.bold:
            self.font.set_bold(True)
        render = self.font.render(self.text, False, self.text_color)
        self.font.set_underline(False)
        self.font.set_bold(False)
        if self.rotate_text is not None:
            render = pygame.transform.rotate(render, self.rotate_text)
        return render


    @property
    def text_surface(self):
        if self._text_surface is None:
            self._text_surface = self.render_surface()
        return self._text_surface

    @property
    def text_color(self):
        if self._text_color is None:
            return (0,0,0)
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = value

    def draw(self):
        if self.visible is False:
            return
        if self.panel:
            super().draw()
        self.screen.blit(self.text_surface,
                         (self.pos[0] + self.size[0] / 2 - self.text_surface.get_width() / 2,
                          self.pos[1] + self.size[1] / 2 - self.text_surface.get_height() / 2))


class Button(Rect_with_text):
    active = False

    def __init__(self, parent, pos, size, text = "", **kwargs):
        self.command = kwargs.get("command")
        if kwargs.get("color") is None:
            kwargs["color"] = 150
        super(Button, self).__init__(parent=parent, pos=pos, size=size, text=text, **kwargs)
        self.panel = True if kwargs.get("panel") is None else kwargs.get("panel")

    def draw(self):
        if not self.visible:
            return
        super(Button, self).draw()
        pygame.draw.rect(self.screen,(200,200,200), (*self.pos, *self.size), width=2)
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
        super().__init__(parent=parent, pos=pos, size=size, text="",**kwargs)
        self.key = key
        self.index = kwargs.get("index")
        self.text_color = kwargs.get("text_color")
        self.background = kwargs.get("background") if kwargs.get("background") is not None else True

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
            wert = "{0:.5f}".format(wert)

        self.text = str(wert)
        self._text_surface = self.render_surface()

        return self._text_surface

    def update(self):
        self._text_surface = None


class ScrollTextfeld(Textfeld):
    def __init__(self, parent, pos, size, key, change_value=1, limits=None, operator="+", **kwargs):
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


