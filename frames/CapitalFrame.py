import asyncio
import datetime
import tkinter
from tkinter import ttk

import customtkinter

import dataProceesing
import settings
from CustomQuery import Option, CustomQuery
from TreeView import CustomTreeView
from frames.LoadingFrame import LoadingFrame


class CapitalFrame:
    def __init__(self, client,root,loop):
        self.root = root
        self.loop = loop
        self.capitalFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))

        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        self.frameName = customtkinter.CTkLabel(self.capitalFrame, text=f"Рейды клана {self.lastSearchedClan['name']}",
                               font=("Sans serif", 32))
        self.frameName.pack(pady=10)

        capitalFieldsFrame = customtkinter.CTkFrame(self.capitalFrame)
        capitalFieldsFrame.pack(expand=True)

        searchOptions = [Option("wars", "Атаки", {"row": 0, "column": 0}, "label"),
                         Option("raids", "Количество рейдов", {"row": 1, "column": 0}, "entry"),
                         Option("attacks", "Количество атак", {"row": 2, "column": 0}, "entry"),
                         Option("districtsDestroyed", "Районов уничтожено", {"row": 3, "column": 0}, "entry"),

                         Option("wars", "Результат", {"row": 0, "column": 1}, "label"),
                         Option("loot", "Золото", {"row": 1, "column": 1}, "entry"),
                         Option("offensiveReward", "Медали за атаку", {"row": 2, "column": 1}, "entry"),
                         Option("defensiveReward", "Медали за защиту", {"row": 3, "column": 1}, "entry")]

        self.capitalFields = CustomQuery(self.root, capitalFieldsFrame, self.lastSearchedClan, searchOptions, "capitalRaids")
        self.capitalFields.createEntries()

        updateButtton = customtkinter.CTkButton(self.capitalFrame, text="Обновить данные",
                                                command=lambda: self.loop.create_task(self.updateData()))
        updateButtton.pack()

        self.client = client

        self.raidData = dataProceesing.getCapitalData(self.lastSearchedClan["tag"])

        names = ("Дата начала (UTC+0)", "Дата окончания (UTC+0)", "Золото столицы", "Рейды","Атаки", "Районов уничтожено", "Медали за атаку", "Медали за защиту")
        toSort = (0, 1, 2, 3,4,5,6,7)
        self.raidTree = CustomTreeView(self.capitalFrame, show="headings", names=names, toSort=toSort)
        self.raidTree.bind("<Double-1>", self.createRaidDetailsFrame)
        self.raidTree.pack(expand=True)
        self.raidTree.tag_configure('current', background='#4B0082')

        if self.raidData != {}:
            self.buildRaidTree()

    async def updateData(self,loadingFrame=None):
        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        closeLoadingFrame = False
        if loadingFrame is None:
            closeLoadingFrame = True
            loadingFrame = LoadingFrame(f"Поиск Рейдов Столицы клана {self.lastSearchedClan['name']}", self.root, 10)
            loadingFrame.nextStep("Поиск информации по Столице")
            data = await self.loop.create_task(self.client.getCapitalRaids(self.lastSearchedClan["tag"]))
            loadingFrame.nextStep("Сохранение информации по Столице")
            dataProceesing.saveCapitalRaidData(data, self.lastSearchedClan["tag"])


        query = self.capitalFields.serch()
        self.raidData = dataProceesing.getCapitalData(self.lastSearchedClan["tag"],query=query)
        self.raidTree.delete(*self.raidTree.get_children())
        loadingFrame.nextStep("Вывод информации по Столице")
        self.buildRaidTree()
        try:
            loadingFrame.nextStep("Вывод информации по рейдам столицы")
            query = self.raidDetailsFields.serch()
            self.raidDetailsData = dataProceesing.getCapitalRaidDetailsData(self.lastSearchedClan["tag"],
                                                                            self.startTime, self.endTime,query=query)
            self.raidDetailsTree.delete(*self.raidDetailsTree.get_children())
            loadingFrame.nextStep("Вывод информации по рейдам столицы")
            self.buildRaidDetailsTree()
        except:
            pass
        if closeLoadingFrame: loadingFrame.close()

    def show(self):
        self.capitalFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

    def buildRaidTree(self):
        for raid in self.raidData.values():
            attackState = ""
            if datetime.datetime.strptime(raid["endTime"],
                                          "%Y-%m-%d") > datetime.datetime.utcnow() + datetime.timedelta(
                hours=1):
                attackState = "current"
            self.raidTree.insert("", tkinter.END,
                                 values=[raid['startTime'], raid['endTime'], raid['loot'], raid['raids'],
                                         raid['attacks'], raid['districtsDestroyed'], raid['offensiveReward'],
                                         raid['defensiveReward']],tags=attackState)

    def createRaidDetailsFrame(self, event):
        if self.raidTree.identify("region", event.x, event.y) != "cell":
            return
        for selection in self.raidTree.selection():
            item = self.raidTree.item(selection)
            self.startTime, self.endTime = item["values"][0:2]

        self.raidDetailsFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))
        self.raidDetailsFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

        customtkinter.CTkLabel(self.raidDetailsFrame, text=f"Рейды клана {self.lastSearchedClan['name']} с {self.startTime} по {self.endTime}",
                               font=("Sans serif", 32)).pack(pady=10)

        raidDetailsFieldsFrame = customtkinter.CTkFrame(self.raidDetailsFrame)
        raidDetailsFieldsFrame.pack(expand=True)

        searchOptions = [Option("wars", "Рейды", {"row": 0, "column": 0}, "label"),
                         Option("attacks", "Атаки", {"row": 1, "column": 0}, "entry"),
                         Option("lootedGold", "Золото столицы", {"row": 2, "column": 0}, "entry")]

        self.raidDetailsFields = CustomQuery(self.root, raidDetailsFieldsFrame, self.lastSearchedClan, searchOptions, "capitalRaidMembers",False)
        self.raidDetailsFields.createEntries()

        updateButtton = customtkinter.CTkButton(self.raidDetailsFrame, text="Обновить данные",
                                                command=lambda: self.loop.create_task(self.updateData()))
        updateButtton.pack()
        self.raidDetailsData = dataProceesing.getCapitalRaidDetailsData(self.lastSearchedClan['tag'], self.startTime,
                                                                        self.endTime)

        names = ("Тег", "Имя", "Атаки", "Золото столицы")
        toSort = (0, 1, 2, 3)
        self.raidDetailsTree = CustomTreeView(self.raidDetailsFrame, show="headings", names=names, toSort=toSort)
        self.raidDetailsTree.pack(expand=True)

        self.raidDetailsTree.tag_configure('good', background='#006400')
        self.raidDetailsTree.tag_configure('notFine', background='#b45f06')
        self.raidDetailsTree.tag_configure('0attaks', background='#92000A')

        exitButton = customtkinter.CTkButton(self.raidDetailsFrame, text="Назад",
                                             command=lambda: self.closeRaidDetails())
        exitButton.pack(pady=10)

        self.buildRaidDetailsTree()

    def closeRaidDetails(self):
        try:
            self.raidDetailsFields.calFrame.destroy()
        except:
            pass
        try:
            self.raidDetailsFields.optionsFrame.destroy()
        except:
            pass
        try:
            self.raidDetailsFrame.destroy()
        except:
            pass


    def buildRaidDetailsTree(self):
        for attack in self.raidDetailsData.values():
            attackState = ""
            if attack['attacks'] == 0:
                attackState = "0"
            elif attack['attacks'] < 6:
                attackState = "notFine"
            elif attack['attacks'] == 6:
                attackState = "good"
            self.raidDetailsTree.insert("", tkinter.END,
                                        values=[attack["tag"], attack["name"], attack["attacks"], attack["loot"]],tags=attackState)
