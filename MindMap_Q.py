import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as mPath

from pathlib import Path
import pickle


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
                                           self.width, self.height, transform=ax.transData)

        # ------------------------------------------------------
        x0, y0 = self.x - self.width / 2, self.y - self.height / 2
        x1, y1 = x0 + self.width, y0 + self.height
        patch = PathPatch(None, facecolor='green', edgecolor='yellow', alpha=0.5)
        self.updatepath(patch, x0, x1, y0, y1)

        self.patches = [self.patch,
                        patch]

        # ---------------------------------------------------------

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


        from matplotlib.textpath import TextToPath
        from matplotlib.font_manager import FontProperties

        fp = FontProperties(family="Helvetica", style="italic")

        lines = text.split("\n")
        for i, t in enumerate(lines):
            # tp = PathPatch(TextPath((self.x, self.y + i * self.height / len(lines)), t, prop=fp, size=12, usetex=False),
            #                 color="black")

            verts, codes = TextToPath().get_text_path(fp, t)
            path = mPath(verts, codes, closed=False)

            x0, y0 = ax.transAxes.transform((self.x, self.y))

            path.vertices[:,0] = path.vertices[:,0] + x0
            path.vertices[:,1] = path.vertices[:,1] + y0 + 100 * i
            ax.add_patch(PathPatch(ax.transAxes.inverted().transform_path(path),
                                   color='black'))


    def updatepath(self, patch, x0, x1, y0, y1):

        pathdata = [
            (mPath.MOVETO, (x0, y1)),
            (mPath.LINETO, (x1, y1)),
            (mPath.LINETO, (x1, y0)),
            (mPath.LINETO, (x0, y0)),
        ]

        codes, verts = zip(*pathdata)
        path = mPath(verts, codes)
        patch.set_path(path)


    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        xoffset, yoffset = self.picked_offset


        for p in self.patches:
            try:
                p.set_x(self.x - xoffset)
            except:
                self.updatepath(p,
                                self.x - xoffset,
                                self.x - xoffset + self.width,
                                self.y + yoffset,
                                self.y + yoffset + self.height)


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
            try:
                p.set_y(self.y - yoffset)
            except:
                self.updatepath(p,
                                self.x - xoffset,
                                self.x - xoffset + self.width,
                                self.y - yoffset,
                                self.y - yoffset + self.height)


        for key, p in self.connectors.items():
            ud, lr = key.split('_')
            p.set_center((self.x + self.offsets[lr] + self.width / 2 - xoffset,
                          self.y + self.offsets[ud] - yoffset))

        self.text.set_y(self.y + self.height / 2 - yoffset)









class newtextbox(TextBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.total_newlines = 0
        self._observers.connect('change', self.update_width)


    def ignore(self, event):
        if self.ax.get_navigate_mode()!= None:
            return True
        elif not event.inaxes:
            return True
        elif event.inaxes != self.ax:
            return True
        else:
            return False


    def _keypress(self, event):

        if self.ignore(event):
            return
        if self.capturekeystrokes:
            key = event.key
            text = self.text
            if len(key) == 1:
                text = (text[:self.cursor_index] + key +
                        text[self.cursor_index:])
                self.cursor_index += 1

            elif key == 'alt+enter':
                text = (text[:self.cursor_index] + "\n" +
                        text[self.cursor_index:])
                self.cursor_index += 2

            elif key == "right":
                if self.cursor_index != len(text):
                    self.cursor_index += 1
            elif key == "left":
                if self.cursor_index != 0:
                    self.cursor_index -= 1
            elif key == "home":
                self.cursor_index = 0
            elif key == "end":
                self.cursor_index = len(text)
            elif key == "backspace":
                if self.cursor_index != 0:
                    text = (text[:self.cursor_index - 1] +
                            text[self.cursor_index:])
                    self.cursor_index -= 1
            elif key == "delete":
                if self.cursor_index != len(self.text):
                    text = (text[:self.cursor_index] +
                            text[self.cursor_index + 1:])
            self.text_disp.set_text(text)
            self._rendercursor()
            if self.eventson:
                self._observers.process('change', self.text)
                if key in ["enter", "return"]:
                    self._observers.process('submit', self.text)


    def update_width(self, text):
        total_newlines = text.count('\n')

        if total_newlines != self.total_newlines:
            startheight = 0.075
            lineheight = 0.03

            pos = self.ax.get_position()
            self.ax.set_position((pos.x0,
                                  pos.y0,
                                  pos.width,
                                  startheight + lineheight * (total_newlines + 1)
                                  ))

            self.total_newlines = total_newlines
            self._rendercursor()




    def _rendercursor(self):
        # this is a hack to figure out where the cursor should go.
        # we draw the text up to where the cursor should go, measure
        # and save its dimensions, draw the real text, then put the cursor
        # at the saved dimensions

        # This causes a single extra draw if the figure has never been rendered
        # yet, which should be fine as we're going to repeatedly re-render the
        # figure later anyways.
        if self.ax.figure._cachedRenderer is None:
            self.ax.figure.canvas.draw()

        text = self.text_disp.get_text()  # Save value before overwriting it.
        widthtext = text[:self.cursor_index]

        if widthtext:
            lines = widthtext.split('\n')
            n_newlines = len(lines) - 1
            widthtext = lines[-1]
        else:
            n_newlines = 0

        self.text_disp.set_text(widthtext or ",")
        bb = self.text_disp.get_window_extent()

        if not widthtext:  # Use the comma for the height, but keep width to 0.
            bb.x1 = bb.x0 + 1

        if self.total_newlines > 0:
            h = (bb.y1 - bb.y0)
            bb.y0 = bb.y0 + h * (self.total_newlines) // 2
            bb.y0 = bb.y0 - h * (n_newlines)
            bb.y1 = bb.y0 + h

        self.cursor.set(
            segments=[[(bb.x1, bb.y0), (bb.x1, bb.y1)]], visible=True)
        self.text_disp.set_text(text)

        self.ax.figure.canvas.draw()



class TextInput():
    def __init__(self, ax, node):
        self.node = node
        self.text_box = newtextbox(ax, label="Text:", initial="asdf")
        self.text_box.on_submit(self.set_text)
        self.text_box._rendercursor()

        self.connect(node)

    def set_text(self, text):
        if self.node is not None:
            self.node.text.set_text(text)
            plt.draw()

    def connect(self, node):
        if node is not None:
            self.node = node
            self.text_box.set_active(True)
            #self.text_box.set_val("asdf")  # Trigger `submit` with the initial string.



def load(savepath):
    if savepath is None:
        print('you must provide a savepath!')
        return

    with open(Path(savepath) / "save.Qmap", "rb") as file:
        f = pickle.load(file)

    m = MindMap(savepath=savepath, f=f, ax=f.axes[0], nodes=f.Q_nodes)
    return m


class MindMap():
    def __init__(self, savepath=None, load=False, f=None, ax=None, nodes=None):
        if load:

            m

            self.f = plt.figure(figsize=(16,9))
            #self.ax = self.f.add_subplot()
            self.ax = self.f.add_axes([0, 0.2, 1, 0.8], xticks=[], yticks=[], xticklabels=[], yticklabels=[])
            self.nodes = []

            #self.f.subplots_adjust(left=0, right=1, bottom=0, top=1)
        else:
            self.f = f
            self.ax = ax
            self.nodes = nodes



        self.savepath = savepath

        if not (ax and f and nodes):
            self.f = plt.figure(figsize=(16,9))
            #self.ax = self.f.add_subplot()
            self.ax = self.f.add_axes([0, 0.2, 1, 0.8], xticks=[], yticks=[], xticklabels=[], yticklabels=[])
            self.nodes = []

            #self.f.subplots_adjust(left=0, right=1, bottom=0, top=1)
        else:
            self.f = f
            self.ax = ax
            self.nodes = nodes


        # make sure aspect-ratio remains equal when zooming
        self.ax.set_aspect(9/16)
        #self.ax.set_axis_off()

        self.ax_txt = self.f.add_axes([0.1, 0.05, 0.8, 0.075])
        self.inputbox = TextInput(self.ax_txt, None)


        self.f.canvas.mpl_connect("button_press_event", self.mouse_down)
        self.f.canvas.mpl_connect("button_release_event", self.mouse_up)
        self.f.canvas.mpl_connect('motion_notify_event', self.mouse_move)

        self.pressed = False
        self.picked = None
        self.edit_node = None


        # n = node(self.ax, 0.5, 0.5, "a dummy text that is very very long\n and contains newlines")
        # self.nodes.append(n)

    @staticmethod
    def load(savepath):
        if savepath is None:
            print('you must provide a savepath!')
            return

        with open(Path(savepath) / "save.Qmap", "rb") as file:
            f = pickle.load(file)

        m = MindMap(savepath=savepath, f=f, ax=f.axes[0], nodes=f.Q_nodes)
        return m

    def dump(self):
        if self.savepath is None:
            return

        # attach nodes to figure object that will be dumped
        self.f.Q_nodes = self.nodes

        with open(Path(self.savepath) / "save.Qmap", "wb") as file:
            pickle.dump(self.f, file)

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
        self.picked = None
        self.edit_node = None
        for n in self.nodes:
            if n.patch.contains_point(self.ax.transData.transform((event.xdata,
                                                                   event.ydata))):
                n.patch.set_color('r')
                self.picked = n
                x, y = n.patch.xy
                self.picked.picked_offset = (event.xdata - x,
                                             event.ydata - y)
                self.edit_node = n

        self.f.canvas.draw()

    def mouse_up(self, event):
        if not self.event_valid(event):
            return

        self.pressed = False

        if self.picked is None:
            n = node(self.ax, event.xdata, event.ydata, self.inputbox.text_box.text)#'asdf')
            self.nodes.append(n)
        else:
            self.picked.patch.set_color('b')


        if self.edit_node is not None:
            self.inputbox.connect(self.edit_node)

        self.picked = None
        self.f.canvas.draw()
        self.dump()


    def mouse_move(self, event):
        if not self.event_valid(event):
            return

        if not self.picked:
            return

        if self.picked is not None:
            self.picked.x = event.xdata
            self.picked.y = event.ydata

            self.f.canvas.draw()

# %%
if False:
    m = MindMap.load(savepath=r"D:\python_modules\MindMap_Q")
else:
    m = MindMap(savepath=r"D:\python_modules\MindMap_Q")



# %%


# {'button': <MouseButton.LEFT: 1>,
#  'key': None, 'step': 0,
#  'dblclick': False,
#  'name': 'button_press_event',
#  'canvas': <matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg object at 0x000001C6AD2C29D0>,
#  'guiEvent': <PyQt5.QtGui.QMouseEvent object at 0x000001C6AA6CCD30>,
#  'x': 245, 'y': 277,
#  'inaxes': <AxesSubplot:>,
#  'xdata': 0.3326612903225806,
#  'ydata': 0.6066017316017318}

