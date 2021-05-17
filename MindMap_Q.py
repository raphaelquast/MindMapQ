import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from scipy.spatial import cKDTree
from itertools import cycle

# use a cKDTree based picking to speed up picks for large collections
tree = cKDTree([(1,2), (3,4)])



tree.query((1,1))

colors = cycle('rgb')



class node():
    def __init__(self, ax, x, y, text):
        self._x = x
        self._y = y
        self.picked_offset = (0, 0)

        self.width = 0.5
        self.height = 0.2

        self.patch = mpl.patches.Rectangle((self.x - self.width / 2,
                                            self.y - self.height / 2),
                                           self.width, self.height)

        self.text = ax.text(self.x,
                            self.y,
                            "a dummy text that is very very long\n and contains newlines",
                            horizontalalignment = 'center',
                            verticalalignment = 'center'
                            )

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        xoffset, yoffset = self.picked_offset

        self._x = x
        self.patch.set_x(self.x - xoffset)
        self.text.set_x(self.x - xoffset + self.width / 2)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        xoffset, yoffset = self.picked_offset

        self._y = y
        self.patch.set_y(self.y - yoffset)
        self.text.set_y(self.y - yoffset + self.height / 2)



class MindMap():
    def __init__(self, ax=None):
        if ax is None:
            self.f = plt.figure()
            self.ax = self.f.add_subplot()
            self.f.subplots_adjust(left=0, right=1, bottom=0, top=1)

        self.ax.set_axis_off()

        self.nodes = []
        self.f.canvas.mpl_connect("button_press_event", self.mouse_down)
        self.f.canvas.mpl_connect("button_release_event", self.mouse_up)
        self.f.canvas.mpl_connect('motion_notify_event', self.mouse_move)

        self.pressed = False
        self.picked = None

        n = node(self.ax, 0.5, 0.5, 'asdf')
        self.picked = n
        self.ax.add_patch(n.patch)
        self.nodes.append(n)



    def event_valid(self, event):
        if self.ax.get_navigate_mode()!= None:
            return False
        elif not event.inaxes:
            return False
        elif event.inaxes != self.ax:
            return False
        else:
            return True


    def mouse_down(self, event):
        if not self.event_valid(event):
            return

        self.pressed = True

        for n in self.nodes:
            if n.patch.contains_point(self.ax.transData.transform((event.xdata,
                                                                   event.ydata))):
                n.patch.set_color('r')
                self.picked = n
                x, y = n.patch.xy
                self.picked.picked_offset = (event.xdata - x,
                                             event.ydata - y)
        self.f.canvas.draw()


    def mouse_up(self, event):
        if not self.event_valid(event):
            return

        self.pressed = False

        if self.picked is None:
            n = node(self.ax, event.xdata, event.ydata, 'asdf')

            self.ax.add_patch(n.patch)
            self.nodes.append(n)
        else:
            self.picked.patch.set_color('b')

        self.picked = None
        self.f.canvas.draw()


    def mouse_move(self, event):
        if not self.event_valid(event):
            return

        if self.picked is not None:
            self.picked.x = event.xdata
            self.picked.y = event.ydata

        self.f.canvas.draw()


m = MindMap()



# %%


{'button': <MouseButton.LEFT: 1>,
 'key': None, 'step': 0,
 'dblclick': False,
 'name': 'button_press_event',
 'canvas': <matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg object at 0x000001C6AD2C29D0>,
 'guiEvent': <PyQt5.QtGui.QMouseEvent object at 0x000001C6AA6CCD30>,
 'x': 245, 'y': 277,
 'inaxes': <AxesSubplot:>,
 'xdata': 0.3326612903225806,
 'ydata': 0.6066017316017318}

