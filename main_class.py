# gui
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import font, messagebox
# from tkinter.ttk import *
# time
import datetime
import time
# threading
import threading
import json
# error handling
import traceback
# thread messaging
from multiprocessing import Queue
import serial

import numpy

from random import randint, choice


#plot
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')

qsize = 5
queue_gui = Queue(maxsize=10)
queue_serial_receive = Queue(maxsize=qsize)
queue_serial_send = Queue(maxsize=qsize)
queue_serial_gui = Queue(maxsize=qsize)

CONFIG_FILE = 'config/config.json'
GLOBAL_PARAMS = {}


myfigure=None
mycanvas=None
myplot=None
mycounter=0

class serialReadThread (threading.Thread):
    def __init__(self,threadID,name,ser,queue_read):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self._stopper = threading.Event()
        self._req = threading.Event()
        self.time1 = time.time()
        self.data = 0
        self.data_received = 0
        self.ser = ser
        self.receivedFlag = False
        self.queue_read = queue_read

    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        line=''
        while True:
            c = self.ser.read().decode()
            line += c
            if c=='\n':
                self.queue_read.put(line)
                line = ''
            if self.stopped():
                break

        if self.ser.isOpen() == True:
            self.ser.close()

class serialWriteThread (threading.Thread):
    def __init__(self,threadID,name,ser,queue_write):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self._stopper = threading.Event()
        self._req = threading.Event()
        self.ser = ser
        self.queue_write=queue_write

    def stop(self):
        self._stopper.set()
    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        while True:
            if self.stopped():
                break
            time.sleep(0.001)
            try:
                while self.queue_write.empty() == False:
                    sdata = self.queue_write.get(block=False)
                    self.ser.write(sdata.encode())
            except:
                print("serial write exception thread")
                traceback.print_exc()

class SerialManagerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stopper = threading.Event()

        self.queue_read = Queue(maxsize=10)
        self.queue_write = Queue(maxsize=10)

        self.thread1=None
        self.thread2=None

    def stop(self):
        self._stopper.set()
    def stopped(self):
        return self._stopper.isSet()
    def open_com(self,portName,baudRate):
        self.ser = serial.Serial(portName, baudRate, timeout=3)
        self.thread1 = serialReadThread(1, "SERIAL_READ", self.ser, self.queue_read)
        self.thread2 = serialWriteThread(2, "SERIAL_WRITE", self.ser, self.queue_write)
        self.thread1.start()
        self.thread2.start()
    def close_com(self):
        if self.thread1 is not None:
            self.thread1.stop()
            self.thread1.join()
        if self.thread2 is not None:
            self.thread2.stop()
            self.thread2.join()

    def run(self):
        global queue_serial_receive, queue_serial_send, queue_serial_gui
        global serialcom

        while True:
            time.sleep(0.01)
            # get data from serial port
            if self.queue_read.empty() == False:
                sdata=self.queue_read.get(block=False)
                if queue_serial_receive.full() == False:
                    queue_serial_receive.put(sdata)
                if queue_serial_gui.full() == False:
                    queue_serial_gui.put(sdata)
            # send data to serial port
            if queue_serial_send.empty() == False:
                sdata = queue_serial_send.get(block=False)
                if self.queue_write.full() == False:
                    self.queue_write.put(sdata)

            if self.stopped():
                self.close_com()
                break

class ControlThread(threading.Thread):
    def __init__(self,):
        threading.Thread.__init__(self)
        self._stopper = threading.Event()
    def stop(self):
        self._stopper.set()
    def stopped(self):
        return self._stopper.isSet()
    def run(self):
        global queue_serial_send, queue_serial_receive

        while True:
            time.sleep(1)
            # demo: send data periodically
            # usage: request data from central app

            if queue_serial_send.full() == False:
                queue_serial_send.put('1\n')
            if self.stopped():
                break

# GUI
def start_threads():
    serialManagerThread.start()
    controlThread.start()

def stop_threads():
    global serialManagerThread, controlThread
    if serialManagerThread is not None:
        print("stop serial manager thread")
        serialManagerThread.stop()
        serialManagerThread.join()
        serialManagerThread = None
    if controlThread is not None:
        print("stop testing thread")
        controlThread.stop()
        controlThread.join()
        controlThread = None

class MainWindow(Frame):
    def __init__( self,master,fullscreen):
        Frame.__init__(self, master)
        self.master = master
        self.master.title("PACTR APP")
        self.master.minsize(1024, 200)

        # fullscreen control
        self.state = fullscreen
        self.master.bind("<F11>", self.toggle_fullscreen)
        self.master.bind("<Escape>", self.end_fullscreen)

        # define variables
        self.config_changed=False

        # initialize
        print('read config data')
        self.read_config_data()

        # DEFINE GUI
        self.frameColor = "slate gray"
        self.widgetColor = "light gray"
        self.widgetTextColor = "white"

        # menu
        self.menubar = Menu(self, bg=self.widgetColor)
        # create a pulldown menu, and add it to the menu bar  
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Full screen", command=self.WIN_CALLBACK_fullscreen)
        self.filemenu.add_command(label="Communication", command=self.WIN_MENU_communication)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.WIN_CALLBACK_exit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.filemenu1 = Menu(self.menubar, tearoff=0)
        self.filemenu1.add_command(label="FESTO Plant", command=self.WIN_MENU_communication)
        self.filemenu1.add_command(label="User guide", command=self.WIN_MENU_communication)
        self.menubar.add_cascade(label="Help", menu=self.filemenu1)

        # display the menu
        self.master.config(menu=self.menubar,bg=self.frameColor)

        self.topFrame = Frame(self.master, border=4)
        self.topFrame.pack(side=TOP,fill=X)
        self.topFrame.config(bg=self.frameColor)

        # load widgets
        self.createGUI()

        # def on_closing():
        #     if messagebox.askokcancel("Quit", "Do you want to quit?"):
        #         root.destroy()

        master.protocol("WM_DELETE_WINDOW", self.WIN_CALLBACK_exit)


        # start gui loop
        self.check_queue()

    def check_queue(self):
        global queue_serial_robot
        global SPECIAL_PARAMS
        log_data = []
        try:
            # check for serial data
            if queue_serial_gui.empty() == False:
                serdata = queue_serial_gui.get(block=False)
                self.textReceive.set(serdata.rstrip('\n'))

            # general loop actions
            # display time
            crt_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.textElapsed.set(crt_time)

        except:
            exc = 'gui update exception: ' + traceback.format_exc()
            print(exc)
        self.master.after(20,self.check_queue)


    def read_config_data(self):
        global GLOBAL_PARAMS, CONFIG_FILE
        with open(CONFIG_FILE) as f:
            file_contents = f.read()
        try:
            GLOBAL_PARAMS = json.loads(file_contents)
            print(GLOBAL_PARAMS)
            return True
        except:
            print('config file exception')
            return False

    def write_config_data(self):
        global GLOBAL_PARAMS, CONFIG_FILE
        params_string = json.dumps(GLOBAL_PARAMS, indent=4, sort_keys=True)
        with open(CONFIG_FILE,'w') as f:
            f.write(params_string)

    def WIN_MENU_communication(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("Communication")
        # callbacks
        def open():
            if serialcom.isConnected()==False:
                serialcom.stop()
                serialcom.config(textComPort.get(), textBaudRate.get())
                serialcom.start()
        def close():
            serialcom.stop()

        def ok():
            try:
                GLOBAL_PARAMS['com']['serial_port'] = textComPort.get()
                GLOBAL_PARAMS['com']['baud_rate'] = int(textBaudRate.get())
                self.config_changed = True
                Dialog2.destroy()
            except:
                messagebox.showinfo("Hello", 'Incorrect values')

        #entry
        textComPort = ttk.Entry(Dialog2)
        textComPort.insert(INSERT, GLOBAL_PARAMS['com']['serial_port'])

        textBaudRate = ttk.Entry(Dialog2)
        textBaudRate.insert(INSERT, GLOBAL_PARAMS['com']['baud_rate'])

        #label
        label1 = ttk.Label(Dialog2, text="Serial port")
        label2 = ttk.Label(Dialog2, text="Baud rate")

        #buttons
        b1 = Button(Dialog2, text="Ok", command=ok,width=WIDGET_W)
        b2 = Button(Dialog2, text="Open", command=open, width=WIDGET_W)
        b3 = Button(Dialog2, text="Close", command=close, width=WIDGET_W)

        r = 0
        label1.grid(row=r, column=0, padx=LABEL_PX, pady=LABEL_PY)
        textComPort.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        label2.grid(row=r, column=0, padx=LABEL_PX, pady=LABEL_PY)
        textBaudRate.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)

        r += 1
        b2.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=2)
        r += 1
        b3.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=2)
        r += 1
        b1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=2)

    def WIN_CALLBACK_PRBS(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("PRBS")

        r = 0
        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = ttk.Label(frame1, text="PRBS:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Length:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text1 = tk.StringVar()
        text1.set("Value")
        entry1 = tk.Label(frame1, textvariable=text1)
        entry1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Magnitude", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Register length:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Frequency Divider:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        btnStart = ttk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        r += 1
        btnStart = ttk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)

    def WIN_CALLBACK_rampReference(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("RampReference")

        r=0
        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = tk.Label(frame1, text="Slope:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("Value")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r+=1
        btnStart = ttk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        r+=1
        btnStart = ttk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)

    def WIN_CALLBACK_sinusoidalReference(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("SinusoidalReference")

        r = 0
        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = tk.Label(frame1, text="Magnitude:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("Value")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        label1 = tk.Label(frame1, text="Frequency:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("Value")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        label1 = tk.Label(frame1, text="Initial phase:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("Value")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        btnStart = ttk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        r += 1
        btnStart = ttk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)

    def WIN_CALLBACK_diracReference(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("DiracReference")

        r=0
        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = tk.Label(frame1, text="Magnitude:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("Value")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r+=1
        btnStart = ttk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        r+=1
        btnStart = ttk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)

    def WIN_CALLBACK_stepReference(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("StepReference")

        r = 0
        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = tk.Label(frame1, text="Magnitude:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("Value")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btnStart = ttk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        r += 1
        btnStart = ttk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)

    def WIN_CALLBACK_exp_model_param(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("Model parameter identification")
        return

    def WIN_CALLBACK_start(self):
        global GLOBAL_PARAMS
        global myseries_t, myseries_y
        global myfigure, myplot, mycanvas
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("Control Panel")

        def cb():
            print("variable is", cbvar.get())

        # menu
        menubar = Menu(Dialog2)
        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Export data")
        filemenu.add_command(label="Save plot")
        menubar.add_cascade(label="Data", menu=filemenu)
        filemenu = Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Controller manual input")
        filemenu2 = Menu(filemenu, tearoff=0)
        filemenu2.add_command(label="PID", command=self.WIN_CALLBACK_ControllerPID)
        filemenu2.add_command(label="RST", command=self.WIN_CALLBACK_ControllerRST)
        filemenu.add_cascade(label="Controller manual input", menu=filemenu2)
        filemenu.add_command(label="Controller computation")
        menubar.add_cascade(label="Controller", menu=filemenu)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Step", command=self.WIN_CALLBACK_stepReference)
        filemenu.add_command(label="Sinusoidal", command=self.WIN_CALLBACK_sinusoidalReference)
        filemenu.add_command(label="Dirac", command=self.WIN_CALLBACK_diracReference)
        filemenu.add_command(label="Ramp", command=self.WIN_CALLBACK_rampReference)
        filemenu.add_command(label="PRBS", command=self.WIN_CALLBACK_PRBS)
        menubar.add_cascade(label="Reference config", menu=filemenu)

        Dialog2.config(menu=menubar)

        r=0

        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)

        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = tk.Label(frame1, text="Control algorithm", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("PID")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)

        r+=1

        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)

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

        r+=1

        # First set up the figure, the axis, and the plot element we want to animate
        myfigure = Figure(figsize=(5, 4), dpi=100)
        myplot = myfigure.add_subplot(111)
        t = numpy.arange(0.0, 3.0, 0.01)
        y = numpy.sin(2 * numpy.pi * t)
        myplot.plot(t, y)

        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)

        # a tk.DrawingArea
        mycanvas = FigureCanvasTkAgg(myfigure, master=frame1)
        mycanvas.show()

        toolbar = NavigationToolbar2TkAgg(mycanvas, frame1)
        toolbar.update()

        mycanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        mycanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=1, sticky=EW)
        frame1.columnconfigure(0, weight=1)

        cbvar = IntVar()
        c = Checkbutton(
            frame1, text="Reference",
            variable=cbvar,
            command=cb)
        c.grid(row=0,column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=W)
        cbvar2 = IntVar()
        c = Checkbutton(
            frame1, text="Output",
            variable=cbvar2,
            command=cb)
        c.grid(row=1, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=W)
        cbvar3 = IntVar()
        c = Checkbutton(
            frame1, text="Command",
            variable=cbvar3,
            command=cb)
        c.grid(row=2, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=W)

        r+=1
        btnEE = ttk.Button(Dialog2, text="Execution element control",
                                          command=self.WIN_CALLBACK_eeControl, width=WIDGET_W)
        btnEE.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)

        def on_key_event(event):
            print('you pressed %s' % event.key)
            key_press_handler(event, mycanvas, toolbar)

        mycanvas.mpl_connect('key_press_event', on_key_event)

        def update():
            global myfigure, myplot, mycanvas, mycounter
            t = numpy.arange(0.0, 3.0, 0.01)
            y = numpy.sin(2 * numpy.pi * t + mycounter*0.1)
            myplot.clear()
            myplot.plot(t, y)
            mycanvas.show()
            mycounter+=1

        timer = mycanvas.new_timer(interval=100)
        timer.add_callback(update)
        timer.start()


    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.master.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.master.attributes("-fullscreen", False)
        return "break"

    def WIN_CALLBACK_fullscreen(self):
        self.toggle_fullscreen()

    def WIN_CALLBACK_connect(self):
        global GLOBAL_PARAMS, serialManagerThread
        serialManagerThread.stop()
        serialManagerThread.join()
        serialManagerThread = SerialManagerThread()
        serialManagerThread.start()
        serialManagerThread.open_com(GLOBAL_PARAMS['com']['serial_port'], GLOBAL_PARAMS['com']['baud_rate'])

    def WIN_CALLBACK_eeControl(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("EEControl")

        r = 0

        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)

        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = ttk.Label(frame1, text="Valve Control:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)

        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)
        frame1.columnconfigure(2, weight=1)
        frame1.columnconfigure(3, weight=1)

        label1 = tk.Label(frame1, text="V1:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        label1 = tk.Label(frame1, text="V2:", )
        label1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        label1 = tk.Label(frame1, text="V3:", )
        label1.grid(row=r, column=2, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        v = IntVar()
        MODES = [
            ("Open", "1"),
            ("Close", "L")
        ]

        rbFrame1 = Frame(Dialog2, border=1)
        rbFrame1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)

        rbFrame1.config(bg=self.widgetTextColor)
        for text, mode in MODES:
            b = tk.Radiobutton(rbFrame1, text=text, value=mode)
            b.pack(anchor=W)

        rbFrame2 = Frame(Dialog2, border=1)
        rbFrame2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        rbFrame2.config(bg=self.widgetTextColor)
        for text, mode in MODES:
            b = Radiobutton(rbFrame2, text=text, value=mode)
            b.pack(anchor=W)

        rbFrame3 = Frame(Dialog2, border=1)
        rbFrame3.grid(row=r, column=2, padx=WIDGET_PX, pady=WIDGET_PY)
        rbFrame3.config(bg=self.widgetTextColor)
        for text, mode in MODES:
            b = Radiobutton(rbFrame3, text=text, value=mode)
            b.pack(anchor=W)

        r += 1
        label1 = ttk.Label(frame1, text="Pump Control:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)

        r += 1
        label1 = tk.Label(frame1, text="P1:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        label1 = tk.Label(frame1, text="P2:", )
        label1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        label1 = tk.Label(frame1, text="P3:", )
        label1.grid(row=r, column=2, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btnStart = ttk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btnStart = ttk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)

    def WIN_CALLBACK_ControllerRST(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("ControllerRST")

        r = 0
        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = tk.Label(frame1, text="Degree R:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text1 = tk.StringVar()
        text1.set("Value")
        entry1 = tk.Label(frame1, textvariable=text1)
        entry1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)

        label1 = tk.Label(frame1, text="Degree S:", )
        label1.grid(row=r, column=2, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=3, padx=WIDGET_PX, pady=WIDGET_PY)

        label1 = tk.Label(frame1, text="Degree T:", )
        label1.grid(row=r, column=4, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=5, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        listbox = Listbox(frame1)
        listbox.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        for item in ["R(0):", "R(1):", "R(2):", "...", "R(value):"]:
            listbox.insert(END, item)

        listbox = Listbox(frame1)
        listbox.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        for item in ["S(0):", "S(1):", "S(2):", "...", "S(value):"]:
            listbox.insert(END, item)

        listbox = Listbox(frame1)
        listbox.grid(row=r, column=2, padx=WIDGET_PX, pady=WIDGET_PY)
        for item in ["T(0):", "T(1):", "T(2):", "...", "T(value):"]:
            listbox.insert(END, item)
        r += 1
        btnStart = tk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btnStart = tk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)


    def WIN_CALLBACK_ControllerPID(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("Controller")

        r = 0
        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = ttk.Label(frame1, text="PID command:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Kp:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text1 = tk.StringVar()
        text1.set("Value")
        entry1 = tk.Label(frame1, textvariable=text1)
        entry1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Ti", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Td:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        btnStart = ttk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        r += 1
        btnStart = ttk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)


    def WIN_CALLBACK_exp_ident(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("Experimental Identification")

        r = 0

        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)

        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)

        label1 = tk.Label(frame1, text="Connencted Device:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("Device name")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)

        r += 1

        frame1 = Frame(Dialog2)
        frame1.grid(row=r, column=0, sticky=EW)

        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)
        frame1.columnconfigure(2, weight=1)
        frame1.columnconfigure(3, weight=1)

        label1 = ttk.Label(frame1, text="PRBS:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Length:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text1 = tk.StringVar()
        text1.set("Value")
        entry1 = tk.Label(frame1, textvariable=text1)
        entry1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Magnitude", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Register length:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        label1 = tk.Label(frame1, text="Frequency Divider:", )
        label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text2 = tk.StringVar()
        text2.set("Value")
        entry2 = tk.Label(frame1, textvariable=text2)
        entry2.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        v = IntVar()
        MODES = [
            ("Structure 1", "1"),
            ("Structure 2", "2"),
            ("Structure 3", "3"),
            ("Structure 4", "L")
        ]
        rbFrame1 = Frame(Dialog2, border=4)
        rbFrame1.grid(row=1, column=1, padx=WIDGET_PX, pady=WIDGET_PY)

        rbFrame1.config(bg=self.widgetTextColor)
        for text, mode in MODES:
            b = Radiobutton(rbFrame1, text=text, value=mode)
            b.pack(anchor=W)
        r += 1
        btnStart = ttk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btnStart = ttk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btnStart = ttk.Button(frame1, text="Help", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)


    def WIN_CALLBACK_update_settings(self):
        self.write_config_data()
        messagebox.showinfo("Info", "Settings updated")

    def WIN_CALLBACK_exit(self):
        global serialcom

        print('stop threads')
        stop_threads()
        if self.config_changed == True:
            self.write_config_data()
            messagebox.showinfo("Info", "Settings updated")
        self.master.destroy()

    def createGUI(self):
        global GLOBAL_PARAMS
        WIDGET_PX = GLOBAL_PARAMS['gui']['widget_px']
        WIDGET_PY = GLOBAL_PARAMS['gui']['widget_py']
        LABEL_PX = GLOBAL_PARAMS['gui']['label_px']
        LABEL_PY = GLOBAL_PARAMS['gui']['label_py']
        WIDGET_W = GLOBAL_PARAMS['gui']['widget_w']
        WIDGET_H = GLOBAL_PARAMS['gui']['widget_h']

        # layout weight
        self.topFrame.columnconfigure(0, weight=0)
        self.topFrame.columnconfigure(1, weight=1)
        # custom font
        customFont = font.Font(family="arial", size=14, slant="roman")
        # style
        s = ttk.Style()
        s.configure('TButton', font=customFont, relief="groove")
        s.configure('TRadiobutton', font=customFont)
        s.configure('TEntry', font=customFont)
        s.configure('TLabel', font=customFont)

        r = 0
        # textbox
        self.textElapsed = tk.StringVar()
        self.labelElapsed = tk.Label(self.topFrame, textvariable=self.textElapsed, font=customFont, bg=self.widgetColor)
        self.labelElapsed.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        r += 1
        self.label1 = tk.Label(self.topFrame, width=WIDGET_W, text="System identification", bg=self.frameColor,
                               foreground=self.widgetTextColor, font=customFont)
        self.label1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r+=1
        self.btnExpId = ttk.Button(self.topFrame, text="Experimental identification",command=self.WIN_CALLBACK_exp_ident, width=WIDGET_W)
        self.btnExpId.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r+=1
        self.btnModelParamId = ttk.Button(self.topFrame, text="Model parameter identification", command=self.WIN_CALLBACK_exp_model_param, width=WIDGET_W)
        self.btnModelParamId.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)

        r += 1
        self.label2 = tk.Label(self.topFrame, width=WIDGET_W, text="FESTO Plant", bg=self.frameColor,
                                         foreground=self.widgetTextColor, font=customFont)
        self.label2.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r+=1
        self.btnPCC = ttk.Button(self.topFrame, text="Peripheral Control Configuration", width=WIDGET_W)
        self.btnPCC.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnDS = ttk.Button(self.topFrame, text="Device Status", width=WIDGET_W)
        self.btnDS.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        r=1
        self.label1 = tk.Label(self.topFrame, width=WIDGET_W, text="Plant Control", bg=self.frameColor,
                                         foreground=self.widgetTextColor, font=customFont)
        self.label1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        v = IntVar()
        MODES = [
            ("Local", "1"),
            ("Remote", "L")
        ]

        self.rbFrame1 = Frame(self.topFrame, border=4)
        self.rbFrame1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        self.rbFrame1.config(bg=self.widgetTextColor)
        for text, mode in MODES:
            b = Radiobutton(self.rbFrame1, text=text, value=mode)
            b.pack(anchor=W)

        # listbox = Listbox(self.topFrame)
        # r += 1
        # listbox.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        # for item in ["Manual", "Automatic"]:
        #     listbox.insert(END, item)
        r+=1
        self.label1 = tk.Label(self.topFrame, width=WIDGET_W, text="Control type", bg=self.frameColor,
                               foreground=self.widgetTextColor, font=customFont)
        self.label1.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r+=1
        variable = StringVar(self.topFrame)
        variable.set("Manual")  # default value
        w = OptionMenu(self.topFrame, variable, "Manual","Automatic")
        w.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)

        r += 1
        self.btnConnection = ttk.Button(self.topFrame, text="Bluetooth Connection", width=WIDGET_W, command=self.WIN_MENU_communication)
        self.btnConnection.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnStart = ttk.Button(self.topFrame, text="Connect", width=WIDGET_W, command=self.WIN_CALLBACK_connect)
        self.btnStart.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnStart = ttk.Button(self.topFrame, text="Start", width=WIDGET_W, command=self.WIN_CALLBACK_start)
        self.btnStart.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)


        r=10
        self.labelTextReceive = tk.Label(self.topFrame, width=WIDGET_W, text="Received data",
                                         bg=self.frameColor, foreground=self.widgetTextColor, font=customFont)
        self.labelTextReceive.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=2)
        r+=1
        self.textReceive = tk.StringVar()
        self.entryTextReceive = tk.Label(self.topFrame, textvariable=self.textReceive, font=customFont,
                                         bg=self.widgetColor)
        self.entryTextReceive.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=2, sticky=EW)

#################################################################

# init classes (threads)
serialManagerThread = SerialManagerThread()
controlThread = ControlThread()
start_threads()

if __name__ == "__main__":


    # initialise and start main loop
    print('app starting')
    root=tk.Tk()
    root.style = ttk.Style()

    # ('clam', 'alt', 'default', 'classic')
    root.style.theme_use("clam")
    fscreen=False
    root.attributes("-fullscreen", fscreen)

    mygui = MainWindow(root,fscreen)
    mygui.pack(fill=BOTH)




    root.mainloop()





