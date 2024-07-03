import asyncio
import datetime
import tkinter
from tkinter import ttk

import customtkinter
import numpy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import TreeView
import dataProceesing
import settings
from CustomQuery import CustomQuery, Option
from SeamlessButton import SeamlessButton
from frames.LoadingFrame import LoadingFrame


class AnalyticsFrame:
    def __init__(self, client, root,loop):
        self.root = root
        self.loop = loop
        self.analyticsFrame = customtkinter.CTkFrame(self.root, width=1280, height=720)

        self.createTabs()

        self.generalFrame = customtkinter.CTkFrame(self.analyticsFrame, fg_color=("gray75", "gray25"), height=720,
                                                   width=1280, corner_radius=0)
        self.warFrame = customtkinter.CTkScrollableFrame(self.analyticsFrame, orientation='vertical',
                                                         fg_color=("gray75", "gray25"), height=720,
                                                         width=1280, corner_radius=0)
        self.clanGamesFrame = customtkinter.CTkFrame(self.analyticsFrame, fg_color=("gray75", "gray25"), height=720,
                                                     width=1280, corner_radius=0)
        self.clanCapitalFrame = customtkinter.CTkFrame(self.analyticsFrame, fg_color=("gray75", "gray25"), height=720,
                                                       width=1280, corner_radius=0)
        self.generalFrame.pack_propagate(0)
        self.clanGamesFrame.pack_propagate(0)
        self.clanCapitalFrame.pack_propagate(0)

        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        self.client = client

    def constructWarFrame(self):
        for child in self.warFrame.winfo_children():
            child.destroy()

        customtkinter.CTkLabel(self.warFrame,
                               text=f"{self.selectedMember[0]}",
                               font=("Sans serif", 32)).pack()
        customtkinter.CTkLabel(self.warFrame,
                               text=f"Количество сохраненных атак в кв {self.warData['warAttacksCount']}",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.warFrame,
                               text=f"Был в {self.warData['wasInWars']} войн из {self.warData['wars']} сохраненных",
                               font=("Sans serif", 14)).pack()
        if self.warData["isCurrentlyInWar"]:
            customtkinter.CTkLabel(self.warFrame,
                                   text=f"На данный момент учавствует в войне",
                                   font=("Sans serif", 14)).pack()
        else:
            customtkinter.CTkLabel(self.warFrame,
                                   text=f"На данный момент не учавствует в войне",
                                   font=("Sans serif", 14)).pack()

        self.createWarAttacksChart()

    def createWarAttacksChart(self):
        self.chartsView = customtkinter.CTkTabview(self.warFrame)
        self.chartsView.pack(expand=True)

        self.starTab = self.chartsView.add("Звезды")
        self.ThsTab = self.chartsView.add("Тх")
        self.posTab = self.chartsView.add("Позиции")
        self.attacksTab = self.chartsView.add("Атаки")

        if len(self.warData["warAttacks"]) == 0:
            return
        starsLabels = ["3 звезды", "2 звезды", "1 звезда", "0 звезд"]
        THsLabels = ["Напал на тх выше", "Напал на тх ниже", "Напал на тх своего уровня"]
        posLabels = ["Не атаковал зеркало.\nЗеркало было закрыто", "Не атаковал зеркало", "Атаковал зеркало", "Уже сам закрыл зеркало"]

        starsArr = []
        stars = {i: 0 for i in starsLabels}
        THs = {i: 0 for i in THsLabels}
        pos = {i: 0 for i in posLabels}
        percents = []

        for attack in self.warData["warAttacks"]:
            starEnding = " звезды"
            if attack[9] == 1:
                starEnding = " звезда"
            elif attack[9] == 0:
                starEnding = " звезд"

            stars[str(attack[9]) + starEnding] += 1
            starsArr.append(attack[9])
            percents.append(attack[8])

            if attack[7] == 0:
                continue

            if attack[4] < attack[12]:
                THs[THsLabels[0]] += 1
            elif attack[4] > attack[12]:
                THs[THsLabels[1]] += 1
            else:
                THs[THsLabels[2]] += 1

            if attack[5] > attack[13] or attack[5] < attack[13]:
                isTaken, who = dataProceesing.getIfMirrorWasBeaten(self.lastSearchedClan["tag"], attack[1], attack[5], attack[14])
                if isTaken:
                    if who == self.selectedMember[1]:
                        pos[posLabels[3]] += 1
                    else:
                        pos[posLabels[0]] += 1
                else:
                    pos[posLabels[1]] += 1
            else:
                pos[posLabels[2]] += 1

        starsLabels = [i for i in starsLabels if stars[i] != 0]
        THsLabels = [i for i in THsLabels if THs[i] != 0]
        posLabels = [i for i in posLabels if pos[i] != 0]

        starsVals = numpy.array([stars[i] for i in starsLabels])
        THsVals = numpy.array([THs[i] for i in THsLabels])
        posVals = numpy.array([pos[i] for i in posLabels])

        customtkinter.CTkLabel(self.warFrame,
                               text=f"Средний процент в атаке {sum(percents) / len(percents)}",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.warFrame,
                               text=f"Средние звезды в атаке {sum(starsArr) / len(starsArr)}",
                               font=("Sans serif", 14)).pack()

        my_dpi = self.warFrame.winfo_fpixels('1i')
        starsFig = Figure(facecolor="#303030", figsize=(600 / my_dpi, 600 / my_dpi), dpi=my_dpi)
        starsPlot = starsFig.add_subplot(111)
        starsPlot.set_title('Атаки по звездам', color="white")

        THFig = Figure(facecolor="#303030", figsize=(600 / my_dpi, 600 / my_dpi), dpi=my_dpi)
        THsPlot = THFig.add_subplot(111)
        THsPlot.set_title('Атаки по тх защитника', color="white")

        posFig = Figure(facecolor="#303030", figsize=(600 / my_dpi, 600 / my_dpi), dpi=my_dpi)
        posPlot = posFig.add_subplot(111)
        posPlot.set_title('Атаки по позиции защитника', color="white")

        patches, texts, pcts = starsPlot.pie(starsVals, radius=0.6, labels=starsLabels, shadow=True,
                                             colors=plt.cm.Dark2.colors,
                                             autopct=lambda x: starsVals[
                                                 numpy.abs(starsVals - x / 100. * starsVals.sum()).argmin()])
        for i, patch in enumerate(patches):
            texts[i].set_color("white")

        patches, texts, pcts = THsPlot.pie(THsVals, radius=0.6, labels=THsLabels, shadow=True,
                                           colors=plt.cm.Dark2.colors,
                                           autopct=lambda x: THsVals[
                                               numpy.abs(THsVals - x / 100. * THsVals.sum()).argmin()])
        for i, patch in enumerate(patches):
            texts[i].set_color("white")

        patches, texts, pcts = posPlot.pie(posVals, radius=0.6, labels=posLabels, shadow=True,
                                           colors=plt.cm.Dark2.colors,
                                           autopct=lambda x: posVals[
                                               numpy.abs(posVals - x / 100. * posVals.sum()).argmin()],
                                           labeldistance=1.2)
        for i, patch in enumerate(patches):
            texts[i].set_color("white")

        chartStars = FigureCanvasTkAgg(starsFig, self.starTab)
        chartStars.get_tk_widget().pack(side=tkinter.LEFT)

        chartTHs = FigureCanvasTkAgg(THFig, self.ThsTab)
        chartTHs.get_tk_widget().pack(side=tkinter.LEFT)

        chartPos = FigureCanvasTkAgg(posFig, self.posTab)
        chartPos.get_tk_widget().pack(side=tkinter.LEFT)

        warAttacksFieldsFrame = customtkinter.CTkFrame(self.attacksTab)
        warAttacksFieldsFrame.pack(expand=True)

        searchOptions = [Option("wars", "Член клана", {"row": 0, "column": 0}, "label"),
                         Option("memberTownHall", "Тх", {"row": 1, "column": 0}, "entry"),
                         Option("mapPosition", "Позиция", {"row": 2, "column": 0}, "entry"),
                         Option("percent", "Проценты", {"row": 3, "column": 0}, "entry"),
                         Option("stars", "Звезды", {"row": 4, "column": 0}, "entry"),

                         Option("wars", "Член оппонента", {"row": 0, "column": 1}, "label"),
                         Option("defenderTownHall", "Тх оппонента", {"row": 1, "column": 1}, "entry"),
                         Option("defenderPosition", "Позиция оппонента", {"row": 2, "column": 1}, "entry"),

                         Option("wars", "Другое", {"row": 0, "column": 2}, "label"),
                         Option("attackNum", "Номер атаки", {"row": 1, "column": 2}, "entry"),
                         Option("attackOrder", "Порядковый номер атаки", {"row": 2, "column": 2}, "entry"),
                         Option("attacked", "Атаковал", {"row": 3, "column": 2}, "selector",
                                ["Не выбрано", "Атаковал", "Не атаковал"]),
                         Option("opponentTh", "Тх оппонента", {"row": 4, "column": 2}, "selector",
                                ["Не выбрано", "Атаковал равного", "Атаковал слабого", "Атаковал сильного"])]

        self.warAttacksFields = CustomQuery(self.root, warAttacksFieldsFrame, self.lastSearchedClan, searchOptions,
                                            "warAttacks", False)
        self.warAttacksFields.createEntries()

        updateButton = customtkinter.CTkButton(self.attacksTab, text="Обновить данные",
                                               command=lambda: self.loop.create_task(self.buildWarAttacksTree()))
        updateButton.pack(pady=20)


        names = ("Номер атаки", "Атаковал", "Процент", "Звезды", "ТХ", "ТХ оппонента", "Номер на кв",
                 "Номер на кв оппонента", "Атака на кв", "Тег оппонента", "Имя оппонента", "Тег клана", "Дата начала",
                 "Дата окончания")
        toSort = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
        self.warTree = TreeView.CustomTreeView(self.attacksTab, show="headings", names=names, toSort=toSort, height=7)
        self.warTree.pack(expand=True)

        self.warTree.tag_configure('3star', background='#006400')
        self.warTree.tag_configure('notFine', background='#b45f06')
        self.warTree.tag_configure('notMirror', background='#92000A')
        self.warTree.tag_configure('current', background='#4B0082')
        self.loop.create_task(self.buildWarAttacksTree())

    async def buildWarAttacksTree(self):
        loadingFrame = LoadingFrame(f"Поиск войн клана {self.lastSearchedClan['name']}", self.root, 4)
        loadingFrame.nextStep("Поиск информации по КВ")
        data = await self.loop.create_task(self.client.getWarInfo(self.lastSearchedClan["tag"]))
        loadingFrame.nextStep("Сохранение информации по КВ")
        dataProceesing.saveWarData(data)

        self.warTree.delete(*self.warTree.get_children())
        query = self.warAttacksFields.serch()
        data = dataProceesing.getMembersWarAttacksData(self.lastSearchedClan["tag"], self.selectedMember[1],query=query)

        loadingFrame.nextStep("Вывод информации по КВ")
        for attack in data.values():
            attackState = ""
            if datetime.datetime.strptime(attack["endTime"],
                                          "%Y-%m-%d %H:%M:%S") > datetime.datetime.utcnow() + datetime.timedelta(
                hours=1):
                attackState = "current"
            elif attack['mapPosition'] != attack['defenderPosition'] and not dataProceesing.getIfMirrorWasBeaten(
                    self.lastSearchedClan["tag"], attack['opponentTag'], attack["mapPosition"], attack["order"])[0]:
                attackState = "notMirror"
            elif attack["stars"] == 3:
                attackState = "3star"
            elif attack["stars"] <= 1 and attack['percent'] <= 85 or attack['percent'] <= 70:
                attackState = "notFine"
            self.warTree.insert("", tkinter.END,
                                values=[attack['attackNum'],
                                        attack['attacked'],
                                        attack['percent'], attack['stars'], attack['memberTownHall'],
                                        attack['defenderTownHall'],
                                        attack['mapPosition'], attack['defenderPosition'], attack["order"],
                                        attack['defenderTag'], attack['defenderName'], attack['opponentTag'],
                                        attack["startTime"], attack["endTime"]], tags=attackState)
        loadingFrame.close()

    def constructClanGamesFrame(self):
        for child in self.clanGamesFrame.winfo_children():
            child.destroy()

        customtkinter.CTkLabel(self.clanGamesFrame,
                               text=f"{self.selectedMember[0]}",
                               font=("Sans serif", 32)).pack()
        customtkinter.CTkLabel(self.clanGamesFrame,
                               text=f"Был в {self.clanGamesData['count']} игр клана",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.clanGamesFrame,
                               text=f"Средние медали за игру {self.clanGamesData['avg']}",
                               font=("Sans serif", 14)).pack()

        clanGamesMembersFieldsFrame = customtkinter.CTkFrame(self.clanGamesFrame)
        clanGamesMembersFieldsFrame.pack(expand=True)

        searchOptions = [Option("wars", "Игры", {"row": 0, "column": 0}, "label"),
                         Option("earnedMedals", "Медали", {"row": 1, "column": 0}, "entry")]

        self.clanGamesMembersFields = CustomQuery(self.root, clanGamesMembersFieldsFrame, self.lastSearchedClan,
                                                  searchOptions,
                                                  "clanGamesMembers", False)
        self.clanGamesMembersFields.createEntries()

        updateButtton = customtkinter.CTkButton(self.clanGamesFrame, text="Обновить данные",
                                                command=lambda: self.buildClanGamesTree())
        updateButtton.pack()

        names = ("Дата начала", "Дата окончания", "Медали")
        toSort = (0, 1, 2)
        self.clanGamesTree = TreeView.CustomTreeView(self.clanGamesFrame, show="headings", names=names, toSort=toSort, height=7)
        self.clanGamesTree.pack(expand=True)

        self.clanGamesTree.tag_configure('4k', background='#006400')
        self.clanGamesTree.tag_configure('notFine', background='#b45f06')
        self.clanGamesTree.tag_configure('0', background='#92000A')
        self.clanGamesTree.tag_configure('current', background='#4B0082')
        self.buildClanGamesTree()

    def buildClanGamesTree(self):
        self.clanGamesTree.delete(*self.clanGamesTree.get_children())
        query = self.clanGamesMembersFields.serch()
        for game in dataProceesing.getClanGamesStat(self.lastSearchedClan['tag'], self.selectedMember[1],query=query)["games"].values():

            attackState = ""
            if datetime.datetime.strptime(game["end"],
                                          "%Y-%m-%d") > datetime.datetime.utcnow() + datetime.timedelta(
                hours=1):
                attackState = "current"
            elif game['earnedMedals'] == 4000:
                attackState = "4k"
            elif game['earnedMedals'] <= 600:
                attackState = "0"
            elif game['earnedMedals'] <= 1000:
                attackState = "notFine"
            self.clanGamesTree.insert("", tkinter.END,
                                values=[game['start'],
                                        game['end'],
                                        game['earnedMedals']], tags=attackState)

    def constructClanCapitalFrame(self):
        for child in self.clanCapitalFrame.winfo_children():
            child.destroy()

        customtkinter.CTkLabel(self.clanCapitalFrame,
                               text=f"{self.selectedMember[0]}",
                               font=("Sans serif", 32)).pack()
        customtkinter.CTkLabel(self.clanCapitalFrame,
                               text=f"Был в {self.clanCapitalData['count']} рейдах",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.clanCapitalFrame,
                               text=f"Среднее золото за рейды: {self.clanCapitalData['avgGold']}",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.clanCapitalFrame,
                               text=f"Среднее количество атака за рейды: {self.clanCapitalData['avgAttacks']}",
                               font=("Sans serif", 14)).pack()

        raidDetailsFieldsFrame = customtkinter.CTkFrame(self.clanCapitalFrame)
        raidDetailsFieldsFrame.pack(expand=True)

        searchOptions = [Option("wars", "Рейды", {"row": 0, "column": 0}, "label"),
                         Option("attacks", "Атаки", {"row": 1, "column": 0}, "entry"),
                         Option("lootedGold", "Золото столицы", {"row": 2, "column": 0}, "entry")]

        self.raidDetailsFields = CustomQuery(self.root, raidDetailsFieldsFrame, self.lastSearchedClan, searchOptions,
                                             "capitalRaidMembers", False)
        self.raidDetailsFields.createEntries()

        updateButtton = customtkinter.CTkButton(self.clanCapitalFrame, text="Обновить данные",
                                                command=lambda: self.loop.create_task(self.buildClanCapitalTree()))
        updateButtton.pack()

        names = ("Дата начала", "Дата окончания", "Атаки","Рейды")
        toSort = (0, 1, 2,3)
        self.clanCapitalTree = TreeView.CustomTreeView(self.clanCapitalFrame, show="headings", names=names, toSort=toSort, height=7)
        self.clanCapitalTree.pack(expand=True)

        self.clanCapitalTree.tag_configure('good', background='#006400')
        self.clanCapitalTree.tag_configure('notFine', background='#b45f06')
        self.clanCapitalTree.tag_configure('0attaks', background='#92000A')
        self.clanCapitalTree.tag_configure('current', background='#4B0082')
        self.loop.create_task(self.buildClanCapitalTree())

    async def buildClanCapitalTree(self):
        self.lastSearchedClan = settings.getSetting("lastSearchedClan")
        loadingFrame = LoadingFrame(f"Поиск Рейдов Столицы клана {self.lastSearchedClan['name']}", self.root, 10)
        loadingFrame.nextStep("Поиск информации по Столице")
        data = await self.loop.create_task(self.client.getCapitalRaids(self.lastSearchedClan["tag"]))
        loadingFrame.nextStep("Сохранение информации по Столице")
        dataProceesing.saveCapitalRaidData(data, self.lastSearchedClan["tag"])

        self.clanCapitalTree.delete(*self.clanCapitalTree.get_children())
        query = self.raidDetailsFields.serch()
        loadingFrame.nextStep("Вывод информации по Столице")
        for raid in dataProceesing.getClanCapitalStat(self.lastSearchedClan['tag'], self.selectedMember[1],query=query)["raids"].values():

            attackState = ""
            if datetime.datetime.strptime(raid["end"],
                                          "%Y-%m-%d") > datetime.datetime.utcnow() + datetime.timedelta(
                hours=1):
                attackState = "current"
            elif raid['attacks'] == 0:
                attackState = "0"
            elif raid['attacks'] < 6:
                attackState = "notFine"
            elif raid['attacks'] == 6:
                attackState = "good"

            self.clanCapitalTree.insert("", tkinter.END,
                                values=[raid['start'],
                                        raid['end'],
                                        raid['attacks'],
                                        raid['gold']], tags=attackState)
        loadingFrame.close()

    def constructGeneralFrame(self):
        for child in self.generalFrame.winfo_children():
            child.destroy()
        customtkinter.CTkLabel(self.generalFrame,
                               text=f"{self.selectedMember[0]}",
                               font=("Sans serif", 32)).pack()
        customtkinter.CTkLabel(self.generalFrame,
                               text=f"Тег {self.selectedMember[1]}",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.generalFrame,
                               text=f"Состоит в клане {self.lastSearchedClan['name']}, {self.lastSearchedClan['tag']}. В должности: {self.selectedMember[4]}",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.generalFrame,
                               text=f"{self.selectedMember[2]} уровень ТХ. {self.selectedMember[3]} уровень аккаунта",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.generalFrame,
                               text=f"Задонатил {self.selectedMember[5]}. Получил {self.selectedMember[6]}. Соотношение {self.selectedMember[7]}",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.generalFrame,
                               text=f"Трофеии {self.selectedMember[8]}. Лига {self.selectedMember[9]}",
                               font=("Sans serif", 14)).pack()
        customtkinter.CTkLabel(self.generalFrame,
                               text=f"Трофеии строителя {self.selectedMember[10]}. Лига строителя {self.selectedMember[11]}",
                               font=("Sans serif", 14)).pack()

        customtkinter.CTkLabel(self.generalFrame,
                               text=f"Описание",
                               font=("Sans serif", 14)).pack(pady=40)

        self.descriptionTextbox = customtkinter.CTkTextbox(self.generalFrame,width=800,height=400)
        self.descriptionTextbox.pack()
        self.descriptionTextbox.after(10, self.descriptionTextbox.focus_set)

        self.descriptionTextbox.insert("0.0",dataProceesing.getDescriptionToMember(self.selectedMember[1]))
        customtkinter.CTkButton(self.generalFrame,text="Сохранить",command=lambda :dataProceesing.addDescriptionToMember(self.selectedMember[1],self.descriptionTextbox.get("0.0", "end"))).pack(pady=10)


    def show(self, member):
        self.analyticsFrame.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.CENTER)
        self.selectedMember = member["values"]

        self.warData = dataProceesing.getWarAttackCountStat(self.lastSearchedClan['tag'], self.selectedMember[1])
        self.clanGamesData = dataProceesing.getClanGamesStat(self.lastSearchedClan['tag'], self.selectedMember[1])
        self.clanCapitalData = dataProceesing.getClanCapitalStat(self.lastSearchedClan['tag'], self.selectedMember[1])

        self.constructGeneralFrame()
        self.constructWarFrame()
        self.constructClanGamesFrame()
        self.constructClanCapitalFrame()

        self.changeFrame("general")

    def createTabs(self):
        self.tabsFrame = customtkinter.CTkFrame(self.analyticsFrame, corner_radius=0, height=720, width=100)
        self.tabsFrame.place(x=0, rely=0.5, relheight=1, anchor=customtkinter.W)
        self.tabsFrame.pack_propagate(0)

        self.generalButton = SeamlessButton(self.tabsFrame, text="Общее", command=lambda: self.changeFrame("general"))
        self.generalButton.pack()

        self.warButton = SeamlessButton(self.tabsFrame, text="Войны", command=lambda: self.changeFrame("war"))
        self.warButton.pack()

        self.clanGamesButton = SeamlessButton(self.tabsFrame, text="Игры", command=lambda: self.changeFrame("CG"))
        self.clanGamesButton.pack()

        self.clanCapitalButton = SeamlessButton(self.tabsFrame, text="Столица",
                                                command=lambda: self.changeFrame("CC"))
        self.clanCapitalButton.pack()

    def changeFrame(self, name):

        self.generalButton.configure(fg_color=("gray75", "gray25") if name == "general" else "transparent")
        self.warButton.configure(fg_color=("gray75", "gray25") if name == "war" else "transparent")
        self.clanGamesButton.configure(fg_color=("gray75", "gray25") if name == "CG" else "transparent")
        self.clanCapitalButton.configure(fg_color=("gray75", "gray25") if name == "CC" else "transparent")

        if name == "general":
            self.generalFrame.place(x=100, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.W)
        else:
            self.generalFrame.place_forget()

        if name == "war":
            self.warFrame.place(x=100, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.W)
        else:
            self.closeFieldFrames(self.warAttacksFields)
            self.warFrame.place_forget()

        if name == "CG":
            self.clanGamesFrame.place(x=100, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.W)
        else:
            self.closeFieldFrames(self.clanGamesMembersFields)
            self.clanGamesFrame.place_forget()

        if name == "CC":
            self.clanCapitalFrame.place(x=100, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.W)
        else:
            self.closeFieldFrames(self.raidDetailsFields)
            self.clanCapitalFrame.place_forget()

    def closeFieldFrames(self, frame):
        try:
            frame.calFrame.destroy()
        except:
            pass
        try:
            frame.optionsFrame.destroy()
        except:
            pass