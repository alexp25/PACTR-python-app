import tkinter as tk
class PageCommunication():
    def __init__(self, params):
        WIDGET_PX = params['gui']['widget_px']
        WIDGET_PY = params['gui']['widget_py']
        LABEL_PX = params['gui']['label_px']
        LABEL_PY = params['gui']['label_py']
        WIDGET_W = params['gui']['widget_w']
        WIDGET_H = params['gui']['widget_h']
        Dialog2 = tk.Toplevel()
        Dialog2.title("Communication")

        # entry
        textComPort = tk.Entry(Dialog2)
        # textComPort.insert(tk.INSERT, GLOBAL_PARAMS['com']['serial_port'])

        textBaudRate = tk.Entry(Dialog2)
        # textBaudRate.insert(tk.INSERT, GLOBAL_PARAMS['com']['baud_rate'])

        # label
        label1 = tk.Label(Dialog2, text="Serial port")
        label2 = tk.Label(Dialog2, text="Baud rate")

        # buttons
        b1 = tk.Button(Dialog2, text="Ok", width=WIDGET_W)
        b2 = tk.Button(Dialog2, text="Open",  width=WIDGET_W)
        b3 = tk.Button(Dialog2, text="Close",  width=WIDGET_W)

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