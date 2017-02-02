import tkinter as tk
from tkinter import ttk
from tkinter import *
class PageStartDiracReference():
    def __init__(self, params):
        WIDGET_PX = params['gui']['widget_px']
        WIDGET_PY = params['gui']['widget_py']
        LABEL_PX = params['gui']['label_px']
        LABEL_PY = params['gui']['label_py']
        WIDGET_W = params['gui']['widget_w']
        WIDGET_H = params['gui']['widget_h']
        Dialog2 = Toplevel()
        Dialog2.title("DiracReference")

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