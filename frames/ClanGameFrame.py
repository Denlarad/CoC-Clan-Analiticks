import asyncio
import datetime
import sqlite3
import tkinter
from tkinter import ttk

import customtkinter
from tkcalendar import Calendar

import dataProceesing
import settings
from CustomQuery import Option, CustomQuery
from TreeView import CustomTreeView


class ClanGamesFrame:
    def __init__(self, client, root):
        self.root = root
        self.clanGamesFrame = customtkinter.CTkFrame(self.root, width=1280, height=720, fg_color=("gray75", "gray25"))

        self.lastSearchedClan = settings.getSetting("lastSearchedClan")

        self.frameName = customtkinter.CTkLabel(self.clanGamesFrame, text=f"Игры клана {self.lastSearchedClan['name']}",
                               font=("Sans serif", 32))
        self.frameName.pack(pady=10)

        clanGamesFieldsFrame = customtkinter.CTkFrame(self.clanGamesFrame)
        clanGamesFieldsFrame.pack(expand=True)

        searchOptions = [Option("wars", "Игры", {"row": 0, "column": 0}, "label"),
                         Option("earnedTier", "Уровень награды", {"row": 1, "column": 0}, "entry"),
                         Option("earnedMedals", "Медали", {"row": 2, "column": 0}, "entry")]

        self.clanGamesFields = CustomQuery(self.root, clanGamesFieldsFrame, self.lastSearchedClan, searchOptions,
                                           "clanGames")
        self.clanGamesFields.createEntries()

        updateButtton = customtkinter.CTkButton(self.clanGamesFrame, text="Подтвердить выборку",
                                                command=lambda: self.updateData())
        updateButtton.pack()

        self.client = client

        self.clanGamesData = dataProceesing.getClanGamesData(self.lastSearchedClan["tag"])

        names = ("Дата начала (UTC+0)", "Дата окончания (UTC+0)", "Уровень награды", "Медали")
        toSort = (0, 1, 2, 3)
        self.clanGamesTree = CustomTreeView(self.clanGamesFrame, show="headings", names=names, toSort=toSort)
        self.clanGamesTree.bind("<Double-1>", self.createClanGamesMembersFrame)
        self.clanGamesTree.pack(expand=True)

        self.clanGamesTree.tag_configure('6lvl', background='#006400')
        self.clanGamesTree.tag_configure('highLvl', background='#b45f06')
        self.clanGamesTree.tag_configure('lowLvl', background='#92000A')
        self.clanGamesTree.tag_configure('current', background='#4B0082')
        if self.clanGamesData != {}:
            self.builClanGamesTree()

        self.clanGamesErrorLabel = customtkinter.CTkLabel(self.clanGamesFrame,text="",text_color="red")
        self.clanGamesErrorLabel.pack()

        addClanGamesMembersDataButton = customtkinter.CTkButton(self.clanGamesFrame, text="Добавить данные",
                                                                command=lambda: self.manualClanGamesData())
        addClanGamesMembersDataButton.pack(pady=10)
        addClanGamesMembersDataButton = customtkinter.CTkButton(self.clanGamesFrame, text="Изменить данные",
                                                                command=lambda: self.manualClanGamesData(update=True))
        addClanGamesMembersDataButton.pack()
        addClanGamesMembersDataButton = customtkinter.CTkButton(self.clanGamesFrame, text="Удалить данные",
                                                                command=lambda: self.deleteClanGame())
        addClanGamesMembersDataButton.pack(pady=10)

    def selectTime(self, option):
        try:
            self.calFrame.destroy()
        except:
            pass
        self.calFrame = customtkinter.CTkFrame(self.root, border_color="white", border_width=1)
        self.calFrame.place(relx=0.5, rely=0.4, relwidth=0.2, relheight=0.4, anchor=customtkinter.CENTER)

        customtkinter.CTkLabel(self.calFrame, text=f"{option}").pack(pady=10)

        self.cal = Calendar(self.calFrame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.cal.pack(pady=10)

        selectBut = customtkinter.CTkButton(self.calFrame, text="Выбрать",
                                            command=lambda option=option: self.confirmTime(option))
        selectBut.pack(pady=10)

        selectBut = customtkinter.CTkButton(self.calFrame, text="Отмена",
                                            command=lambda: self.calFrame.destroy())
        selectBut.pack(pady=10)

    def confirmTime(self, option):
        if option == "Дата начала":
            self.startTimeEntry.delete(0, tkinter.END)
            self.startTimeEntry.insert(0, self.cal.get_date())
        else:
            self.endTimeEntry.delete(0, tkinter.END)
            self.endTimeEntry.insert(0, self.cal.get_date())

        self.calFrame.destroy()

    def manualClanGamesData(self, update=False):
        self.clanGamesErrorLabel.configure(text="")
        self.closeSubFrames()
        self.clanGamesDataFrame = customtkinter.CTkFrame(self.root, width=1280, height=720,
                                                         fg_color=("gray75", "gray25"), border_color="white",
                                                         border_width=1)
        self.clanGamesDataFrame.place(relx=0.5, rely=0.5, relwidth=0.2, relheight=0.55, anchor=customtkinter.CENTER)

        startTimeLablel = customtkinter.CTkLabel(self.clanGamesDataFrame, text="Дата начала (гггг-мм-дд)")
        startTimeLablel.pack(pady=5)

        self.startTimeEntry = customtkinter.CTkEntry(self.clanGamesDataFrame)
        self.startTimeEntry.pack()

        startBut = customtkinter.CTkButton(self.clanGamesDataFrame, text="Выбрать",
                                           command=lambda: self.selectTime("Дата начала"))
        startBut.pack(pady=10)

        endTimeLablel = customtkinter.CTkLabel(self.clanGamesDataFrame, text="Дата окончания (гггг-мм-дд)")
        endTimeLablel.pack(pady=5)

        self.endTimeEntry = customtkinter.CTkEntry(self.clanGamesDataFrame)
        self.endTimeEntry.pack(pady=10)

        endBut = customtkinter.CTkButton(self.clanGamesDataFrame, text="Выбрать",
                                         command=lambda: self.selectTime("Дата окончания"))
        endBut.pack()

        earnedTierLabel = customtkinter.CTkLabel(self.clanGamesDataFrame, text="Уровень награды")
        earnedTierLabel.pack(pady=5)

        self.earnedTierEntry = customtkinter.CTkEntry(self.clanGamesDataFrame)
        self.earnedTierEntry.pack()

        earnedMedalsLabel = customtkinter.CTkLabel(self.clanGamesDataFrame, text="Медали")
        earnedMedalsLabel.pack(pady=5)

        self.earnedMedalsEntry = customtkinter.CTkEntry(self.clanGamesDataFrame)
        self.earnedMedalsEntry.pack()

        addButton = customtkinter.CTkButton(self.clanGamesDataFrame, text="Добавить",
                                            command=lambda: self.saveClanGameData())
        addButton.pack(pady=10)

        cancelButton = customtkinter.CTkButton(self.clanGamesDataFrame, text="Отменить",
                                               command=lambda: self.closeClanGameData())
        cancelButton.pack()

        self.clanGameEntryErrorLabel = customtkinter.CTkLabel(self.clanGamesDataFrame,text="",text_color="red",wraplength=300)
        self.clanGameEntryErrorLabel.pack(pady=5)
        if update:
            for selection in self.clanGamesTree.selection():
                item = self.clanGamesTree.item(selection)
            try:
                self.startTimeEntry.delete(0, tkinter.END)
                self.startTimeEntry.insert(0, item["values"][0])

                self.endTimeEntry.delete(0, tkinter.END)
                self.endTimeEntry.insert(0, item["values"][1])

                self.earnedTierEntry.delete(0, tkinter.END)
                self.earnedTierEntry.insert(0, item["values"][2])

                self.earnedMedalsEntry.delete(0, tkinter.END)
                self.earnedMedalsEntry.insert(0, item["values"][3])
            except:
                self.clanGamesErrorLabel.configure(text="Не выбрана игра")
                self.closeClanGameData()
                return

    def deleteClanGame(self):
        self.clanGamesErrorLabel.configure(text="")
        self.closeSubFrames()
        self.removeClanGameFrame = customtkinter.CTkFrame(self.root, width=1280, height=720,
                                                          fg_color=("gray75", "gray25"), border_color="white",
                                                          border_width=1)
        self.removeClanGameFrame.place(relx=0.5, rely=0.5, relwidth=0.2, relheight=0.2, anchor=customtkinter.CENTER)

        for selection in self.clanGamesTree.selection():
            item = self.clanGamesTree.item(selection)
        try:
            customtkinter.CTkLabel(self.removeClanGameFrame,
                                   text=f"Удалить игру клана с {item['values'][0]} по {item['values'][1]}").pack(pady=10)
        except:
            self.clanGamesErrorLabel.configure(text="Не выбрана игра")
            self.closeClanGameDelete()
            return
        confirmButton = customtkinter.CTkButton(self.removeClanGameFrame, text="Удалить",
                                                command=lambda: self.confirmClanGameDelete(item['values'][0],
                                                                                           item['values'][1]))
        confirmButton.pack(pady=10)

        cancelButton = customtkinter.CTkButton(self.removeClanGameFrame, text="Отменить",
                                               command=lambda: self.closeClanGameDelete())
        cancelButton.pack()

    def confirmClanGameDelete(self, start, end):
        dataProceesing.deleteClanGameData(self.lastSearchedClan["tag"], start, end)
        self.updateData()
        self.closeClanGameDelete()

    def closeClanGameDelete(self):
        try:
            self.removeClanGameFrame.destroy()
        except:
            pass

    def saveClanGameData(self):
        self.clanGameEntryErrorLabel.configure(text="")
        error = ""
        try:
            datetime.date.fromisoformat(self.startTimeEntry.get())
        except:
            error += "Дата начала должна быть в формате (гггг-мм-дд)\n"
        try:
            datetime.date.fromisoformat(self.startTimeEntry.get())
        except:
            error += "Дата окончания должна быть в формате (гггг-мм-дд)\n"

        if not self.earnedTierEntry.get().isdigit():
            error += "Уровень награды должен быть числом\n"
        if not self.earnedTierEntry.get().isdigit():
            error += "Количество медалей должно быть числом\n"

        if error != "":
            self.clanGameEntryErrorLabel.configure(text=error)
            return
        resData = {"1": {"startTime": self.startTimeEntry.get(), "endTime": self.endTimeEntry.get(),
                         "earnedTier": self.earnedTierEntry.get(), "earnedMedals": self.earnedMedalsEntry.get()}}
        dataProceesing.saveClanGameData(resData, self.lastSearchedClan["tag"])

        self.updateData()
        self.closeClanGameData()

    def closeClanGameData(self):
        try:
            self.clanGamesDataFrame.place_forget()
        except:
            pass

    def manualClanGamesMemberData(self,update=False):
        self.clanGamesMemberErrorLabel.configure(text="")
        self.closeSubFrames()
        self.clanGamesDataMemberFrame = customtkinter.CTkFrame(self.root, width=1280, height=720,
                                                               fg_color=("gray75", "gray25"), border_color="white",
                                                               border_width=1)
        self.clanGamesDataMemberFrame.place(relx=0.5, rely=0.45, relwidth=0.2, relheight=0.3,
                                            anchor=customtkinter.CENTER)

        memberLabel = customtkinter.CTkLabel(self.clanGamesDataMemberFrame, text="Член клана")
        memberLabel.pack(pady=5)

        self.selectedMember = tkinter.StringVar(self.clanGamesDataMemberFrame)

        connection = sqlite3.connect('clanDatabase.db')
        cursor = connection.cursor()

        cursor.execute(
            f"select tag,name from members where clanTag = '{self.lastSearchedClan['tag']}'")

        options = []
        for i in cursor.fetchall():
            options.append(f"{i[0]},{i[1]}")
        connection.close()

        self.memberSelector = customtkinter.CTkOptionMenu(self.clanGamesDataMemberFrame, variable=self.selectedMember,
                                                          values=options)
        self.memberSelector.pack()

        membersEarnedMedalsLabel = customtkinter.CTkLabel(self.clanGamesDataMemberFrame, text="Медали")
        membersEarnedMedalsLabel.pack(pady=5)

        self.membersEarnedMedalsEntry = customtkinter.CTkEntry(self.clanGamesDataMemberFrame)
        self.membersEarnedMedalsEntry.pack()

        addButton = customtkinter.CTkButton(self.clanGamesDataMemberFrame, text="Добавить",
                                            command=lambda: self.saveClanGameMemberData())
        addButton.pack(pady=10)

        cancelButton = customtkinter.CTkButton(self.clanGamesDataMemberFrame, text="Отменить",
                                               command=lambda: self.closeClanGameMemberData())
        cancelButton.pack()

        self.clanGameMemberEntryErrorLabel = customtkinter.CTkLabel(self.clanGamesDataMemberFrame, text="", text_color="red",
                                                              wraplength=300)
        self.clanGameMemberEntryErrorLabel.pack(pady=5)
        if update:
            for selection in self.clanGamesMembersTree.selection():
                item = self.clanGamesMembersTree.item(selection)
            try:

                self.selectedMember.set(f"{item['values'][0]},{item['values'][1]}")

                self.membersEarnedMedalsEntry.delete(0, tkinter.END)
                self.membersEarnedMedalsEntry.insert(0, item["values"][2])
            except:
                self.clanGamesMemberErrorLabel.configure(text="Не выбран член клана")
                self.closeClanGameMemberData()
                return

    def saveClanGameMemberData(self):
        self.clanGameMemberEntryErrorLabel.configure(text="")
        error = ""
        try:
            tag, name = self.selectedMember.get().split(",")
        except:
            error += "Выберите члена клана\n"

        if not self.membersEarnedMedalsEntry.get().isdigit():
            error += "Количество медалей должно быть числом\n"

        if error != "":
            self.clanGameMemberEntryErrorLabel.configure(text=error)
            return

        resData = {"1": {"tag": tag, "name": name,
                         "earnedMedals": self.membersEarnedMedalsEntry.get(), "startTime": self.startTime,
                         "endTime": self.endTime}}
        dataProceesing.saveClanGameMemberData(resData, self.lastSearchedClan["tag"])
        self.updateData()
        self.closeClanGameMemberData()


    def deleteClanGameMember(self):
        self.clanGamesMemberErrorLabel.configure(text="")
        self.closeSubFrames()
        self.removeClanGameMemberFrame = customtkinter.CTkFrame(self.root, width=1280, height=720,
                                                          fg_color=("gray75", "gray25"), border_color="white",
                                                          border_width=1)
        self.removeClanGameMemberFrame.place(relx=0.5, rely=0.5, relwidth=0.2, relheight=0.2, anchor=customtkinter.CENTER)

        for selection in self.clanGamesMembersTree.selection():
            item = self.clanGamesMembersTree.item(selection)
        try:
            customtkinter.CTkLabel(self.removeClanGameMemberFrame,
                                   text=f"Удалить запись игру клана с {self.startTime} по {self.endTime} \n от игрока {item['values'][0]}").pack(pady=10)
        except:
            self.clanGamesMemberErrorLabel.configure(text="Не выбран член клана")
            self.closeClanGameMemberDelete()
            return
        confirmButton = customtkinter.CTkButton(self.removeClanGameMemberFrame, text="Удалить",
                                                command=lambda: self.confirmClanGameMemberDelete(self.startTime,self.endTime,item['values'][0]))
        confirmButton.pack(pady=10)

        cancelButton = customtkinter.CTkButton(self.removeClanGameMemberFrame, text="Отменить",
                                               command=lambda: self.closeClanGameMemberDelete())
        cancelButton.pack()


    def confirmClanGameMemberDelete(self, start, end,member):
        dataProceesing.deleteClanGameMemberData(self.lastSearchedClan["tag"], start, end,member)
        self.updateData()
        self.closeClanGameMemberDelete()

    def closeClanGameMemberDelete(self):
        try:
            self.removeClanGameMemberFrame.destroy()
        except:
            pass

    def closeClanGameMemberData(self):
        try:
            self.clanGamesDataMemberFrame.place_forget()
        except:
            pass

    def closeSubFrames(self):
        self.closeClanGameData()
        self.closeClanGameMemberData()
        self.closeClanGameDelete()
        self.closeClanGameMemberDelete()
        try:
            self.calFrame.destroy()
        except:
            pass

    def updateData(self):
        self.lastSearchedClan = settings.getSetting("lastSearchedClan")
        self.frameName.configure(text=f"Игры клана {self.lastSearchedClan['name']}")
        query = self.clanGamesFields.serch()
        self.clanGamesData = dataProceesing.getClanGamesData(self.lastSearchedClan["tag"], query=query)
        self.clanGamesTree.delete(*self.clanGamesTree.get_children())
        self.builClanGamesTree()
        try:
            query = self.clanGamesMembersFields.serch()
            self.clanGamesMembersData = dataProceesing.getClanGamesMembersData(self.lastSearchedClan['tag'],
                                                                               self.startTime, self.endTime,
                                                                               query=query)
            self.clanGamesMembersTree.delete(*self.clanGamesMembersTree.get_children())
            self.buildClanGamesMembersTree()
        except:
            pass

    def show(self):
        self.clanGamesFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

    def builClanGamesTree(self):
        for clanGame in self.clanGamesData.values():
            attackState = ""
            if datetime.datetime.strptime(clanGame["endTime"],
                                          "%Y-%m-%d") > datetime.datetime.utcnow() + datetime.timedelta(
                hours=1):
                attackState = "current"
            elif clanGame['earnedTier'] == 6:
                attackState = "6lvl"
            elif clanGame['earnedTier'] == 5:
                attackState = "highLvl"
            elif clanGame['earnedTier'] < 5:
                attackState = "lowLvl"
            self.clanGamesTree.insert("", tkinter.END,
                                      values=[clanGame['startTime'], clanGame['endTime'], clanGame['earnedTier'],
                                              clanGame['earnedMedals']], tags=attackState)

    def createClanGamesMembersFrame(self, event):
        if self.clanGamesTree.identify("region", event.x, event.y) != "cell":
            return
        for selection in self.clanGamesTree.selection():
            item = self.clanGamesTree.item(selection)
            self.startTime, self.endTime = item["values"][0:2]
        try:
            self.startTime
        except:
            return

        self.clanGamesMembersFrame = customtkinter.CTkFrame(self.root, width=1280, height=720,
                                                            fg_color=("gray75", "gray25"))
        self.clanGamesMembersFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

        lastSearchedClan = settings.getSetting("lastSearchedClan")

        customtkinter.CTkLabel(self.clanGamesMembersFrame,
                               text=f"Игра клана {self.lastSearchedClan['name']} с {self.endTime} по {self.endTime}",
                               font=("Sans serif", 32)).pack(pady=10)

        clanGamesMembersFieldsFrame = customtkinter.CTkFrame(self.clanGamesMembersFrame)
        clanGamesMembersFieldsFrame.pack(expand=True)

        searchOptions = [Option("wars", "Игры", {"row": 0, "column": 0}, "label"),
                         Option("earnedMedals", "Медали", {"row": 1, "column": 0}, "entry")]

        self.clanGamesMembersFields = CustomQuery(self.root, clanGamesMembersFieldsFrame, self.lastSearchedClan,
                                                  searchOptions,
                                                  "clanGamesMembers", False)
        self.clanGamesMembersFields.createEntries()

        updateButtton = customtkinter.CTkButton(self.clanGamesMembersFrame, text="Подтвердить выборку",
                                                command=lambda: self.updateData())
        updateButtton.pack(pady=10)
        self.clanGamesMembersData = dataProceesing.getClanGamesMembersData(lastSearchedClan['tag'], self.startTime,
                                                                           self.endTime)

        names = ("Тег", "Имя", "Медали")
        toSort = (0, 1, 2)
        self.clanGamesMembersTree = CustomTreeView(self.clanGamesMembersFrame, show="headings", names=names,
                                                   toSort=toSort)
        self.clanGamesMembersTree.pack(expand=True)

        self.clanGamesMembersTree.tag_configure('4k', background='#006400')
        self.clanGamesMembersTree.tag_configure('notFine', background='#b45f06')
        self.clanGamesMembersTree.tag_configure('0', background='#92000A')

        exitButton = customtkinter.CTkButton(self.clanGamesMembersFrame, text="Назад",
                                             command=lambda: self.closeClanGamesMembers())
        exitButton.pack()

        self.buildClanGamesMembersTree()

        self.clanGamesMemberErrorLabel = customtkinter.CTkLabel(self.clanGamesMembersFrame, text="", text_color="red")
        self.clanGamesMemberErrorLabel.pack()

        addClanGamesMembersDataButton = customtkinter.CTkButton(self.clanGamesMembersFrame, text="Добавить данные",
                                                                command=lambda: self.manualClanGamesMemberData())
        addClanGamesMembersDataButton.pack(pady=10)
        addClanGamesMembersDataButton = customtkinter.CTkButton(self.clanGamesMembersFrame, text="Изменить данные",
                                                                command=lambda: self.manualClanGamesMemberData(update=True))
        addClanGamesMembersDataButton.pack()
        addClanGamesMembersDataButton = customtkinter.CTkButton(self.clanGamesMembersFrame, text="Удалить данные",
                                                                command=lambda: self.deleteClanGameMember())
        addClanGamesMembersDataButton.pack(pady=10)


    def closeClanGamesMembers(self):
        try:
            self.clanGamesMembersFields.calFrame.destroy()
        except:
            pass
        try:
            self.clanGamesMembersFields.optionsFrame.destroy()
        except:
            pass
        try:
            self.clanGamesMembersFrame.destroy()
        except:
            pass

    def buildClanGamesMembersTree(self):
        for attack in self.clanGamesMembersData.values():
            attackState = ""
            if attack['earnedMedals'] == 4000:
                attackState = "4k"
            elif attack['earnedMedals'] <= 600:
                attackState = "0"
            elif attack['earnedMedals'] <= 1000:
                attackState = "notFine"
            self.clanGamesMembersTree.insert("", tkinter.END,
                                             values=[attack['tag'], attack['name'], attack['earnedMedals']],
                                             tags=attackState)
