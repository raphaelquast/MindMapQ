import PySimpleGUI as sg
import numpy as np
from pathlib import Path
from MindMap_Q import MindMap

window_width = 1000
window_height = 650

default_theme = "DarkTeal6"
default_style = "classic"

# ------------------------------- This is to include a matplotlib figure in a Tkinter canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backends._backend_tk import ToolTip
from matplotlib.backend_bases import NavigationToolbar2



def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()

    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)

    # set background color based on PySimpleGUI theme
    color = sg.theme_background_color()
    toolbar.config(background=color)
    toolbar._message_label.config(background=color)
    toolbar.update()

    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


import tkinter as tk
from matplotlib import cbook

class Toolbar(NavigationToolbar2Tk):
    toolitems = (
                (None, None, None, None),
                ('Home', 'Reset original view', 'home', 'home'),
                #('Back', 'Back to previous view', 'back', 'back'),
                #('Forward', 'Forward to next view', 'forward', 'forward'),
                (None, None, None, None),
                ('Pan',
                 'Left button pans, Right button zooms\nx/y fixes axis, CTRL fixes aspect',
                 'move',
                 'pan'),
                ('Zoom',
                 'Zoom to rectangle\nx/y fixes axis, CTRL fixes aspect',
                 'zoom_to_rect',
                 'zoom'),
                #('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
                (None, None, None, None),
                ('Save', 'Save the figure', 'filesave', 'save_figure'),
                (None, None, None, None))

    # def __init__(self, *args, **kwargs):
    #     super(Toolbar, self).__init__(*args, **kwargs)

    def __init__(self, canvas, window, *, pack_toolbar=True):
        # Avoid using self.window (prefer self.canvas.get_tk_widget().master),
        # so that Tool implementations can reuse the methods.
        self.window = window

        tk.Frame.__init__(self, master=window, borderwidth=2,
                          width=int(canvas.figure.bbox.width), height=50)

        self._buttons = {}
        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                # Add a spacer; return value is unused.
                self._Spacer()
            else:
                self._buttons[text] = button = self._Button(
                    text,
                    str(cbook._get_data_path(f"images/{image_file}.png")),
                    toggle=callback in ["zoom", "pan"],
                    command=getattr(self, callback),
                )
                if tooltip_text is not None:
                    ToolTip.createToolTip(button, tooltip_text)

        # This filler item ensures the toolbar is always at least two text
        # lines high. Otherwise the canvas gets redrawn as the mouse hovers
        # over images because those use two-line messages which resize the
        # toolbar.
        # label = tk.Label(master=self,
        #                  text='\N{NO-BREAK SPACE}\n\N{NO-BREAK SPACE}')
        # label.pack(side=tk.RIGHT)

        self.message = tk.StringVar(master=self)
        self._message_label = tk.Label(master=self, textvariable=self.message)
        self._message_label.pack(side=tk.RIGHT)

        NavigationToolbar2.__init__(self, canvas)
        if pack_toolbar:
            self.pack(side=tk.BOTTOM, fill=tk.X)


    def set_message(self, s):
        pass


    def _Spacer(self):
        # Buttons are 30px high. Make this 26px tall +2px padding to center it.
        s = tk.Frame(
            master=self, height=26, pady=2, bg=sg.theme_background_color())
        s.pack(side=tk.LEFT, padx=5)
        return s


# ------------------------------- PySimpleGUI CODE
def create_window():

    layout = [
        [
         sg.Canvas(key='controls_cv'),
         sg.B('Grid on/off'),
         sg.HSep(),
         #sg.InputText(key='node_txt'),
         sg.MLine(change_submits=True, autoscroll=True, visible=True, do_not_clear=True, key="node_txt"),
         sg.InputText(default_text = 0.05, key='round_base', change_submits=True, size=(10, 10), tooltip="set grid spacing"),
         sg.B('snap to grid'),
         sg.HSep(),
         sg.B('LOAD MindMap'),
         sg.B('SAVE MindMap'),
         sg.B('Exit'),
         ],
        [sg.Column(
            layout=[
                [sg.Canvas(key='fig_cv',
                           # it's important that you set this size
                           size=(window_width, window_height)
                           )]
            ],
            background_color='#DAE0E6',
            pad=(0, 0)
        )],
        [sg.B('New MindMap'),
         sg.T('Matplotlib Style:'), sg.Combo(plt.style.available,
                                             default_value=default_style,
                                             size=(15, 10),
                                             key='-STYLE-'),
         sg.HSep(),
         sg.B('Set GUI theme'),
         sg.T('GUI Theme:'), sg.Combo(sg.theme_list(),
                                              default_value=default_theme,
                                              size=(15, 10),
                                              key='-THEME-')]
    ]

    window = sg.Window('Graph with controls', layout, finalize=True)

    return window



def create_new_mindmap(window, values):
    # turn interactive mode off to avoid creating a separate plot-window
    plt.ioff()
    plt.close('all')
    plt.style.use(values['-STYLE-'])
    m = MindMap(savepath=r"D:\python_modules\MindMap_Q")

    DPI = m.f.get_dpi()
    m.f.set_size_inches(window_width / float(DPI), window_height / float(DPI))

    draw_figure_w_toolbar(window['fig_cv'].TKCanvas,
                          m.f,
                          window['controls_cv'].TKCanvas)
    return m


def load_mindmap(window, values, savepath=Path(__file__).parent):

    # make sure interactive mode is off so that we don't get a
    # separate plot-window
    plt.ioff()
    plt.close('all')

    m = MindMap.load(savepath)
    # call plt.draw to ensure that the laoded figure is interactive
    plt.draw()
    DPI = m.f.get_dpi()
    m.f.set_size_inches(window_width / float(DPI), window_height / float(DPI))

    #------------------------------- Instead of plt.show()
    draw_figure_w_toolbar(window['fig_cv'].TKCanvas,
                          m.f,
                          window['controls_cv'].TKCanvas)

    return m


def set_gui_theme(window, values, m):
    window.close()
    sg.theme(values['-THEME-'])
    window = create_window()

    draw_figure_w_toolbar(window['fig_cv'].TKCanvas,
                          m.f,
                          window['controls_cv'].TKCanvas)
    return window

def toggle_grid(m):
    m.ax.grid()
    m.f.canvas.draw()


def main():
    # create an initial empty MindMap
    sg.theme(default_theme)
    window = create_window()
    m = create_new_mindmap(window, {'-STYLE-':default_style})
    m.gui = window


    while True:
        event, values = window.read()
        print(event, values)
        if event in (sg.WIN_CLOSED, 'Exit'):  # always,  always give a way out!
            break
        elif event == 'Set GUI theme':
            if values['-THEME-'] != sg.theme():  # if new theme chosen, create a new window
                window = set_gui_theme(window, values, m)
        elif event == 'New MindMap':
            if values['-STYLE-']:
                m = create_new_mindmap(window, values)
        elif event == 'LOAD MindMap':
            m = load_mindmap(window, values)
        elif event == 'SAVE MindMap':
            m.dump()
        elif event == 'Grid on/off':
            toggle_grid(m)
        elif event == 'Set Text' or event == 'node_txt':
            if hasattr(m, 'edit_node') and m.edit_node is not None:
                m.edit_node.text.set_text(values['node_txt'])
                m.f.canvas.draw()
        elif event == "snap to grid" or event=='round_base':
            m.round_base = values["round_base"]

    window.close()


if __name__ == "__main__":
    main()