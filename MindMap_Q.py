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

    def mouse_down(self, *args):
        self.pressed = True
        self.picked = None
        event, = args

        for n in self.nodes:
            if n.patch.contains_point(self.ax.transData.transform((event.xdata,
                                                                   event.ydata))):
                n.patch.set_color('r')
                self.picked = n
                x, y = n.patch.xy
                self.picked.picked_offset = (event.xdata - x,
                                             event.ydata - y)
        self.f.canvas.draw()
        print(self.pressed, self.picked.x, self.picked.y)


    def mouse_up(self, *args):
        self.pressed = False
        event, = args

        if self.picked is None:
            width = 0.5
            height = 0.2

            patch = mpl.patches.Rectangle((event.xdata - width / 2,
                                           event.ydata - height / 2),
                                          width,
                                          height)

            n = node(self.ax, event.xdata, event.ydata, 'asdf')

            self.ax.add_patch(n.patch)
            self.nodes.append(n)
        else:
            self.picked.patch.set_color('b')

        self.picked = None
        self.f.canvas.draw()


    def mouse_move(self, event):

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









# %%








# use a cKDTree based picking to speed up picks for large collections
tree = cKDTree(np.stack([x0, y0], axis=1))
maxdist = np.max([w.max(), h.max()])

def picker(artist, event):
    if event.dblclick:
        dist, index = tree.query((event.xdata, event.ydata))
        if dist < maxdist:
            return True, dict(ind=index)
        else:
            if self.cb_annotate in np.atleast_1d(callback):
                self._cb_hide_annotate()
    return False, None

coll.set_picker(picker)



def onpick(event):
    if isinstance(event.artist, collections.EllipseCollection):
        ind = event.ind

        clickdict = dict(
            pos=coll.get_offsets()[ind],
            ID=coll.get_urls()[ind],
            val=coll.get_array()[ind],
            f=f,
        )

        if callback is not None:
            for cb_i in np.atleast_1d(callback):
                cb_i(**clickdict)

f.canvas.mpl_connect("pick_event", onpick)
