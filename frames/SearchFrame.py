import asyncio
import datetime
import tkinter
from collections import OrderedDict
from tkinter import ttk

import customtkinter

import dataProceesing
import settings
from SeamlessButton import SeamlessButton
from TreeView import CustomTreeView
from tkcalendar import Calendar
from CustomQuery import CustomQuery, Option


class SearchFrame:
    def __init__(self, client, root):
        self.root = root
        self.searchFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))

        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        self.frameName = customtkinter.CTkLabel(self.searchFrame, text=f"Поиск по клану {self.lastSearchedClan['name']}",
                               font=("Sans serif", 32))
        self.frameName.pack(pady=10)

        self.client = client

        searchOptions = [Option("general", "Общее", {"row": 0, "column": 0}, "label"),
                         Option("townHall", "Тх", {"row": 1, "column": 0}, "entry"),
                         Option("level", "Уровень", {"row": 2, "column": 0}, "entry"),
                         Option("role", "Роль", {"row": 3, "column": 0}, "selector",
                                ["Не выбрано", "Член", "Старейшина", "Соруководитель", "Глава"]),
                         Option("send", "Задонатил", {"row": 4, "column": 0}, "entry"),
                         Option("received", "Получил", {"row": 5, "column": 0}, "entry"),

                         Option("wars", "Войны", {"row": 0, "column": 1}, "label"),
                         Option("starsAVG", "Средние звезды", {"row": 1, "column": 1}, "entry"),
                         Option("percentAVG", "Средние проценты", {"row": 2, "column": 1}, "entry"),
                         Option("attacks", "Количество атак", {"row": 3, "column": 1}, "entry"),
                         Option("attacksMissed", "Пропущеные атаки", {"row": 4, "column": 1}, "entry"),
                         Option("opponentTh", "Тх оппонента", {"row": 5, "column": 1}, "selector",
                                ["Не выбрано", "Атаковал равного", "Атаковал слабого", "Атаковал сильного"]),

                         Option("cg", "Игры клана", {"row": 0, "column": 2}, "label"),
                         Option("earnedMedalsAVG", "Средние медали", {"row": 1, "column": 2}, "entry"),

                         Option("cc", "Столица клана", {"row": 0, "column": 3}, "label"),
                         Option("lootedGoldAVG", "Среднее золото", {"row": 1, "column": 3}, "entry"),
                         Option("attacksAVG", "Среднее число атак", {"row": 2, "column": 3}, "entry")]

        self.fields = CustomQuery(self.root,self.searchFrame,self.lastSearchedClan,searchOptions,"SearchFrame",colorCorrection="gray17")

        self.fields.createEntries()

        getResButton = customtkinter.CTkButton(self.fields.inputsFrame, text="Поиск", command=self.buildResultTable)
        getResButton.pack(pady=10)

        self.resFrame = customtkinter.CTkFrame(self.fields.inputsFrame)
        self.resFrame.pack(pady=10)

    def buildResultTable(self):
        data = self.fields.serch()
        if data is None:
            return

        for widget in self.resFrame.winfo_children():
            widget.destroy()
        names = list(OrderedDict.fromkeys(data.pop("columns")))
        names = [self.fields.columnNames[i] for i in names]
        toSort = (i for i in range(len(names)))
        resTree = CustomTreeView(self.resFrame, show="headings", names=names, toSort=toSort)
        resTree.pack(expand=True)

        for member in data.values():
            resTree.insert("", tkinter.END,
                           values=member)

    async def updateData(self):
        self.lastSearchedClan = settings.getSetting("lastSearchedClan")
        self.frameName.configure(text=f"Поиск по клану {self.lastSearchedClan['name']}")

    def show(self):
        self.searchFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)
