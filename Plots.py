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
        self.remove_background = True if kwargs.get("remove_background") is None else kwargs.get("remove_background")
        if kwargs.get("fig"):
            self.fig = kwargs.get("fig")
        else:
            self.setup()
        self.manual_init()
        if self.remove_background:
            self.fig.set_facecolor((0, 0, 0, 0))
            for ax in self.fig.get_axes():
                ax.set_facecolor((0, 0, 0, 0))
        self.fig.tight_layout()

    def manual_init(self):
        pass

    def setup(self):
        if sum(self.size) == 0:
            self.size = (200, 200)
        self.fig, self.ax = plt.subplots(1, 1, figsize=self.size // 100)

    def render_surface(self):
        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        self._surface = pygame.image.frombuffer(canvas.buffer_rgba(), canvas.get_width_height(), "RGBA")

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


class Formula(Plot_object):
    textsize = 25

    def __init__(self, parent, formula: str, **kwargs):
        self.formula = formula
        super().__init__(parent=parent, **kwargs)
        self.remove_background = True

    def manual_init(self):
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.text(0.0, .5, self.formula, size=self.textsize, ha="left", va="bottom")
        self.ax.axis("off")
        self.pos -= (self.size[0] // 8, self.size[1] // 2)
