import tkinter
from tkinter import PhotoImage

import customtkinter
from PIL import Image, ImageTk
from customtkinter import CTkImage

from SeamlessButton import SeamlessButton


class HelpFrame:
    def __init__(self, root):
        root.bind("<F1>",lambda x:self.close())
        self.root = root
        self.helpFrame = customtkinter.CTkFrame(self.root, border_color="white", border_width=1)
        self.helpFrame.place(relx=0.5, rely=0.4, relwidth=0.7, relheight=0.7, anchor=customtkinter.CENTER)

        self.loginFrame = customtkinter.CTkScrollableFrame(self.helpFrame, orientation='vertical',
                                                         fg_color=("gray75", "gray25"), height=720,
                                                         width=1280, corner_radius=0)
        self.generalFrame = customtkinter.CTkScrollableFrame(self.helpFrame, fg_color=("gray75", "gray25"), height=720,
                                                   width=1280, corner_radius=0)
        self.warFrame = customtkinter.CTkScrollableFrame(self.helpFrame, orientation='vertical',
                                                         fg_color=("gray75", "gray25"), height=720,
                                                         width=1280, corner_radius=0)
        self.warLeagueFrame = customtkinter.CTkScrollableFrame(self.helpFrame, orientation='vertical',
                                                         fg_color=("gray75", "gray25"), height=720,
                                                         width=1280, corner_radius=0)
        self.clanGamesFrame = customtkinter.CTkScrollableFrame(self.helpFrame, fg_color=("gray75", "gray25"), height=720,
                                                     width=1280, corner_radius=0)
        self.clanCapitalFrame = customtkinter.CTkScrollableFrame(self.helpFrame, fg_color=("gray75", "gray25"), height=720,
                                                       width=1280, corner_radius=0)
        self.searchFrame = customtkinter.CTkScrollableFrame(self.helpFrame, orientation='vertical',
                                                         fg_color=("gray75", "gray25"), height=720,
                                                         width=1280, corner_radius=0)
        self.analyticsFrame = customtkinter.CTkScrollableFrame(self.helpFrame, orientation='vertical',
                                                               fg_color=("gray75", "gray25"), height=720,
                                                               width=1280, corner_radius=0)
        try:
            self.createTabs()
            self.loginInfo()
            self.generalInfo()
            self.warsInfo()
            self.warLeaguesInfo()
            self.clanGamesInfo()
            self.capitalInfo()
            self.analyticsInfo()
            self.searchInfo()
        except:
            customtkinter.CTkLabel(self.helpFrame,text="Были удалены изображения со справкой, выгрузите базу данных и переустановите приложение",text_color="red").pack()

    def close(self):
        self.helpFrame.destroy()
        self.root.bind("<F1>", lambda x: HelpFrame(self.root))

    def createTabs(self):
        self.tabsFrame = customtkinter.CTkFrame(self.helpFrame, corner_radius=0, height=720, width=100)
        self.tabsFrame.place(relx=0.003, rely=0.5, relheight=0.99,relwidth=0.097, anchor=customtkinter.W)
        self.tabsFrame.pack_propagate(0)

        self.loginButton = SeamlessButton(self.tabsFrame, text="Вход", command=lambda: self.changeFrame("login"))
        self.loginButton.pack()

        self.generalButton = SeamlessButton(self.tabsFrame, text="Общее", command=lambda: self.changeFrame("general"))
        self.generalButton.pack()

        self.warButton = SeamlessButton(self.tabsFrame, text="Войны", command=lambda: self.changeFrame("war"))
        self.warButton.pack()

        self.warLeagueButton = SeamlessButton(self.tabsFrame, text="ЛКВ", command=lambda: self.changeFrame("lcw"))
        self.warLeagueButton.pack()

        self.clanGamesButton = SeamlessButton(self.tabsFrame, text="Игры", command=lambda: self.changeFrame("CG"))
        self.clanGamesButton.pack()

        self.clanCapitalButton = SeamlessButton(self.tabsFrame, text="Столица",
                                                command=lambda: self.changeFrame("CC"))
        self.clanCapitalButton.pack()

        self.searchButton = SeamlessButton(self.tabsFrame, text="Поиск", command=lambda: self.changeFrame("search"))
        self.searchButton.pack()

        self.analyticsButton = SeamlessButton(self.tabsFrame, text="Член клана",
                                                command=lambda: self.changeFrame("analytics"))
        self.analyticsButton.pack()

        customtkinter.CTkButton(self.tabsFrame,text="Закрыть",command=lambda :self.close()).pack(pady=10,padx=10)
        self.changeFrame("login")

    def changeFrame(self, name):

        self.loginButton.configure(fg_color=("gray75", "gray25") if name == "login" else "transparent")
        self.generalButton.configure(fg_color=("gray75", "gray25") if name == "general" else "transparent")
        self.warButton.configure(fg_color=("gray75", "gray25") if name == "war" else "transparent")
        self.warLeagueButton.configure(fg_color=("gray75", "gray25") if name == "lcw" else "transparent")
        self.clanGamesButton.configure(fg_color=("gray75", "gray25") if name == "CG" else "transparent")
        self.clanCapitalButton.configure(fg_color=("gray75", "gray25") if name == "CC" else "transparent")
        self.searchButton.configure(fg_color=("gray75", "gray25") if name == "search" else "transparent")
        self.analyticsButton.configure(fg_color=("gray75", "gray25") if name == "analytics" else "transparent")

        if name == "login":
            self.loginFrame.place(relx=0.1, rely=0.5, relwidth=0.89, relheight=0.99, anchor=customtkinter.W)
        else:
            self.loginFrame.place_forget()

        if name == "general":
            self.generalFrame.place(relx=0.1, rely=0.5, relwidth=0.89, relheight=0.99, anchor=customtkinter.W)
        else:
            self.generalFrame.place_forget()

        if name == "war":
            self.warFrame.place(relx=0.1, rely=0.5, relwidth=0.89, relheight=0.99, anchor=customtkinter.W)
        else:
            self.warFrame.place_forget()

        if name == "lcw":
            self.warLeagueFrame.place(relx=0.1, rely=0.5, relwidth=0.89, relheight=0.99, anchor=customtkinter.W)
        else:
            self.warLeagueFrame.place_forget()

        if name == "CG":
            self.clanGamesFrame.place(relx=0.1, rely=0.5, relwidth=0.89, relheight=0.99, anchor=customtkinter.W)
        else:
            self.clanGamesFrame.place_forget()

        if name == "CC":
            self.clanCapitalFrame.place(relx=0.1, rely=0.5, relwidth=0.89, relheight=0.99, anchor=customtkinter.W)
        else:
            self.clanCapitalFrame.place_forget()

        if name == "search":
            self.searchFrame.place(relx=0.1, rely=0.5, relwidth=0.89, relheight=0.99, anchor=customtkinter.W)
        else:
            self.searchFrame.place_forget()

        if name == "analytics":
            self.analyticsFrame.place(relx=0.1, rely=0.5, relwidth=0.89, relheight=0.99, anchor=customtkinter.W)
        else:
            self.analyticsFrame.place_forget()

    def loginInfo(self):
        customtkinter.CTkLabel(self.loginFrame,wraplength=800,text='''
        Для использования программы необходимо зарегистрироваться в Clash of clans API.
        Данные программа получает непосредственно с серверов SuperCell 
        и по их решению для доступа к серверам нужно у них зарегистрироваться.
        Перейдите на сайт https://developer.clashofclans.com/#/login или нажмите на кнопку зарегистрироваться.
        Сайт для регистрации представлен ниже:''',justify="left",font=("Sans serif", 16)).pack(pady=10,padx=10)
        img = Image.open("img/register.png")
        customtkinter.CTkLabel(self.loginFrame,text="",image=CTkImage(img,size=(800, 430))).pack(pady=10,padx=10)
        customtkinter.CTkLabel(self.loginFrame,wraplength=800,text='''
        При успешном входе в аккаунт, повторно вводить данные для входа при запуске не нужно.
        Выйти из аккаунта можно на вкладке "Общее" нажав на кнопку "Выйти из аккаунта"''',justify="left",font=("Sans serif", 16)).pack(pady=10,
                                                                                                        padx=10)

    def generalInfo(self):
        customtkinter.CTkLabel(self.generalFrame,wraplength=800,text='''
        На вкладке "Общее" производится поиск клана. Введя его тег, # не обязателен, и нажав на "Найти клан"
        С серверов будут скачены все доступные данные по клану. Последний найденный клан сохраняется при закрытии приложения.
        При первом запуске приложения в определенный день, автоматически происходит поиск по последнему найденному клану.
        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/searched.png")
        customtkinter.CTkLabel(self.generalFrame,text="", image=CTkImage(img,size=(800, 430))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.generalFrame, wraplength=800,text='''
                На данной вкладке находятся 2 таблицы "Общее" с кратким описание членов клана.
                Двойной щелчок по выбранному в таблице пользователю открывает его полное описание. 
                См. раздел "Член клана"
                
                Второй таблицей является "Войны", с кратким описанием аналитики по атакам по членам клана.
                Данные в эту таблицу попадают только если член клана провел от 10 атак. Это необходимо чтобы,если член провел только 2 атаки на 3 звезды, статистика не выводила его на 1 место по клану.
                
                Для сортировки по возрастанию или убыванию можно нажать на название колонки таблицы.
                ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/warsGeneral.png")
        customtkinter.CTkLabel(self.generalFrame,text="", image=CTkImage(img, size=(760, 327))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.generalFrame, wraplength=800,text='''
                Сохраненную информацию по клану можно выгрузить отдельным файлом для передачи другим пользователям приложения.
                
                Нажав "Выгрузить информацию по клану" в папке Путь_к_приложению/Databases/copy сохранится файл формата .db
                
                Так же каждый день при первом запуске происходит резервное копирование базы данных в Путь_к_приложению/Databases/backups
                
                Нажав "Загрузить информацию по клану" можно выбрать .db файл для загрузки. После загрузки необходимо обновить данные для отображения.
                ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

    def warsInfo(self):
        customtkinter.CTkLabel(self.warFrame, wraplength=800,text='''
        На вкладке "Войны" находятся все КВ сохраненного клана. И все атаки в данном КВ.
        
        ВАЖНО! Сохранить информацию по КВ можно только до начала следующего, после доступа к данным на сервере нет. Следующее КВ считается начатым при нажатии поиска КВ. Даже если не подтвердить поиск, все равно доступ будет закрыт.
        
        При необходимости можно провести поиск по КВ найденного клана, нажав "Обновить данные"
        Для сортировки по возрастанию или убыванию можно нажать на название колонки таблицы.
        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/wars.png")
        customtkinter.CTkLabel(self.warFrame,text="", image=CTkImage(img,size=(800, 430))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.warFrame, wraplength=800,text='''
                        В таблице по КВ имеются цветовые обозначения:
                        1. Фиолетовый - текущая война
                        2. Зеленый - вый гранная война
                        3. Красный - проигранная война
                        4. Серый - Ничья
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.warFrame, wraplength=800,text='''
                        Все даты в программе по часовому поясу UTC-0 и формату ГГГГ-ММ-ДД, так как сервера SuperCell хранят даты в даном формате.
                        
                        Про выборку по категориям смотрите раздел "Поиск"

                        При двойном щелчке по необходимому КВ открываются атаки в данном КВ по членам клана.
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/warAttacks.png")
        customtkinter.CTkLabel(self.warFrame,text="", image=CTkImage(img, size=(800, 430))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.warFrame, wraplength=800,text='''
                        В таблице по атакам на КВ имеются цветовые обозначения:
                        1. Зеленый - 3 звезды
                        2. Красный - Не атаковал или забрал чужое зеркало
                        3. Оранжевый - Атака ниже 85% и меньше 2 звезд 
                        4. Серый - Не входит в предыдущие категории
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

    def warLeaguesInfo(self):
        customtkinter.CTkLabel(self.warLeagueFrame, wraplength=800,text='''
        На вкладке "Лиги войн" находятся все ЛКВ сохраненного клана. И все атаки в данном ЛКВ.
        
        ВАЖНО! Сохранить информацию по ЛКВ можно только до начала следующего КВ, после доступа к данным на сервере нет. Следующее КВ считается начатым при нажатии поиска КВ. Даже если не подтвердить поиск, все равно доступ будет закрыт.
        
        При необходимости можно провести поиск по ЛКВ найденного клана, нажав "Обновить данные"
        Для сортировки по возрастанию или убыванию можно нажать на название колонки таблицы.
        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/warLeagues.png")
        customtkinter.CTkLabel(self.warLeagueFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.warLeagueFrame, wraplength=800,text='''
                        В таблице по ЛКВ имеются цветовые обозначения:
                        1. Фиолетовый - текущая ЛКВ
                        
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.warLeagueFrame, wraplength=800,text='''
                        При двойном щелчке по необходимому ЛКВ открываются 2 таблицы "По войнам" и "По атакам".
                        
                        Таблица "По войнам" идентична вкладке "Войны", но отображаются только КВ данного ЛКВ. Информацию об данной вкладке можно найти в одноименном разделе. Данные по КВ дублируются на вкладку "Войны"
                        
                        Таблица "По атакам" показывает статистику отдельных членов клана на данном ЛКВ.
                        
                        Желательно не пользоваться только статистикой для выдачи бонусов. А использовать её только как один из факторов при выборе кандидатов на бонусы.
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/warLeaguesStat.png")
        customtkinter.CTkLabel(self.warLeagueFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10, padx=10)

    def clanGamesInfo(self):
        customtkinter.CTkLabel(self.clanGamesFrame, wraplength=800,text='''
        На вкладке "Игры кланов" находятся все ИК сохраненного клана. И все данные по членам в ИК.
        
        ВАЖНО! К ИК нет доступа на серверах, все необходимо вводить вручную. Сохраняйте скриншоты ИК для удобства записи. При получении награды за ИК вам дается доступ к медалям всех членов клана. Перезайдя в игру вы их больше не увидите!

        При необходимости можно провести поиск по ИК найденного клана, нажав "Обновить данные"
        Для сортировки по возрастанию или убыванию можно нажать на название колонки таблицы.
        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/clanGames.png")
        customtkinter.CTkLabel(self.clanGamesFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                        padx=10)

        customtkinter.CTkLabel(self.clanGamesFrame, wraplength=800,text='''
                        В таблице по ИК имеются цветовые обозначения:
                        1. Зеленый - 6 уровень награды
                        2. Красный - <5 уровня награды
                        3. Оранжевый - 5 уровень награды
                        4. Фиолетовый - Текущие ИК

                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.clanGamesFrame, wraplength=800,text='''
                        Поскольку ИК не скачиваются с серверов Есть возможность сохранения, удаления и изменения данных.
                        
                        При добавлении данных, нажатием "Добавить данные" открывается окно с вводом данных, представленное ниже.
                        
                        Уровень наград и количество медалей - целые числа.
                        Дата начала и окончания вводятся по формату: ГГГГ-ММ-ДД. Для удобства используйте "Выбрать"
                        
                        После можно нажать "Добавить" для сохранения результата.
                        
                        Если есть необходимость изменить или удалить запись, выберите её в таблице и нажмите нужную кнопку.
                        
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/clanGamesAdd.png")
        customtkinter.CTkLabel(self.clanGamesFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                        padx=10)

        customtkinter.CTkLabel(self.clanGamesFrame, wraplength=800,text='''
                                При двойном щелчке по необходимому ИК открывается таблица с медалями каждого члена на этом ИК.
                                
                                ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/clanGamesMembers.png")
        customtkinter.CTkLabel(self.clanGamesFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                        padx=10)
        customtkinter.CTkLabel(self.clanGamesFrame, wraplength=800,text='''
                                В таблице по медалям членов клана по ИК имеются цветовые обозначения:
                                1. Зеленый - 4000 медалей
                                2. Красный - 600 и меньше медалей
                                3. Оранжевый - от 600 и до 1000 медалей
                                4. Серый - от 1000 и до 4000 медалей

                                ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)
        customtkinter.CTkLabel(self.clanGamesFrame, wraplength=800,text='''
                                        При добавлении данных, нажатием "Добавить данные" открывается окно с вводом данных, представленное ниже.
                                        
                                        Количество медалей - целые числа.
                                        Член клана выбирается из списка, представленного на вкладке "Общие". Если вы не можете найти нужного члена клана проверте не вышел ли он из клана.
                                        
                                        После можно нажать "Добавить" для сохранения результата.

                                        Если есть необходимость изменить или удалить запись, выберите её в таблице и нажмите нужную кнопку.

                                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)
        img = Image.open("img/clanGamesMembersAdd.png")
        customtkinter.CTkLabel(self.clanGamesFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                        padx=10)

    def capitalInfo(self):
        customtkinter.CTkLabel(self.clanCapitalFrame, wraplength=800, text='''
        На вкладке "Столица" находятся все Рейды на столицы сохраненного клана. И все атаки в данных Рейдах .

        ВАЖНО! Сохранить информацию по Рейдам можно только до начала следующего, после доступа к данным на сервере нет.

        При необходимости можно провести поиск по Рейдам найденного клана, нажав "Обновить данные"
        Для сортировки по возрастанию или убыванию можно нажать на название колонки таблицы.
        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/clanСapital.png")
        customtkinter.CTkLabel(self.clanCapitalFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.clanCapitalFrame, wraplength=800, text='''
                        Все даты в программе по часовому поясу UTC-0 и формату ГГГГ-ММ-ДД, так как сервера SuperCell хранят даты в даном формате.

                        Про выборку по категориям смотрите раздел "Поиск"

                        При двойном щелчке по необходимым Рейдам открываются атаки в данном Рейде по членам клана.
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/clanСapitalMember.png")
        customtkinter.CTkLabel(self.clanCapitalFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.clanCapitalFrame, wraplength=800, text='''
                        В таблице по атакам на Рейде имеются цветовые обозначения:
                        1. Зеленый - 6 атак
                        2. Красный - 0-1 атака
                        3. Оранжевый - 2-5 атак
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)
    def analyticsInfo(self):
        customtkinter.CTkLabel(self.analyticsFrame, wraplength=800, text='''
        При двойном щелчке в таблице "Общее" на одноименной вкладке открывается статистика на выбранного члена клана.

        Имеются следующие вкладки:
        1. Общее - основная информация об члене клана, и форма для записи своего описания о нем
        2. Войны - статистика по атакам на кв и таблица с атаками
        3. Игры - статистика по ИК на и таблица с заработанными медалями
        4. Столица - статистика по Рейдам и таблица с  заработанными медалями
        
        Все даты в программе по часовому поясу UTC-0 и формату ГГГГ-ММ-ДД, так как сервера SuperCell хранят даты в даном формате.
        
        Про выборку в таблицах по категориям смотрите раздел "Поиск"
        
        При необходимости можно обновить данные в таблице нажав "Обновить данные" в интересующей вкладке
        Для сортировки по возрастанию или убыванию можно нажать на название колонки таблицы.
        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/memberGen.png")
        customtkinter.CTkLabel(self.analyticsFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.analyticsFrame, wraplength=800, text='''
                        На вкладке "Войны" присутствуют 3 диаграммы:
                        1. Звезды в атаках
                        2. Сила опонента в атаках
                        3. Атаки на зеркала
                        
                        В разделе диаграммы указано число атака входящих в данную категорию. Рядом с разделом указано его название.
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/memberWar.png")
        customtkinter.CTkLabel(self.analyticsFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10, padx=10)

        customtkinter.CTkLabel(self.analyticsFrame, wraplength=800, text='''
                        Все таблицы идентичны таблицам из таких же вкладок при просмотре информации о кв в целом. Для справки об интересующих таблица смотрите одноименные разделы.
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/memberCC.png")
        customtkinter.CTkLabel(self.analyticsFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                          padx=10)

    def searchInfo(self):
        customtkinter.CTkLabel(self.searchFrame, wraplength=800, text='''
        На вкладке "Поиск по клану" и перед таблица в остальных вкладках есть возможность выборки данных.

        Для задачи статистики по которой происходит выборка используется кнопка "Добавить статистику". В открывшимся окне дается выбор статистик применимых к той таблице в которой производится выборка. Нажав на необходимую статистику она добавится в список.
        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/searchAdd.png")
        customtkinter.CTkLabel(self.searchFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                        padx=10)

        customtkinter.CTkLabel(self.searchFrame, wraplength=800, text='''
                        В изображении ниже представлены 2 вида статистик:
                        1. С предопределенными значениями выбора
                        2. Числовые с заданием математического знака неравенства/равенства
                        
                        На изображении имеются следующие отображения:
                        1 - Логическая операция определяющее взаимодействие с другими статистиками в выборе
                        2 - Название статистики
                        3 - Значение статистики
                        4 - Неравенство/равенство числовой статистики
                        5 - Управление положением статистик
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/searchButtons.png")
        customtkinter.CTkLabel(self.searchFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                        padx=10)
        customtkinter.CTkLabel(self.searchFrame, wraplength=800, text='''
                                Положение в списки имеет значение, порядок расмотрения статистик сверху-вниз, логическая операция привязывает статистику к той что сверху (оператор 1 в списке не имеет значения),приоритет операции "И" можно воспринимать как приоритет умножения, "ИЛИ" сложения. Если не ввести число или установить "Не выбрано" найдутся все результаты по данной статистике.
                                
                                Например в следующем примере идет выбор "(кто имеет роль старейшину и в среднем на рейдах приносит больше 10000 золота) или у кого 12 тх"
                                ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/searchEx1.png")
        customtkinter.CTkLabel(self.searchFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                        padx=10)

        customtkinter.CTkLabel(self.searchFrame, wraplength=800, text='''
                        В следующем примере идет выбор "(кто имеет роль старейшину и в среднем на рейдах приносит больше 10000 золота) или (у кого 14 тх и задонатил больше 400)"
                        ''', justify="left", font=("Sans serif", 16)).pack(pady=10, padx=10)

        img = Image.open("img/searchEx2.png")
        customtkinter.CTkLabel(self.searchFrame, text="", image=CTkImage(img, size=(800, 430))).pack(pady=10,
                                                                                                        padx=10)