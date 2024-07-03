import asyncio
import datetime
import tkinter
from tkinter import ttk

import customtkinter

import dataProceesing
import settings
from CustomQuery import CustomQuery, Option
from TreeView import CustomTreeView
from frames.LoadingFrame import LoadingFrame


class WarFrame:
    def __init__(self, client, root,loop):
        self.root = root
        self.loop = loop
        self.warFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))

        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        self.frameName = customtkinter.CTkLabel(self.warFrame, text=f"Войны клана {self.lastSearchedClan['name']}", font=("Sans serif", 32))
        self.frameName.pack(pady=10)

        warFieldsFrame = customtkinter.CTkFrame(self.warFrame)
        warFieldsFrame.pack(expand=True)

        searchOptions = [Option("wars", "Клан", {"row": 0, "column": 0}, "label"),
                         Option("clanStars", "Звезды клана", {"row": 1, "column": 0}, "entry"),
                         Option("clanAttacks", "Атаки клана", {"row": 2, "column": 0}, "entry"),
                         Option("clanPercent", "Проценты клана", {"row": 3, "column": 0}, "entry"),
                         Option("teamSize", "Размер команд", {"row": 4, "column": 0}, "entry"),

                         Option("wars", "Оппонент", {"row": 0, "column": 1}, "label"),
                         Option("opponentStars", "Звезды оппонента", {"row": 1, "column": 1}, "entry"),
                         Option("opponentAttacks", "Атаки оппонента", {"row": 2, "column": 1}, "entry"),
                         Option("opponentPercent", "Проценты оппонента", {"row": 3, "column": 1}, "entry"),

                         Option("wars", "Другое", {"row": 0, "column": 2}, "label"),
                         Option("warResult", "Итог", {"row": 1, "column": 2}, "selector",
                                ["Не выбрано", "Победа", "Поражение", "Ничья"])]

        self.warFields = CustomQuery(self.root, warFieldsFrame, self.lastSearchedClan, searchOptions, "wars")
        self.warFields.createEntries()

        updateButtton = customtkinter.CTkButton(self.warFrame, text="Обновить данные",
                                                command=lambda: self.loop.create_task(self.updateData()))
        updateButtton.pack()

        self.client = client

        self.warData = dataProceesing.getWarsData(self.lastSearchedClan["tag"])

        names = ("Тег оппонента", "Имя оппонента", "Звезды клана", "Атаки клана", "Процент клана", "Звезды оппонента",
                 "Атаки оппонента", "Процент оппонента", "Размер команд", "Дата начала (UTC+0)",
                 "Дата окончания (UTC+0)")
        toSort = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
        self.warTree = CustomTreeView(self.warFrame, show="headings", names=names, toSort=toSort)
        self.warTree.bind("<Double-1>", self.createWarDetailsFrame)

        self.warTree.tag_configure('win', background='#006400')
        self.warTree.tag_configure('loose', background='#92000A')
        self.warTree.tag_configure('current', background='#4B0082')

        ysb = ttk.Scrollbar(self.warFrame, orient=tkinter.VERTICAL, command=self.warTree.yview)
        self.warTree.configure(yscroll=ysb.set)
        self.warTree.pack(expand=True)
        if self.warData != {}:
            self.buildWarsTree()

    async def updateData(self,loadingFrame=None):
        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        closeLoadingFrame = False
        if loadingFrame is None:
            closeLoadingFrame = True
            loadingFrame=LoadingFrame(f"Поиск войн клана {self.lastSearchedClan['name']}",self.root,10)
            loadingFrame.nextStep("Поиск информации по КВ")
            data = await self.loop.create_task(self.client.getWarInfo(self.lastSearchedClan["tag"]))
            loadingFrame.nextStep("Сохранение информации по КВ")
            dataProceesing.saveWarData(data)

        self.frameName.configure(text=f"Войны клана {self.lastSearchedClan['name']}", font=("Sans serif", 32))
        query = self.warFields.serch()
        loadingFrame.nextStep("Применение выборки по КВ")
        self.warData = dataProceesing.getWarsData(self.lastSearchedClan["tag"], query=query)
        self.warTree.delete(*self.warTree.get_children())
        loadingFrame.nextStep("Вывод информации по кв")
        self.buildWarsTree()
        try:
            loadingFrame.nextStep(f"Применение выборки по атакам на КВ против {self.opponentTag}")
            query = self.warAttacksFields.serch()
            self.warDetailsData = dataProceesing.getWarAttacksData(self.lastSearchedClan["tag"], self.opponentTag,query=query)
            self.warDetailsTree.delete(*self.warDetailsTree.get_children())
            loadingFrame.nextStep(f"ПВывод информации по атакам на КВ против {self.opponentTag}")
            self.buildWarDetailsTree()
        except:
            pass
        if closeLoadingFrame: loadingFrame.close()

    def show(self):
        self.warFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

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

    def createWarDetailsFrame(self, event):
        if self.warTree.identify("region", event.x, event.y) != "cell":
            return
        for selection in self.warTree.selection():
            item = self.warTree.item(selection)
            self.opponentTag, self.opponentName = item["values"][0:2]
        try:
            self.opponentTag
        except:
            return

        self.warDetailsFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))
        self.warDetailsFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

        lastSearchedClan = settings.getSetting("lastSearchedClan")


        customtkinter.CTkLabel(self.warDetailsFrame, text=f"Война клана {lastSearchedClan['name']} с кланом {self.opponentName}", font=("Sans serif", 32)).pack(pady=10)

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
                                ["Не выбрано", "Атаковал равного", "Атаковал слабого", "Атаковал сильного"])
                         ]
# Option("mirror", "Зеркало", {"row": 5, "column": 2}, "selector",
# ["Не выбрано", "Атаковал Зеркало", "Не атаковал зеркало", "Зеркало было атаковано",
# "Сам забрал зеркало"])
        self.warAttacksFields = CustomQuery(self.root, warAttacksFieldsFrame, self.lastSearchedClan, searchOptions,
                                            "warAttacks",False)
        self.warAttacksFields.createEntries()

        updateButton = customtkinter.CTkButton(self.warDetailsFrame, text="Обновить данные",
                                               command=lambda: self.loop.create_task(self.updateData()))
        updateButton.pack()

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
        exitButton.pack(pady=15)

        self.buildWarDetailsTree()

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

    def buildWarDetailsTree(self):
        for attack in self.warDetailsData.values():
            attackState = ""
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
                                               attack['defenderTag'], attack['defenderName']], tags=attackState)

