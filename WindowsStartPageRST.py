import tkinter as tk
from tkinter import ttk
from tkinter import *
class PageStartRST():
    def __init__(self, params):
        WIDGET_PX = params['gui']['widget_px']
        WIDGET_PY = params['gui']['widget_py']
        LABEL_PX = params['gui']['label_px']
        LABEL_PY = params['gui']['label_py']
        WIDGET_W = params['gui']['widget_w']
        WIDGET_H = params['gui']['widget_h']
        from tkinter import Toplevel
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