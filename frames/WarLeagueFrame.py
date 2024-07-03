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


class WarLeagueFrame:
    def __init__(self, client,root,style,loop):
        self.root = root
        self.style = style
        self.loop = loop
        self.warLeagueFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))

        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        self.frameName = customtkinter.CTkLabel(self.warLeagueFrame, text=f"ЛКВ клана {self.lastSearchedClan['name']}",
                               font=("Sans serif", 32))
        self.frameName.pack(pady=10)
        updateButtton = customtkinter.CTkButton(self.warLeagueFrame, text="Обновить данные",
                                                command=lambda: self.loop.create_task(self.updateData()))
        updateButtton.pack(pady=15)

        self.client = client

        self.leagueData = dataProceesing.getLeagueWarData(self.lastSearchedClan["tag"])

        names = ("Сезон", "1 раунд", "2 раунд", "3 раунд", "4 раунд", "5 раунд", "6 раунд", "7 раунд")
        toSort = (0,0)
        self.warLeagueTree = CustomTreeView(self.warLeagueFrame, show="headings", names=names, toSort=toSort)
        self.warLeagueTree.bind("<Double-1>", self.createWarFrame)
        self.warLeagueTree.pack()
        self.warLeagueTree.tag_configure('current', background='#4B0082')

        if self.leagueData != {}:
            self.buildLeagueWarsTree()

    def buildLeagueWarsTree(self):
        today = datetime.datetime.today()
        datem = datetime.datetime(today.year, today.month, 1)
        for season, warLeague in self.leagueData.items():
            tag = ""
            if datetime.datetime.strptime(season,"%Y-%m") == datem:
                tag = "current"
            self.warLeagueTree.insert("", tkinter.END,
                                      values=[season, warLeague['1CW']["name"], warLeague['2CW']["name"],
                                              warLeague['3CW']["name"], warLeague['4CW']["name"],
                                              warLeague['5CW']["name"],
                                              warLeague['6CW']["name"], warLeague['7CW']["name"]],tags=tag)

    def createWarFrame(self, event):
        if self.warLeagueTree.identify("region", event.x, event.y) != "cell":
            return
        for selection in self.warLeagueTree.selection():
            item = self.warLeagueTree.item(selection)
            season = item["values"][0]
            self.opponentTags = [i["tag"] for i in self.leagueData[season].values()]
        try:
            self.opponentTags
        except:
            return

        self.warFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))
        self.showWars()

        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        customtkinter.CTkLabel(self.warFrame, text=f"ЛКВ клана {self.lastSearchedClan['name']} за {season}",
                               font=("Sans serif", 32)).pack(pady=10)

        updateButtton = customtkinter.CTkButton(self.warFrame, text="Обновить данные",
                                                command=lambda: self.loop.create_task(self.updateData()))
        updateButtton.pack()

        self.warData = dataProceesing.getWarsData(self.lastSearchedClan["tag"], self.opponentTags)

        tabs = customtkinter.CTkTabview(self.warFrame)
        tabs.pack()
        warsTab = tabs.add("По войнам")
        attacksTab = tabs.add("По атакам")
        names = ("Тег оппонента", "Имя оппонента", "Звезды клана", "Атаки клана", "Процент клана", "Звезды оппонента",
                 "Атаки оппонента", "Процент оппонента", "Размер команд", "Дата начала (UTC+0)",
                 "Дата окончания (UTC+0)")
        toSort = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        self.warTree = CustomTreeView(warsTab, show="headings", names=names, toSort=toSort,height=7)
        self.warTree.bind("<Double-1>", self.createWarDetailsFrame)
        self.warTree.pack(expand=True)

        self.warTree.tag_configure('win', background='#006400')
        self.warTree.tag_configure('loose', background='#92000A')
        self.warTree.tag_configure('current', background='#4B0082')

        if self.warData != {}:
            self.buildWarsTree()

        self.attacksSummaryData = dataProceesing.getAttacksSummaryData(self.lastSearchedClan["tag"], self.opponentTags)
        names = ("Имя", "1 раунд", "2 раунд", "3 раунд", "4 раунд", "5 раунд",
                 "6 раунд", "7 раунд", "Средние звезды", "Средние проценты")
        toSort = (0, 8, 9,)
        self.attacksSummaryTree = CustomTreeView(attacksTab, show="headings", names=names, toSort=toSort,height=7)
        self.attacksSummaryTree.pack(expand=True)

        if self.attacksSummaryData != {}:
            self.buildAttacksSummaryTree()

        exitButton = customtkinter.CTkButton(self.warFrame, text="Назад", command=lambda: self.closeWar())
        exitButton.pack(pady=10)

    def buildWarsTree(self):
        for war in self.warData.values():
            warState = "none"
            if datetime.datetime.strptime(war["endDate"],
                                          "%Y-%m-%d %H:%M:%S") > datetime.datetime.utcnow() + datetime.timedelta(
                hours=1):
                warState = "current"
            elif war["clanStars"] > war["opponentStars"] or (
                    (war["clanStars"] == war["opponentStars"]) and (war["clanPercent"] > war["opponentPercent"])):
                warState = "win"
            elif war["clanStars"] < war["opponentStars"] or (
                    (war["clanStars"] == war["opponentStars"]) and (war["clanPercent"] < war["opponentPercent"])):
                warState = "loose"
            self.warTree.insert("", tkinter.END,
                                values=[war['opponentTag'], war['opponentName'], war['clanStars'], war['clanAttacks'],
                                        war['clanPercent'], war['opponentStars'], war['opponentAttacks'],
                                        war['opponentPercent'],
                                        war['teamSize'], war['startDate'], war['endDate']], tags=warState)

    def buildAttacksSummaryTree(self):
        for member, war in self.attacksSummaryData.items():
            avgStars = []
            avgPercents = []
            resList = [member]
            for summary in war.values():
                if summary["wasNot"]:
                    resStr = "Не было"
                    resList.append(resStr)
                    continue

                if not summary["attacked"]:
                    resStr = "Не атаковал"
                else:
                    resStr = f"Звезды: {summary['stars']}.\n" \
                             f"Процент: {summary['percent']}.\n" \
                             f"{summary['isTh']}.\n" \
                             f"{summary['isMirror']}."
                avgStars.append(summary['stars'])
                avgPercents.append(summary['percent'])
                resList.append(resStr)

            if len(avgStars) != 0:
                resList.append(round(sum(avgStars) / len(avgStars),2))
            else:
                resList.append(0)
            if len(avgPercents):
                resList.append(round(sum(avgPercents) / len(avgPercents),2))
            else:
                resList.append(0)
            self.attacksSummaryTree.insert("", tkinter.END,
                                           values=resList)

    async def updateData(self,loadingFrame=None):
        self.lastSearchedClan = settings.getSetting("lastSearchedClan")
        closeLoadingFrame = False
        if loadingFrame is None:
            closeLoadingFrame = True
            loadingFrame=LoadingFrame(f"Поиск ЛКВ клана {self.lastSearchedClan['name']}",self.root,12)
            loadingFrame.nextStep("Поиск информации по ЛКВ")
            CWL = await self.loop.create_task(self.client.getWarLeagueInfo(self.lastSearchedClan["tag"]))
            loadingFrame.nextStep("Сохранение информации по ЛКВ")
            if CWL:
                await self.loop.create_task(
                    dataProceesing.saveLeagueWarData(CWL[0], CWL[1], self.lastSearchedClan["tag"],self.client))


        self.frameName.configure(text=f"ЛКВ клана {self.lastSearchedClan['name']}")

        self.leagueData = dataProceesing.getLeagueWarData(self.lastSearchedClan["tag"])
        self.warLeagueTree.delete(*self.warLeagueTree.get_children())
        loadingFrame.nextStep("Вывод информации по ЛКВ")
        self.buildLeagueWarsTree()
        try:
            loadingFrame.nextStep("Получение информации по КВ")
            self.warData = dataProceesing.getWarsData(self.lastSearchedClan["tag"], self.opponentTags)
            self.warTree.delete(*self.warTree.get_children())
            loadingFrame.nextStep("Вывод информации по КВ")
            self.buildWarsTree()

            loadingFrame.nextStep("Получение информации по атакам за ЛКВ")
            self.attacksSummaryData = dataProceesing.getAttacksSummaryData(self.lastSearchedClan["tag"],
                                                                           self.opponentTags)
            self.attacksSummaryTree.delete(*self.attacksSummaryTree.get_children())
            loadingFrame.nextStep("Вывод информации по атакам за ЛКВ")
            self.buildAttacksSummaryTree()
        except:
            pass

        try:
            query = self.warAttacksFields.serch()
            loadingFrame.nextStep("Получение информации по атакам за КВ")
            self.warDetailsData = dataProceesing.getWarAttacksData(self.lastSearchedClan["tag"], self.opponentTag,query=query)
            self.warDetailsTree.delete(*self.warDetailsTree.get_children())
            loadingFrame.nextStep("Вывод информации по атакам за КВ")
            self.buildWarDetailsTree()
        except:
            pass
        if closeLoadingFrame: loadingFrame.close()

    def showLeaguesWars(self):
        self.warLeagueFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

    def showWars(self):
        self.warFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)
        self.style.configure('Treeview', rowheight=90)

    def createWarDetailsFrame(self, event):
        for selection in self.warTree.selection():
            item = self.warTree.item(selection)
            self.opponentTag, self.opponentName = item["values"][0:2]
        try:
            self.opponentTag
        except:
            return

        self.style.configure('Treeview', rowheight=25)

        self.warDetailsFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))
        self.warDetailsFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

        lastSearchedClan = settings.getSetting("lastSearchedClan")

        customtkinter.CTkLabel(self.warDetailsFrame,
                               text=f"Война клана {lastSearchedClan['name']} с кланом {self.opponentName}",
                               font=("Sans serif", 32)).pack(pady=10)

        warAttacksFieldsFrame = customtkinter.CTkFrame(self.warDetailsFrame)
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

        updateButtton = customtkinter.CTkButton(self.warDetailsFrame, text="Обновить данные",
                                                command=lambda: self.loop.create_task(self.updateData()))
        updateButtton.pack()
        self.warDetailsData = dataProceesing.getWarAttacksData(lastSearchedClan['tag'], self.opponentTag)

        names = ("Тег", "Имя", "Номер атаки", "Атаковал", "Процент", "Звезды", "ТХ", "ТХ оппонента", "Номер на кв",
                 "Номер на кв оппонента", "Атака на кв", "Тег оппонента", "Имя оппонента")
        toSort = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        self.warDetailsTree = CustomTreeView(self.warDetailsFrame, show="headings", names=names, toSort=toSort)
        self.warDetailsTree.pack(expand=True)

        self.warDetailsTree.tag_configure('3star', background='#006400')
        self.warDetailsTree.tag_configure('notFine', background='#b45f06')
        self.warDetailsTree.tag_configure('notMirror', background='#92000A')

        exitButton = customtkinter.CTkButton(self.warDetailsFrame, text="Назад", command=lambda: self.closeWarDetails())
        exitButton.pack(pady=10)

        self.buildWarDetailsTree()

    def closeWar(self):
        try:
            self.warFrame.destroy()
        except:
            pass

        self.style.configure('Treeview', rowheight=25)

    def closeWarDetails(self):
        try:
            self.warAttacksFields.calFrame.destroy()
        except:
            pass
        try:
            self.warAttacksFields.optionsFrame.destroy()
        except:
            pass
        try:
            self.warDetailsFrame.destroy()
        except:
            pass
        self.style.configure('Treeview', rowheight=90)


    def buildWarDetailsTree(self):
        for attack in self.warDetailsData.values():
            attackState = "notMirror"
            if attack['mapPosition'] != attack['defenderPosition'] and not \
                    dataProceesing.getIfMirrorWasBeaten(self.lastSearchedClan["tag"], self.opponentTag,
                                                        attack["mapPosition"],
                                                        attack["order"])[0]:
                attackState = "notMirror"
            elif attack["stars"] == 3:
                attackState = "3star"
            elif attack["stars"] <= 1 and attack['percent'] <= 85 or attack['percent'] <= 70:
                attackState = "notFine"

            self.warDetailsTree.insert("", tkinter.END,
                                       values=[attack['memberTag'], attack['memberName'], attack['attackNum'],
                                               attack['attacked'],
                                               attack['percent'], attack['stars'], attack['memberTownHall'],
                                               attack['defenderTownHall'],
                                               attack['mapPosition'], attack['defenderPosition'], attack["order"],
                                               attack['defenderTag'], attack['defenderName']],tags=attackState)