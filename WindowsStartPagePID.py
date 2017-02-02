import tkinter as tk
from tkinter import ttk
from tkinter import *
class PageStartPID():
    def __init__(self, params):
        WIDGET_PX = params['gui']['widget_px']
        WIDGET_PY = params['gui']['widget_py']
        LABEL_PX = params['gui']['label_px']
        LABEL_PY = params['gui']['label_py']
        WIDGET_W = params['gui']['widget_w']
        WIDGET_H = params['gui']['widget_h']
        from tkinter import Toplevel
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