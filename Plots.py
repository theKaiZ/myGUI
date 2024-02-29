from myGUI.Rect import Rect
import matplotlib.backends.backend_agg as agg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pygame



class Plot_object(Rect):
    _surface = None
    fig = None
    ax = None

    def __init__(self, parent, **kwargs):
        ###todo update size
        super(Plot_object, self).__init__(parent=parent, **kwargs)
        ### todo I think about the possibility to pass an object to
        self.remove_background = True if kwargs.get("remove_background") is None else kwargs.get("remove_background")
        if kwargs.get("fig"):
            self.fig = kwargs.get("fig")
        else:
            self.setup()
        self.manual_init()
        self.fig.tight_layout()

    def manual_init(self):
        pass


    def setup(self):
        self.fig, self.ax = plt.subplots(1,1,figsize=self.size//100)


    def plot(self, xdata=None, ydata=None, **kwargs):
        self._surface = None
        if xdata is not None and ydata is not None:
            return self.ax.plot(xdata, ydata, **kwargs)
        elif xdata is not None:
            return self.ax.plot(xdata, **kwargs)

    def render_surface(self):
        if self.remove_background:
            self.fig.set_facecolor((0,0,0,0))
            for ax in self.fig.get_axes():
                ax.set_facecolor((0,0,0,0))
        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        buf = canvas.buffer_rgba()
        #renderer = canvas.get_renderer()
        #raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        self._surface = pygame.image.frombuffer(buf, size, "RGBA")
        #if self.remove_background:
        #    self._surface.set_colorkey((255,255,255))  #remove white background

    @property
    def surface(self):
        """
        rendering the plot for pygame
        Make sure you delete the surface when updating a plot
        :return:
        """
        if self._surface is not None:
            return self._surface
        self.render_surface()
        return self._surface

    def draw(self):
        if not self.visible:
            return
        self.screen.blit(self.surface, self.pos)

    def removefromGUI(self):
        super().removefromGUI()
        plt.close(self.fig)