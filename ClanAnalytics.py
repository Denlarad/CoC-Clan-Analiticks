import asyncio
from tkinter import ttk

import customtkinter

import settings
from frames.HelpFrame import HelpFrame
from frames.LoginFrame import LoginFrame
from frames.MainFrame import MainFrame

root = customtkinter.CTk()
root.geometry('1600x900')

customtkinter.set_appearance_mode("dark")

style = ttk.Style()

style.theme_use("default")

style.configure("Treeview",
                background="#2a2d2e",
                foreground="white",
                rowheight=25,
                fieldbackground="#343638",
                bordercolor="#343638",
                borderwidth=0)
style.map('Treeview', background=[('selected', '#22559b')])

style.configure("Treeview.Heading",
                background="#565b5e",
                foreground="white",
                relief="flat")
style.map("Treeview.Heading",
          background=[('active', '#3484F0')])

loop = asyncio.get_event_loop()

mainFrame = MainFrame(root, style, loop)
# customtkinter перезаписывает создание TK(), для изменения wm_state и скорее всего прочих свойств надо вызывать с задержкой
root.after(100, root.wm_state, 'zoomed')
try:
    root.iconbitmap("img/ico.ico")
except:
    pass
root.title('Аналитика клана')
root.bind("<F1>",lambda x:HelpFrame(root))
loop.run_forever()
