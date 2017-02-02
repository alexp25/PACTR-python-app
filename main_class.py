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


# import other files
from PageOne import PageOne
from WindowStart import PageStart
from WindowCommunication import PageCommunication
from PageExpIdent import PageExpIdent
from PageTwo import PageTwo

qsize = 5
queue_gui = Queue(maxsize=10)
queue_serial_receive = Queue(maxsize=qsize)
queue_serial_send = Queue(maxsize=qsize)
queue_serial_gui = Queue(maxsize=qsize)

CONFIG_FILE = 'config/config.json'
GLOBAL_PARAMS = {}

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

TITLE_FONT = ("Helvetica", 18, "bold")
class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        global GLOBAL_PARAMS
        tk.Tk.__init__(self, *args, **kwargs)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.menubar = Menu(self)
        # create a pulldown menu, and add it to the menu bar
        self.filemenu = Menu(self.menubar, tearoff=0)
        # self.filemenu.add_command(label="Full screen", command=self.WIN_CALLBACK_fullscreen)
        self.filemenu.add_command(label="Exit", command=lambda: self.show_frame("PageOne"))
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu1 = Menu(self.menubar, tearoff=0)
        self.filemenu1.add_command(label="FESTO Plant", command=lambda: self.show_frame("PageOne"))
        self.filemenu1.add_command(label="User guide", command=lambda: self.show_frame("PageOne"))
        self.menubar.add_cascade(label="Help", menu=self.filemenu1)
        # display the menu
        self.config(menu=self.menubar)
        params = {'global':GLOBAL_PARAMS,'title_font': ("Helvetica", 18, "bold")}
        self.frames = {}
        for F in (PageOne,MainWindow,PageTwo, PageExpIdent):
            page_name = F.__name__
            frame = F(parent=container, controller=self, params=params)
            self.frames[page_name] = frame
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("MainWindow")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class MainWindow(Frame):
    def __init__(self, parent, controller, params):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # define variables
        self.config_changed=False
        # initialize
        print('read config data')
        self.read_config_data()
        # DEFINE GUI
        self.frameColor = "slate gray"
        self.widgetColor = "light gray"
        self.widgetTextColor = "white"

        self.topFrame = Frame(self, border=4)
        self.topFrame.pack(side=TOP,fill=X)
        self.topFrame.config(bg=self.frameColor)

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
        r += 1
        self.btnExpId = ttk.Button(self.topFrame, text="Experimental identification",
                                   command=lambda: controller.show_frame("PageExpIdent"), width=WIDGET_W)
        self.btnExpId.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnModelParamId = ttk.Button(self.topFrame, text="Model parameter identification", width=WIDGET_W)
        self.btnModelParamId.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)

        r += 1
        self.label2 = tk.Label(self.topFrame, width=WIDGET_W, text="FESTO Plant", bg=self.frameColor,
                               foreground=self.widgetTextColor, font=customFont)
        self.label2.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnPCC = ttk.Button(self.topFrame, text="Peripheral Control Configuration", width=WIDGET_W)
        self.btnPCC.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnDS = ttk.Button(self.topFrame, text="Device Status", width=WIDGET_W)
        self.btnDS.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1

        r = 1
        self.btnConnection = ttk.Button(self.topFrame, text="Bluetooth Connection", width=WIDGET_W,
                                        command=lambda: PageCommunication(GLOBAL_PARAMS))
        self.btnConnection.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnStart = ttk.Button(self.topFrame, text="Connect", width=WIDGET_W, command=self.WIN_CALLBACK_connect)
        self.btnStart.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnStart = ttk.Button(self.topFrame, text="Start", width=WIDGET_W, command=lambda: PageStart(GLOBAL_PARAMS))
        self.btnStart.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY)

        r = 10
        self.labelTextReceive = tk.Label(self.topFrame, width=WIDGET_W, text="Received data",
                                         bg=self.frameColor, foreground=self.widgetTextColor, font=customFont)
        self.labelTextReceive.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=2)
        r += 1
        self.textReceive = tk.StringVar()
        self.entryTextReceive = tk.Label(self.topFrame, textvariable=self.textReceive, font=customFont,
                                         bg=self.widgetColor)
        self.entryTextReceive.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=2, sticky=EW)
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


#################################################################

# init classes (threads)
serialManagerThread = SerialManagerThread()
controlThread = ControlThread()
start_threads()

if __name__ == "__main__":
    # initialise and start main loop

    app = SampleApp()
    app.mainloop()





