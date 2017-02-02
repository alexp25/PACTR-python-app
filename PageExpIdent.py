
import tkinter as tk

class PageExpIdent(tk.Frame):
    def __init__(self, parent, controller, params):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # WIDGET_PX = params['global']['gui']['widget_px']
        # WIDGET_PY = params['global']['gui']['widget_py']
        # LABEL_PX = params['global']['gui']['label_px']
        # LABEL_PY = params['global']['gui']['label_py']
        # WIDGET_W = params['global']['gui']['widget_w']
        # WIDGET_H = params['global']['gui']['widget_h']

        WIDGET_PX = 10
        WIDGET_PY = 10
        LABEL_PX = 10
        LABEL_PY = 10
        WIDGET_W = 10
        WIDGET_H = 10

        r = 0
        frame1 = tk.Frame(self)
        frame1.grid(row=r, column=0, sticky=tk.EW)
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)
        label1 = tk.Label(frame1, text="Connencted Device:", )
        label1.grid(row=0, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        text10 = tk.StringVar()
        text10.set("Device name")
        entry10 = tk.Label(frame1, textvariable=text10)
        entry10.grid(row=0, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
    
        r += 1
    
        frame1 = tk.Frame(self)
        frame1.grid(row=r, column=0, sticky=tk.EW)
    
        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(1, weight=1)
        frame1.columnconfigure(2, weight=1)
        frame1.columnconfigure(3, weight=1)
    
        label1 = tk.Label(frame1, text="PRBS:", )
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
    
        v = tk.IntVar()
        MODES = [
            ("Structure 1", "1"),
            ("Structure 2", "2"),
            ("Structure 3", "3"),
            ("Structure 4", "L")
        ]
        rbFrame1 = tk.Frame(self, border=4)
        rbFrame1.grid(row=1, column=1, padx=WIDGET_PX, pady=WIDGET_PY)
    
        # rbFrame1.config(bg=self.widgetTextColor)
        for text, mode in MODES:
            b = tk.Radiobutton(rbFrame1, text=text, value=mode)
            b.pack(anchor=tk.W)
        r += 1
        btnStart = tk.Button(frame1, text="OK", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btnStart = tk.Button(frame1, text="Cancel", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btnStart = tk.Button(frame1, text="Help", width=WIDGET_W)
        btnStart.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
        r += 1
        btn1 = tk.Button(frame1, text="Go to the start page",
                           command=lambda: controller.show_frame("MainWindow"))
        btn1.grid(row=r, column=0, padx=WIDGET_PX, pady=WIDGET_PY)
