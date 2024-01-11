from Rect import Button, Rectangular_object
from GUI import myGUI


class Slide():
    drawables = []
    clickables = []
    def __init__(self, parent):
        self.content = []  # pictures, plots... seen on the Slide
        self.actions = []  # actions taken on clicks
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

    def removefromGUI(self):
        for cont in self.content:
            cont.removefromGUI()


class S1(Slide):
    def manual_init(self):
        self.content.append(Rectangular_object(self.parent, pos=(100, 100), size=(50, 50)))
        self.content.append(Rectangular_object(self.parent, pos=(100, 200), size=(50, 50)))
        self.content.append(Button(self.parent, (260,100), (50,50), "Hallo",command=lambda:print("Miaz")))
        # P =Plot_object(self.parent,(0,00),(300,300))

    def set_indices(self, indices):
        self.plot.set_plot_indices(indices)


class S2(Slide):
    def manual_init(self):
        self.content.append(Rectangular_object(self.parent, pos= (300, 100), size= (50, 50)))
        self.content.append(Rectangular_object(self.parent, pos=(300, 200), size=(50, 50)))


class S3(Slide):
    def manual_init(self):
        self.content.append(Rectangular_object(self.parent, pos=(350, 100), size=(50, 50)))
        self.content.append(Rectangular_object(self.parent, pos=(350, 200), size=(50, 50)))


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
