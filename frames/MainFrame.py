import asyncio
import datetime
import sqlite3
import tkinter
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import customtkinter
import keyring

import requests

import dataProceesing
import settings
from SeamlessButton import SeamlessButton
from TreeView import CustomTreeView
from frames.AnaliticsFrame import AnalyticsFrame
from frames.CapitalFrame import CapitalFrame
from frames.ClanGameFrame import ClanGamesFrame
from frames.HelpFrame import HelpFrame
from frames.LoadingFrame import LoadingFrame
from frames.LoginFrame import LoginFrame
from frames.SearchFrame import SearchFrame
from frames.WarFrame import WarFrame
from frames.WarLeagueFrame import WarLeagueFrame


class MainFrame:
    # __init__ не дает использовать себя как async
    def __init__(self, root, style, loop):

        self.root = root
        self.mail = settings.getSetting("emailInUse")
        self.style = style
        self.loop = loop
        loop.create_task(self.update())

        self.helpFrame = customtkinter.CTkFrame(self.root,width=48, height=48,fg_color="transparent",corner_radius=10)
        self.helpFrame.pack_propagate(0)
        self.helpFrame.place(relx=0.97, rely=0.05,  anchor=customtkinter.CENTER)
        SeamlessButton(self.helpFrame, text="?",command=lambda :HelpFrame(self.root),font=("Sans serif", 32),anchor="c",border_width=2,corner_radius=10).pack()

        self.loginFrame = LoginFrame(root, self,self.loop)
        self.loginFrame.loginFrame.bind("<Destroy>", lambda event: self.closeLoop())

        if self.mail == "":
            self.loginFrame.show()
        else:
            self.startFrame = LoadingFrame("Загрузка", self.root, 12)
            loop.create_task(self.create())


    # Поскольку для tkinter и asyncio нужен loop но он может быть только 1, была сделана имитация root.mainloop() через loop от asyncio
    # Решение взято с https://stackoverflow.com/questions/47895765/use-asyncio-and-tkinter-or-another-gui-lib-together-without-freezing-the-gui
    async def update(self):
        while True:
            self.root.update()
            await asyncio.sleep(.1)

    def closeLoop(self):
        self.loop.stop()

    async def create(self, mail=None):

        if mail is not None: self.mail = mail
        self.helpFrame.configure(fg_color=("gray75", "gray25"))
        self.mainFrame = customtkinter.CTkFrame(self.root, fg_color=("gray75", "gray25"))
        self.createTabs()

        # self.mainFrame = customtkinter.CTkFrame(self.root, fg_color=("gray75", "gray25"))
        # self.mainFrame.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=customtkinter.CENTER)

        group1Frame = customtkinter.CTkFrame(self.mainFrame)
        group1Frame.pack(expand=True)

        controlFrame = customtkinter.CTkFrame(group1Frame)
        controlFrame.pack(side=tkinter.LEFT, expand=True, fill='y', padx=10, pady=10)

        infoFrame = customtkinter.CTkFrame(group1Frame)
        infoFrame.pack(side=tkinter.RIGHT, expand=True, fill='y', padx=10, pady=10)

        customtkinter.CTkLabel(controlFrame, text="Введите тег клана").pack(pady=10, padx=15)

        self.clanTagEntry = customtkinter.CTkEntry(controlFrame)
        self.clanTagEntry.pack()

        clanSearchButton = customtkinter.CTkButton(controlFrame, text="Найти клан")
        clanSearchButton.pack(pady=25)

        # Ничем не отличается от поиска но добавлена для удобства пользователю
        clanUpdateButton = customtkinter.CTkButton(controlFrame, text="Обновить данные")
        clanUpdateButton.pack()

        self.errorLable = customtkinter.CTkLabel(controlFrame, text="", wraplength=200, text_color="red")
        self.errorLable.pack(pady=25, padx=15)

        exitButton = customtkinter.CTkButton(controlFrame, text="Выйти",
                                             command=lambda: self.root.destroy())
        exitButton.pack(side=tkinter.BOTTOM, pady=25, padx=10)

        logoutButton = customtkinter.CTkButton(controlFrame, text="Выйти из аккаунта", command=lambda: self.logOut())
        logoutButton.pack(side=tkinter.BOTTOM, padx=10)

        dumpButton = customtkinter.CTkButton(controlFrame, text="Выгрузить информацию по клану",
                                             command=lambda: self.dumpDB())
        dumpButton.pack(side=tkinter.BOTTOM, pady=25, padx=10)

        loadButton = customtkinter.CTkButton(controlFrame, text="Загрузить информацию по клану",
                                             command=lambda: self.loadDB())
        loadButton.pack(side=tkinter.BOTTOM, padx=10)

        self.nameLable = customtkinter.CTkLabel(infoFrame, text="Клан", wraplength=500, font=("Sans serif", 32))
        self.nameLable.pack(pady=5, padx=15)

        self.resLable = customtkinter.CTkLabel(infoFrame, text="основная информация", wraplength=500)
        self.resLable.pack(pady=5, padx=15)
        self.client = requests.RequestClient()
        await self.loop.create_task(self.client.create(self.mail, keyring.get_password("OOOMEGALUL", self.mail)))

        tabs = customtkinter.CTkTabview(self.mainFrame)
        tabs.pack(expand=True)
        membersTab = tabs.add("Общее")
        attacksTab = tabs.add("Войны")

        names = (
            "Имя", "Тег", "Тх", "Уровень", "Роль в клане", "Задонатил", "Получил Доната", "Отдал:Получил", "Трофеи",
            "Лига",
            "Трофеи строителя", "Лига строителя")
        toSort = (0, 2, 3, 4, 5, 6, 7, 8, 10)

        self.tree = CustomTreeView(membersTab, show="headings", names=names, toSort=toSort)
        self.tree.bind("<Double-1>", lambda x: self.openMemberInfo(x))
        self.tree.pack(expand=True)

        clanSearchButton.bind("<Button-1>",lambda x: self.searchClan())
        self.clanTagEntry.bind("<Return>",lambda x: self.searchClan())
        clanUpdateButton.bind("<Button-1>",lambda x=True: self.searchClan(x))

        lastSearchedClan = settings.getSetting("lastSearchedClan")
        try:
            lastSearchedClan["tag"]
        except:
            lastSearchedClan = {"tag":"","name":""}
        names = ("Тег", "Имя", "Роль", "Провел атак", "Пропустил атаки", "Средние звезды",
                 "Средние проценты")
        toSort = (0, 1, 2, 3, 4, 5, 6)
        self.warsSummaryTree = CustomTreeView(attacksTab, show="headings", names=names, toSort=toSort)
        self.warsSummaryTree.pack(expand=True)

        try:
            self.warFrame = WarFrame(self.client, self.root, self.loop)
            self.leagueFrame = WarLeagueFrame(self.client, self.root, self.style, self.loop)
            self.capitalFrame = CapitalFrame(self.client, self.root, self.loop)
            self.analyticsFrame = AnalyticsFrame(self.client, self.root, self.loop)
            self.clanGamesFrame = ClanGamesFrame(self.client, self.root)
            self.searchFrame = SearchFrame(self.client, self.root)
        except sqlite3.OperationalError:
            dataProceesing.createDataBase()
            self.warFrame = WarFrame(self.client, self.root, self.loop)
            self.leagueFrame = WarLeagueFrame(self.client, self.root, self.style, self.loop)
            self.capitalFrame = CapitalFrame(self.client, self.root, self.loop)
            self.analyticsFrame = AnalyticsFrame(self.client, self.root, self.loop)
            self.clanGamesFrame = ClanGamesFrame(self.client, self.root)
            self.searchFrame = SearchFrame(self.client, self.root)

        try:
            self.startFrame.close()
        except:
            pass
        if lastSearchedClan["tag"] != "":
            self.clanTagEntry.delete(0, tkinter.END)
            self.clanTagEntry.insert(0, lastSearchedClan["tag"])
            clanData = dataProceesing.getClanData(lastSearchedClan["tag"])
            if clanData == {}:
                try:
                    dataProceesing.backupDatabase()
                except:
                    self.errorLable.configure(text="При сохранении бэкапа произошла ошибка")
                    pass
                self.searchClan()
            else:
                clanData["members"] = dataProceesing.getMembersData(lastSearchedClan["tag"])
                self.clanInfo = clanData
                self.buildInfo()
            self.summaryData = dataProceesing.getWarAttacksSummary(lastSearchedClan["tag"])
            if self.summaryData != {}:
                self.buildWarDetailsTree()
        self.lastSearchedClan = lastSearchedClan

        exitMemberInfoButton = customtkinter.CTkButton(self.analyticsFrame.tabsFrame, text="Назад",
                                                       command=lambda: self.closeMemberInfo())
        exitMemberInfoButton.pack(pady=40,padx=5)

        self.changeFrame("general")

    def dumpDB(self):
        confirmFrame = customtkinter.CTkFrame(self.root, border_color="white", border_width=1)
        confirmFrame.place(relx=0.5, rely=0.4, relwidth=0.2, relheight=0.1, anchor=customtkinter.CENTER)
        customtkinter.CTkLabel(confirmFrame,text=f"{dataProceesing.dumpDataBase()}").pack(pady=10,padx=1)
        customtkinter.CTkButton(confirmFrame,text="Ок",command=lambda :confirmFrame.destroy()).pack()

    def logOut(self):
        self.helpFrame.configure(fg_color="transparent")
        self.mainFrame.destroy()
        self.tabsFrame.destroy()
        settings.saveSetting("emailInUse", "")
        settings.saveSetting("lastSearchedClan", {"tag": "", "name": ""})
        self.loginFrame.show()

    def loadDB(self):
        confirmFrame = customtkinter.CTkFrame(self.root, border_color="white", border_width=1)
        customtkinter.CTkLabel(confirmFrame, text=f'{dataProceesing.loadDataBase(askopenfilename(filetypes=[("Выгрузка БД", ".db")]))}').pack(pady=10,
                                                                                                                padx=1)
        confirmFrame.place(relx=0.5, rely=0.4, relwidth=0.2, relheight=0.1, anchor=customtkinter.CENTER)
        customtkinter.CTkButton(confirmFrame, text="Ок", command=lambda: confirmFrame.destroy()).pack()

    def createTabs(self):
        self.tabsFrame = customtkinter.CTkFrame(self.root, corner_radius=0, height=720, width=100)
        self.tabsFrame.place(relx=0, rely=0.9, relheight=0.1, relwidth=1)

        self.generalButton = SeamlessButton(self.tabsFrame, text="Общее", anchor='center',
                                            command=lambda: self.changeFrame("general"))
        self.generalButton.pack(side=tkinter.LEFT, fill='both', expand=True)

        self.warButton = SeamlessButton(self.tabsFrame, text="Войны", anchor='center',
                                        command=lambda: self.changeFrame("war"))
        self.warButton.pack(side=tkinter.LEFT, fill='both', expand=True)

        self.warLeagueButton = SeamlessButton(self.tabsFrame, text="Лиги войн", anchor='center',
                                              command=lambda: self.changeFrame("warLeague"))
        self.warLeagueButton.pack(side=tkinter.LEFT, fill='both', expand=True)

        self.clanCapitalButton = SeamlessButton(self.tabsFrame, text="Столица", anchor='center',
                                                command=lambda: self.changeFrame("CC"))
        self.clanCapitalButton.pack(side=tkinter.LEFT, fill='both', expand=True)

        self.clanGamesButton = SeamlessButton(self.tabsFrame, text="Игры клана", anchor='center',
                                              command=lambda: self.changeFrame("CG"))
        self.clanGamesButton.pack(side=tkinter.LEFT, fill='both', expand=True)

        self.clanSearchButton = SeamlessButton(self.tabsFrame, text="Поиск по клану", anchor='center',
                                               command=lambda: self.changeFrame("search"))
        self.clanSearchButton.pack(side=tkinter.LEFT, fill='both', expand=True)

    def changeFrame(self, name):

        self.generalButton.configure(fg_color=("gray75", "gray25") if name == "general" else "transparent")
        self.warButton.configure(fg_color=("gray75", "gray25") if name == "war" else "transparent")
        self.warLeagueButton.configure(fg_color=("gray75", "gray25") if name == "warLeague" else "transparent")
        self.clanGamesButton.configure(fg_color=("gray75", "gray25") if name == "CG" else "transparent")
        self.clanCapitalButton.configure(fg_color=("gray75", "gray25") if name == "CC" else "transparent")
        self.clanSearchButton.configure(fg_color=("gray75", "gray25") if name == "search" else "transparent")

        if name == "general":
            self.openMainFrame()
        else:
            self.closeMainFrame()

        if name == "war":
            self.openWarLog()
        else:
            self.closeWarLog()

        if name == "warLeague":
            self.openLeagueWarLog()
        else:
            self.closeWarLeagueLog()

        if name == "CC":
            self.openCapitalLog()
        else:
            self.closeCapitalLog()

        if name == "CG":
            self.openClanGamesLog()
        else:
            self.closeClanGamesLog()

        if name == "search":
            self.openSearchFrame()
        else:
            self.closeSearchFrame()

        self.helpFrame.lift()

    def buildWarDetailsTree(self):
        for attack in self.summaryData.values():
            self.warsSummaryTree.insert("", tkinter.END,
                                        values=[attack['tag'], attack['name'], attack['role'],
                                                attack['attacks'],
                                                attack['missed'], round(attack['stars'], 2),
                                                round(attack['percents'], 2)])

    def closeClanGamesLog(self):
        self.clanGamesFrame.clanGamesFrame.place_forget()
        self.clanGamesFrame.closeClanGamesMembers()
        self.closeFieldFrames(self.clanGamesFrame.clanGamesFields)

    def closeWarLog(self):
        self.warFrame.warFrame.place_forget()
        self.warFrame.closeWarDetails()
        self.closeFieldFrames(self.warFrame.warFields)

    def closeWarLeagueLog(self):
        self.leagueFrame.warLeagueFrame.place_forget()
        self.leagueFrame.closeWarDetails()
        # Поскольку стиль общий для всего, и для показа информации по членам в ЛКВ нужно увеличивать высоту TreeView
        # После закрытия инфы по членам, возвращается обратно в нужную ширину в методах close()
        # И при закрытии отдельной инфы по кв она высота увеличивается
        # Поэтому, появляется баг, что если в данном методе вызывать последним closeWarDetails() то все TreeView будут высокими
        self.leagueFrame.closeWar()

    def closeCapitalLog(self):
        self.capitalFrame.capitalFrame.place_forget()
        self.capitalFrame.closeRaidDetails()
        self.closeFieldFrames(self.capitalFrame.capitalFields)

    def closeSearchFrame(self):
        self.searchFrame.searchFrame.place_forget()
        self.closeFieldFrames(self.searchFrame.fields)

    def closeMainFrame(self):
        self.mainFrame.place_forget()

    def closeMemberInfo(self):
        self.analyticsFrame.analyticsFrame.place_forget()
        self.closeFieldFrames(self.analyticsFrame.warAttacksFields)
        self.closeFieldFrames(self.analyticsFrame.raidDetailsFields)
        self.closeFieldFrames(self.analyticsFrame.clanGamesMembersFields)
        self.openMainFrame()

    def openMemberInfo(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            for selection in self.tree.selection():
                item = self.tree.item(selection)
            try:
                item
            except:
                return
            self.mainFrame.place_forget()
            self.analyticsFrame.show(item)

    def closeFieldFrames(self, frame):
        try:
            frame.calFrame.destroy()
        except:
            pass
        try:
            frame.optionsFrame.destroy()
        except:
            pass

    def openSearchFrame(self):
        self.mainFrame.place_forget()
        self.searchFrame.show()

    def openClanGamesLog(self):
        self.mainFrame.place_forget()
        self.clanGamesFrame.show()

    def openLeagueWarLog(self):
        self.mainFrame.place_forget()
        self.leagueFrame.showLeaguesWars()

    def openWarLog(self):
        self.mainFrame.place_forget()
        self.warFrame.show()

    def openCapitalLog(self):
        self.mainFrame.place_forget()
        self.capitalFrame.show()

    def openMainFrame(self):
        self.mainFrame.place(relx=0.5, rely=0.45, relwidth=1, relheight=0.9, anchor=customtkinter.CENTER)

    def searchClan(self, isUpdate=False):
        self.loadingFrame = LoadingFrame("Скачивание информации по клану", self.root, 12)

        if not self.loop.create_task(self.search(isUpdate)):
            return

    async def search(self, isUpdate):
        self.loadingFrame.nextStep("Поиск клана")
        if isUpdate:
            if self.lastSearchedClan["tag"] == "":
                self.errorLable.configure(text="Не был ранее найден клан")
                return False
            resData = await self.loop.create_task(self.client.getClanInfo(self.lastSearchedClan["tag"]))
        else:
            resData = await self.loop.create_task(self.client.getClanInfo(self.clanTagEntry.get()))

        if not resData:
            self.errorLable.configure(
                text="Произошла ошибка.\n Проверте:\n 1. Написанный тег.\n 2. Интернет соединение.\n 3. Нет ли в данный момент технического перерыва.\n Иначе внутренняя ошибка программы.")
            return False
        self.errorLable.configure(text="")

        self.loadingFrame.nextStep("Найден клан")
        resDict = {"name": resData.name, "tag": resData.tag, "required_trophies": resData.required_trophies,
                   "required_builder_base_trophies": resData.required_builder_base_trophies,
                   "required_townhall": resData.required_townhall,
                   "chat_language": resData.chat_language.name, "location": resData.location.name, "type": resData.type,
                   "family_friendly": resData.family_friendly, "member_count": resData.member_count,
                   "level": resData.level, "description": resData.description, "public_war_log": resData.public_war_log,
                   "war_frequency": resData.war_frequency, "war_win_streak": resData.war_win_streak,
                   "war_wins": resData.war_wins, "war_losses": resData.war_losses, "war_ties": resData.war_ties,
                   "war_league": resData.war_league.name, "capital_league": resData.capital_league.name,
                   "members": {}}

        for member in resData.members:
            resDict["members"][member.tag] = {"name": member.name, "tag": member.tag, "town_hall": member.town_hall,
                                              "exp_level": member.exp_level, "role": member.role.name,
                                              "donations": member.donations,
                                              "received": member.received, "trophies": member.trophies,
                                              "league": member.league.name,
                                              "builder_base_trophies": member.builder_base_trophies,
                                              "builder_base_league": member.builder_base_league.name}

        dataProceesing.saveClanData(resDict)

        settings.saveSetting("lastSearchedClan", {"tag": resData.tag, "name": resData.name})
        self.lastSearchedClan = {"tag": resData.tag, "name": resData.name}

        self.loadingFrame.nextStep("Сохранена информация по клану")

        self.clanInfo = dataProceesing.getClanData(self.lastSearchedClan["tag"])
        self.clanInfo["members"] = dataProceesing.getMembersData(self.lastSearchedClan["tag"])
        self.tree.delete(*self.tree.get_children())
        self.loadingFrame.nextStep("Вывод информации по клану")
        self.buildInfo()

        self.loadingFrame.nextStep("Поиск информации по КВ")
        warData = await self.loop.create_task(self.client.getWarInfo(resData.tag))
        self.loadingFrame.nextStep("Сохранение информации по КВ")
        dataProceesing.saveWarData(warData)

        self.loadingFrame.nextStep("Поиск информации по ЛКВ")
        CWL = await self.loop.create_task(self.client.getWarLeagueInfo(resData.tag))
        if CWL:
            self.loadingFrame.nextStep("Сохранение информации по ЛКВ")
            await self.loop.create_task(dataProceesing.saveLeagueWarData(CWL[0], CWL[1], resData.tag,self.client,self.loop))

        self.loadingFrame.nextStep("Поиск информации по Столице")
        raids = await self.loop.create_task(self.client.getCapitalRaids(resData.tag))
        self.loadingFrame.nextStep("Сохранение информации по Столице")
        dataProceesing.saveCapitalRaidData(raids, resData.tag)

        self.loadingFrame.nextStep("Вывод информации по звездам/процентам")
        self.summaryData = dataProceesing.getWarAttacksSummary(resData.tag)
        self.warsSummaryTree.delete(*self.warsSummaryTree.get_children())
        if self.summaryData != {}:
            self.buildWarDetailsTree()

        await self.loop.create_task(self.warFrame.updateData(self.loadingFrame))
        await self.loop.create_task(self.searchFrame.updateData())
        await self.loop.create_task(self.leagueFrame.updateData(self.loadingFrame))
        self.clanGamesFrame.updateData()
        await self.loop.create_task(self.capitalFrame.updateData(self.loadingFrame))

        self.loadingFrame.close()
        return True

    def buildInfo(self):

        self.nameLable.configure(text=f"{self.clanInfo['name']}")
        resText = f"\nТег: {self.clanInfo['tag']}.\n"
        resText += "\nОсновная информация:\n"

        resText += f"\nДля входа необходимо: {self.clanInfo['required_trophies']} трофеев; {self.clanInfo['required_builder_base_trophies']} трофеев строителя; {self.clanInfo['required_townhall']} уровень тх; \n"
        resText += f"\nЯзык клана {self.clanInfo['chat_language']}. Страна клана: {self.clanInfo['location']}.\n"
        resText += f"\nТип: {self.clanInfo['type']}. Семейного типа: {self.clanInfo['family_friendly']}.\n"
        resText += f"\nИгроков: {self.clanInfo['member_count']}. Уровень: {self.clanInfo['level']}.\n"
        resText += f"\nОписание: {self.clanInfo['description']} \n"
        resText += "\nВойны:\n"
        resText += f"\nПубличный ход войн: {self.clanInfo['public_war_log']}. Частота войн: {self.clanInfo['war_frequency']}. Серия Побед: {self.clanInfo['war_win_streak']}.\n"
        resText += f"\nПобед: {self.clanInfo['war_wins']}. Поражений: {self.clanInfo['war_losses']}. Ничьи: {self.clanInfo['war_ties']}\n"
        resText += f"\nЛига кланов: {self.clanInfo['war_league']}\n"
        resText += "\nСтолица:\n"
        resText += f"\nЛига столицы: {self.clanInfo['capital_league']}\n"

        for member in self.clanInfo['members'].values():
            if int(member['received']) != 0 and int(member['donations']) != 0:
                ratio = int(member['donations']) / int(member['received'])
            elif int(member['received']) == 0:
                ratio = int(member['donations']) / 1
            elif int(member['donations']) == 0:
                ratio = 1 / int(member['received'])
            else:
                ratio = 0

            self.tree.insert("", tkinter.END,
                             values=[member['name'], member['tag'], member['town_hall'], member['exp_level'],
                                     member['role'], member['donations'], member['received'], round(ratio, 2),
                                     member['trophies'],
                                     member['league'], member['builder_base_trophies'], member['builder_base_league']])
        self.resLable.configure(text=resText)
