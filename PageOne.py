import tkinter as tk
class PageOne(tk.Frame):
    def __init__(self, parent, controller, params):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 1", font=params['title_font'])
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("MainWindow"))
        button.pack()