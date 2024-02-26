from myGUI.Rect import Rect
import matplotlib.backends.backend_agg as agg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pygame


matplotlib.rcParams.update({"lines.linewidth": 1,
                            "axes.labelsize": 15,
                            "xtick.labelsize": 8,
                            "ytick.labelsize": 8,
                            "axes.titlesize": 10,
                            'font.size': 8})


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
        if self.remove_background:
            self._surface.set_colorkey((255,255,255))  #remove white background
        return self._surface

    def draw(self):
        if not self.visible:
            return
        self.screen.blit(self.surface, self.pos)

    def removefromGUI(self):
        super().removefromGUI()
        plt.close(self.fig)