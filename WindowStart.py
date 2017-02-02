import tkinter as tk
import numpy
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')

myfigure=None
mycanvas=None
myplot=None
mycounter=0

from WindowStartPagePRBS import PageStartPRBS
from WindowsStartPageRampReference import PageStartRampReference
from WindowsStartPageDiracReference import PageStartDiracReference
from WindowsStartPageSinusoidalReference import PageStartSinusoidalReference
from WindowsStartPageStepReference import PageStartStepReference
from WindowsStartPagePID import PageStartPID
from WindowsStartPageRST import PageStartRST

class PageStart():
    def __init__(self, params):
        # global GLOBAL_PARAMS
        # global myseries_t, myseries_y
        global myfigure, myplot, mycanvas
        WIDGET_PX = params['gui']['widget_px']
        WIDGET_PY = params['gui']['widget_py']
        LABEL_PX = params['gui']['label_px']
        LABEL_PY = params['gui']['label_py']
        WIDGET_W = params['gui']['widget_w']
        WIDGET_H = params['gui']['widget_h']
        Dialog2 = tk.Toplevel()
        Dialog2.title("Control Panel")

        def cb():
            print("variable is", cbvar.get())
        # menu
        menubar = tk.Menu(Dialog2)
        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Export data")
        filemenu.add_command(label="Save plot")
        menubar.add_cascade(label="Data", menu=filemenu)
        filemenu = tk.Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Controller manual input")
        filemenu2 = tk.Menu(filemenu, tearoff=0)
        # filemenu2.add_command(label="PID", command=self.WIN_CALLBACK_ControllerPID)
        # filemenu2.add_command(label="RST", command=self.WIN_CALLBACK_ControllerRST)
        filemenu.add_cascade(label="Controller manual input", menu=filemenu2)
        filemenu2.add_cascade(label="PID", command=lambda: PageStartPID(params))
        filemenu2.add_cascade(label="RST", command=lambda: PageStartRST(params))
        filemenu.add_command(label="Controller computation")
        menubar.add_cascade(label="Controller", menu=filemenu)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Step", command=lambda: PageStartStepReference(params))
        filemenu.add_command(label="Sinusoidal", command=lambda: PageStartSinusoidalReference(params))
        filemenu.add_command(label="Dirac", command=lambda: PageStartDiracReference(params))
        filemenu.add_command(label="Ramp", command=lambda: PageStartRampReference(params))
        filemenu.add_command(label="PRBS", command=lambda: PageStartPRBS(params))
        menubar.add_cascade(label="Reference config", menu=filemenu)

        Dialog2.config(menu=menubar)
        r = 0
        frame1 = tk.Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=tk.EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)
        label1 = tk.Label(frame1, text="Control algorithm", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("PID")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        frame1 = tk.Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=tk.EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)
        frame1.columnconfigure(2, weight=1)
        frame1.columnconfigure(3, weight=1)
        label1 = tk.Label(frame1, text="Command", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text1 = tk.StringVar()
        text1.set("0")
        entry1 = tk.Label(frame1, textvariable=text1)
        entry1.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        label1 = tk.Label(frame1, text="Output", )
        label1.grid(row=0, column=2, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("0")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=0, column=3, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        # First set up the figure, the axis, and the plot element we want to animate
        myfigure = Figure(figsize=(5, 4), dpi=100)
        myplot = myfigure.add_subplot(111)
        t = numpy.arange(0.0, 3.0, 0.01)
        y = numpy.sin(2 * numpy.pi * t)
        myplot.plot(t, y)

        frame1 = tk.Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=tk.EW)

        # a tk.DrawingArea
        mycanvas = FigureCanvasTkAgg(myfigure, master=frame1)
        mycanvas.show()

        toolbar = NavigationToolbar2TkAgg(mycanvas, frame1)
        toolbar.update()

        mycanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        mycanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        frame1 = tk.Frame(Dialog2)
        frame1.grid(row=r, column=1, sticky=tk.EW)
        frame1.columnconfigure(0, weight=1)

        cbvar = tk.IntVar()
        c = tk.Checkbutton(
            frame1, text="Reference",
            variable=cbvar,
            command=cb)
        c.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=tk.W)
        cbvar2 = tk.IntVar()
        c = tk.Checkbutton(
            frame1, text="Output",
            variable=cbvar2,
            command=cb)
        c.grid(row=1, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=tk.W)
        cbvar3 = tk.IntVar()
        c = tk.Checkbutton(
            frame1, text="Command",
            variable=cbvar3,
            command=cb)
        c.grid(row=2, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=tk.W)

        r += 1
        # btnEE = tk.Button(Dialog2, text="Execution element control",
        #                    command=self.WIN_CALLBACK_eeControl, width=WIDGET_W)
        # btnEE.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)

        def on_key_event(event):
            print('you pressed %s' % event.key)
            key_press_handler(event, mycanvas, toolbar)

        mycanvas.mpl_connect('key_press_event', on_key_event)

        def update():
            global myfigure, myplot, mycanvas, mycounter
            t = numpy.arange(0.0, 3.0, 0.01)
            y = numpy.sin(2 * numpy.pi * t + mycounter * 0.1)
            myplot.clear()
            myplot.plot(t, y)
            mycanvas.show()
            mycounter += 1

        timer = mycanvas.new_timer(interval=100)
        timer.add_callback(update)
        timer.start()