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
        self.width = 0.5
        self.height = 0.2
        self.connector_radius = self.height / 10
        self.picked_offset = (0,0)

        self.offsets = dict(u = self.height,
                            d = 0,
                            l = self.width / 2,
                            r = -self.width / 2,
                            c = 0)

        self.patch = mpl.patches.Rectangle((self.x - self.width / 2,
                                            self.y - self.height / 2),
                                           self.width, self.height)
        self.patches = [self.patch]

        self.connectors = dict()
        for key in ['u_r',
                    'u_l',
                    'u_c',
                    'd_r',
                    'd_l',
                    'd_c']:
            ud, lr = key.split('_')
            c = mpl.patches.Circle((self.x + self.offsets[lr],
                                    self.y - self.height / 2 + self.offsets[ud]),
                                    self.connector_radius, color='g')
            self.connectors[key] = c



        for p in self.patches + list(self.connectors.values()):
            ax.add_patch(p)

        self.text = ax.text(self.x,
                            self.y,
                            text,
                            horizontalalignment = 'center',
                            verticalalignment = 'center'
                            )

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        xoffset, yoffset = self.picked_offset

        for p in self.patches:
            p.set_x(self.x - xoffset)

        for key, p in self.connectors.items():

            ud, lr = key.split('_')
            p.set_center((self.x + self.offsets[lr] - xoffset,
                          self.y + self.offsets[ud] + yoffset))

        self.text.set_x(self.x + self.width / 2 - xoffset)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y
        xoffset, yoffset = self.picked_offset

        for p in self.patches:
            p.set_y(self.y - yoffset)

        for key, p in self.connectors.items():
            ud, lr = key.split('_')
            p.set_center((self.x + self.offsets[lr] + self.width / 2 - xoffset,
                          self.y + self.offsets[ud] - yoffset))

        self.text.set_y(self.y + self.height / 2 - yoffset)






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

        n = node(self.ax, 0.5, 0.5, "a dummy text that is very very long\n and contains newlines")
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

        if not self.picked:
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

