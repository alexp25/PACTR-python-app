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
# custom modules
from serial_com import serialCom

qsize = 5
queue_gui = Queue(maxsize=10)
queue_serial_receive = Queue(maxsize=qsize)
queue_serial_send = Queue(maxsize=qsize)
queue_serial_gui = Queue(maxsize=qsize)

CONFIG_FILE = 'config/config.json'
GLOBAL_PARAMS = {}
serialcom = serialCom("COM5",115200)

class SerialManagerThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self._stopper = threading.Event()
    def stop(self):
        self._stopper.set()
    def stopped(self):
        return self._stopper.isSet()
    def run(self):
        global queue_serial_receive, queue_serial_send, queue_serial_gui
        global serialcom
        while True:
            time.sleep(0.01)
            # get data from serial port
            serdata = serialcom.get_received_data()
            if serdata is not None:
                if queue_serial_receive.full() == False:
                    queue_serial_receive.put(serdata)
                if queue_serial_gui.full() == False:
                    queue_serial_gui.put(serdata)
            # send data to serial port
            if queue_serial_send.empty() == False:
                serdata = queue_serial_send.get(block=False)
                serialcom.send(serdata)
            if self.stopped():
                break

class ControlThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
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

        # display the menu
        self.master.config(menu=self.menubar,bg=self.frameColor)

        self.topFrame = Frame(self.master, border=4)
        self.topFrame.pack(side=TOP,fill=X)
        self.topFrame.config(bg=self.frameColor)

        # load widgets
        self.createGUI()

        # start threads
        start_threads()

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
        global GLOBAL_PARAMS
        serialcom.stop()
        serialcom.config(GLOBAL_PARAMS['com']['serial_port'], GLOBAL_PARAMS['com']['baud_rate'])
        serialcom.start()

    def WIN_CALLBACK_update_settings(self):
        self.write_config_data()
        messagebox.showinfo("Info", "Settings updated")

    def WIN_CALLBACK_exit(self):
        global serialcom
        print('stop threads')
        stop_threads()
        print('stop serial com')
        serialcom.stop()
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
        # buttons
        self.btnExit = ttk.Button(self.topFrame, text="Exit", command=self.WIN_CALLBACK_exit, width=WIDGET_W)
        self.btnConnect = ttk.Button(self.topFrame, text="Connect", command=self.WIN_CALLBACK_connect, width=WIDGET_W)
        # textbox, spinbox values
        self.textReceive = tk.StringVar()
        self.textElapsed = tk.StringVar()
        # self.textElapsed.set("Test timer")
        # custom font
        customFont = font.Font(family="arial", size=14, slant="roman")
        # textbox
        self.labelElapsed = tk.Label(self.topFrame, textvariable=self.textElapsed, font=customFont, bg=self.widgetColor)
        self.entryTextReceive = tk.Label(self.topFrame,textvariable=self.textReceive, font=customFont, bg=self.widgetColor)
        # labels
        self.labelTextReceive = tk.Label(self.topFrame, width=WIDGET_W, text="Serial receive", bg=self.frameColor, foreground=self.widgetTextColor, font=customFont)
        # style
        s = ttk.Style()
        s.configure('TButton', font=customFont,relief="groove")
        s.configure('TRadiobutton', font=customFont)
        s.configure('TEntry', font=customFont)
        s.configure('TLabel', font=customFont)
        # layout
        r = 0
        self.labelElapsed.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, sticky=EW, columnspan=2)
        r += 1
        self.btnConnect.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.btnExit.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        self.labelTextReceive.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=1)
        self.entryTextReceive.grid(row=r, column=1, padx=WIDGET_PX, pady=WIDGET_PY, columnspan=1, sticky=EW)

#################################################################
if __name__ == "__main__":
    # init classes (threads)
    serialManagerThread = SerialManagerThread(1)
    controlThread = ControlThread(2)

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




