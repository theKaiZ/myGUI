from Rect import Button, Rectangular_object
from GUI import myGUI


class Slide():
    def __init__(self, parent):
        print("Create", self.__class__.__name__)
        self.content = []  # pictures, plots... seen on the Slide
        self.actions = []  # actions taken on clicks
        self.n_action = 0
        self.parent = parent
        parent.active_slide = self
        self.manual_init()

    def set_indices(self, indices):
        pass

    def manual_init(self):
        pass

    @property
    def next(self):
        if len(self.actions):
            self.actions.pop(0)()
            return True
        return False

    def __del__(self):
        print("\nDelete", self.__class__.__name__, self.content)
        while len(self.content):
            self.content.pop().__del__()


class S1(Slide):
    def manual_init(self):
        self.content.append(Rectangular_object(self.parent, (100, 100), (50, 50)))
        self.content.append(Rectangular_object(self.parent, (100, 200), (50, 50)))
        # P =Plot_object(self.parent,(0,00),(300,300))

    def set_indices(self, indices):
        self.plot.set_plot_indices(indices)


class S2(Slide):
    def manual_init(self):
        self.content.append(Rectangular_object(self.parent, (300, 100), (50, 50)))
        self.content.append(Rectangular_object(self.parent, (300, 200), (50, 50)))


class S3(Slide):
    def manual_init(self):
        self.content.append(Rectangular_object(self.parent, (350, 100), (50, 50)))
        self.content.append(Rectangular_object(self.parent, (350, 200), (50, 50)))


class Presenter(myGUI):
    active_slide = None
    num_slide = 0

    def manual_init(self):
        self.slides = [lambda: S1(self),
                       lambda: S2(self),
                       lambda: S3(self)]

    def setup_buttons(self):
        Button(self, (500, 500), (100, 50), "NEXT", command=lambda: self.next)

    @property
    def next(self):
        if self.active_slide is None:
            self.active_slide = self.slides[self.num_slide]()
            self.num_slide += 1
            if self.num_slide > len(self.slides) - 1:
                self.num_slide = 0
            return
        if not self.active_slide.next:
            del self.active_slide
            self.next


if __name__ == "__main__":
    Presenter().run()
