import datetime
import tkinter

import customtkinter
from tkcalendar import Calendar

import dataProceesing
from SeamlessButton import SeamlessButton


class Option:
    def __init__(self, name, rusName, grid, optionType, values=[]):
        self.name = name
        self.rusName = rusName
        self.grid = grid
        self.optionType = optionType
        self.values = values


class CustomQuery:
    def __init__(self, root,searchFrame, lastSearchedClan, options,searchIn,showCalendar=True,colorCorrection=None):
        self.allOptions = options
        self.root = root
        self.searchFrame = searchFrame
        self.lastSearchedClan = lastSearchedClan
        self.searchIn = searchIn
        self.showCalendar = showCalendar
        if colorCorrection is None: colorCorrection = "gray20"
        self.colorCorrection = colorCorrection

    def createEntries(self):
        self.inputsFrame = customtkinter.CTkFrame(self.searchFrame)
        self.inputsFrame.pack()

        dateFrame = customtkinter.CTkFrame(self.inputsFrame, bg_color=self.colorCorrection, fg_color=self.colorCorrection)
        if self.showCalendar:
            dateFrame.pack()

        dataLabel = customtkinter.CTkLabel(dateFrame, text="Выборка по периоду (гггг-мм-дд):")
        dataLabel.pack()

        dataStartLabel = customtkinter.CTkLabel(dateFrame, text="От:")
        dataStartLabel.pack(side=tkinter.LEFT, padx=5)

        self.periodStart = customtkinter.CTkEntry(dateFrame)
        self.periodStart.pack(side=tkinter.LEFT, padx=5)

        startBut = customtkinter.CTkButton(dateFrame, text="Выбрать",
                                           command=lambda: self.selectTime("Дата начала"))
        startBut.pack(side=tkinter.LEFT, padx=5)

        dataStartLabel = customtkinter.CTkLabel(dateFrame, text="До:")
        dataStartLabel.pack(side=tkinter.LEFT, padx=5)

        self.periodEnd = customtkinter.CTkEntry(dateFrame)
        self.periodEnd.pack(side=tkinter.LEFT, padx=5)

        endBut = customtkinter.CTkButton(dateFrame, text="Выбрать",
                                         command=lambda: self.selectTime("Дата окончания"))
        endBut.pack(side=tkinter.LEFT, padx=5)

        self.columnNames = {"tag": "Тег", "name": "Имя"}
        self.options = {"order": []}

        generalLabel = customtkinter.CTkLabel(self.inputsFrame, text="Выборка по информации:")
        generalLabel.pack(pady=10)

        self.generalFrame = customtkinter.CTkScrollableFrame(self.inputsFrame, height=100, width=1030)
        self.generalFrame.pack(padx=10)

        self.addButton = customtkinter.CTkButton(self.inputsFrame, text="Добавить статистику",
                                                 command=lambda: self.addOption())
        self.addButton.pack(pady=10)

        self.errorLable = customtkinter.CTkLabel(self.inputsFrame,text="",text_color="red",wraplength=700)
        self.errorLable.pack()

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
            self.periodStart.delete(0, tkinter.END)
            self.periodStart.insert(0, self.cal.get_date())
        else:
            self.periodEnd.delete(0, tkinter.END)
            self.periodEnd.insert(0, self.cal.get_date())

        self.calFrame.destroy()

    def addOption(self):
        self.optionsFrame = customtkinter.CTkFrame(self.root, border_color="white", border_width=1)
        self.optionsFrame.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor=customtkinter.CENTER)

        buttonsFrame = customtkinter.CTkFrame(self.optionsFrame)
        buttonsFrame.pack(pady=20, padx=20)

        for option in self.allOptions:
            if option.optionType == "label":
                customtkinter.CTkLabel(buttonsFrame, text=option.rusName).grid(row=option.grid["row"],
                                                                               column=option.grid["column"])
            elif option.optionType == "entry":
                SeamlessButton(buttonsFrame, text=option.rusName,
                               command=lambda name=option.name, rusName=option.rusName: self.createEntry(name, rusName,
                                                                                                         "self.generalFrame",
                                                                                                         "general")).grid(
                    row=option.grid["row"],
                    column=option.grid["column"])
            elif option.optionType == "selector":
                SeamlessButton(buttonsFrame, text=option.rusName,
                               command=lambda name=option.name, rusName=option.rusName,
                                              values=option.values: self.createSelector(name, rusName,
                                                                                        "self.generalFrame",
                                                                                        values, "general")).grid(
                    row=option.grid["row"], column=option.grid["column"])

        cancelButton = customtkinter.CTkButton(self.optionsFrame, text="Отмена",
                                               command=lambda: self.optionsFrame.destroy())
        cancelButton.pack(padx=20, pady=20)

    def removeOption(self, pos):
        self.options["order"].pop(pos)
        for i in self.generalFrame.grid_slaves(row=pos):
            i.destroy()
        for i in range(pos, len(self.options["order"])):
            first = self.options["order"][i]

            exec(
                f"self.upButton{first['name']}{first['exist']}.configure(command=lambda self=self,pos = i: self.moveOrder(-1,pos))")
            exec(
                f"self.downButton{first['name']}{first['exist']}.configure(command=lambda self=self,pos = i: self.moveOrder(1,pos))")

            exec(
                f"self.closeButton{first['name']}{first['exist']}.configure(command=lambda self=self,pos=i: self.removeOption(pos))")
            for j in self.generalFrame.grid_slaves(row=i + 1):
                grid = j.grid_info()
                j.grid(row=grid["row"] - 1, column=grid["column"], padx=5)

    def createEntry(self, name, description, parentFrame, type):
        exist = sum(x["exist"] for x in self.options["order"]) + 1
        exec(f"grid = {parentFrame}.grid_size()")

        self.optionsFrame.destroy()
        exec("self.createOperatorSelector(name,exist,parentFrame,grid)")

        exec(f"{name}Label = customtkinter.CTkLabel({parentFrame}, text='{description}:')")
        exec(f"{name}Label.grid(column=1,row=grid[1],padx=5,pady=2)")

        exec(f"self.{name}Entry{exist} = customtkinter.CTkEntry({parentFrame})")
        exec(f"self.{name}Entry{exist}.grid(column=2,row=grid[1],padx=5)")

        exec(f"self.selectedFunk{name}{exist} = tkinter.StringVar({parentFrame})")

        options = ["<", ">", "=", "<=", ">=", "!="]

        exec(f"self.selectedFunk{name}{exist}.set(options[2])")

        exec(
            f"self.selectorFunk{name}{exist} = customtkinter.CTkOptionMenu({parentFrame}, variable=self.selectedFunk{name}{exist},values=options)")
        exec(f"self.selectorFunk{name}{exist}.grid(column=3,row=grid[1],padx=5)")

        exec(
            f"self.closeButton{name}{exist} = customtkinter.CTkButton({parentFrame}, text='Удалить', command=lambda self=self,pos=len(self.options['order']): self.removeOption(pos))")
        exec(f"self.closeButton{name}{exist}.grid(column=4,row=grid[1],padx=5)")

        exec(
            f"self.upButton{name}{exist} = customtkinter.CTkButton({parentFrame}, text='⮝', command=lambda self=self,pos = len(self.options['order']): self.moveOrder(-1,pos))")
        exec(f"self.upButton{name}{exist}.grid(column=5,row=grid[1],padx=5)")

        exec(
            f"self.downButton{name}{exist} = customtkinter.CTkButton({parentFrame}, text='⮟', command=lambda self=self,pos = len(self.options['order']): self.moveOrder(1,pos))")
        exec(f"self.downButton{name}{exist}.grid(column=6,row=grid[1],padx=5)")

        exec(
            f"self.options['order'].append(" + "{" + f"'name':'{name}', 'data': self.{name}Entry{exist}, 'funk': self.selectedFunk{name}{exist}, 'operator': self.selectedOperator{name}{exist}, 'exist':{exist}" + "})")
        self.columnNames[name] = description

    def createSelector(self, name, description, parentFrame, options, type):
        exist = sum(x["exist"] for x in self.options["order"])
        exec(f"grid = {parentFrame}.grid_size()")

        self.optionsFrame.destroy()
        exec("self.createOperatorSelector(name,exist,parentFrame,grid)")

        exec(f"{name}Label = customtkinter.CTkLabel({parentFrame}, text='{description}:')")
        exec(f"{name}Label.grid(column=1,row=grid[1],padx=5,pady=2)")

        exec(f"self.selectedFunk{name}{exist} = tkinter.StringVar({parentFrame})")
        exec(f"self.selectedFunk{name}{exist}.set('selector')")

        exec(f"self.{name}Entry{exist} = tkinter.StringVar({parentFrame})")
        exec(f"self.{name}Entry{exist}.set(options[0])")

        exec(
            f"selector{name} = customtkinter.CTkOptionMenu({parentFrame}, variable=self.{name}Entry{exist},values=options)")
        exec(f"selector{name}.grid(column=2,row=grid[1],padx=5)")

        exec(
            f"self.closeButton{name}{exist} = customtkinter.CTkButton({parentFrame}, text='Удалить', command=lambda self=self,pos=len(self.options['order']): self.removeOption(pos))")
        exec(f"self.closeButton{name}{exist}.grid(column=4,row=grid[1],padx=5)")

        exec(
            f"self.upButton{name}{exist} = customtkinter.CTkButton({parentFrame}, text='⮝', command=lambda self=self,pos = len(self.options['order']): self.moveOrder(-1,pos))")
        exec(f"self.upButton{name}{exist}.grid(column=5,row=grid[1],padx=5)")

        exec(
            f"self.downButton{name}{exist} = customtkinter.CTkButton({parentFrame}, text='⮟', command=lambda self=self,pos = len(self.options['order']): self.moveOrder(1,pos))")
        exec(f"self.downButton{name}{exist}.grid(column=6,row=grid[1],padx=5)")

        exec(
            f"self.options['order'].append(" + "{" + f"'name':'{name}', 'data': self.{name}Entry{exist}, 'funk': self.selectedFunk{name}{exist}, 'operator': self.selectedOperator{name}{exist}, 'exist':{exist}" + "},)")

        if name == "opponentTh":
            self.columnNames["memberTh"] = "ТХ на момент кв"
            self.columnNames["defenderTh"] = "ТХ оппонента"

        if name == "mirror":
            self.columnNames["mapPosition"] = "Позиция на кв"
            self.columnNames["defenderPosition"] = "Позиция оппонента"
        self.columnNames[name] = description

    def createOperatorSelector(self, name, exist, parentFrame, grid):
        exec(f"self.selectedOperator{name}{exist} = tkinter.StringVar({parentFrame})")

        options = ["И", "ИЛИ"]
        exec(f"self.selectedOperator{name}{exist}.set(options[0])")

        exec(
            f"selectorFunk{name} = customtkinter.CTkOptionMenu({parentFrame}, variable=self.selectedOperator{name}{exist},values=options)")
        exec(f"selectorFunk{name}.grid(column=0,row=grid[1],padx=5)")

    def moveOrder(self, direction, pos):
        if (pos != 0 and direction == -1) or (pos != len(self.options["order"]) - 1 and direction == 1):
            self.options["order"][pos], self.options["order"][pos + direction] = self.options["order"][pos + direction], \
                                                                                 self.options["order"][pos]
            first = self.options["order"][pos]
            second = self.options["order"][pos + direction]

            exec(
                f"self.upButton{first['name']}{first['exist']}.configure(command=lambda self=self,pos = pos: self.moveOrder(-1,pos))")
            exec(
                f"self.downButton{first['name']}{first['exist']}.configure(command=lambda self=self,pos = pos: self.moveOrder(1,pos))")

            exec(
                f"self.upButton{second['name']}{second['exist']}.configure(command=lambda self=self,pos = pos + direction: self.moveOrder(-1,pos))")
            exec(
                f"self.downButton{second['name']}{second['exist']}.configure(command=lambda self=self,pos = pos + direction: self.moveOrder(1,pos))")

            exec(
                f"self.closeButton{first['name']}{first['exist']}.configure(command=lambda self=self,pos=pos: self.removeOption(pos))")
            exec(
                f"self.closeButton{second['name']}{second['exist']}.configure(command=lambda self=self,pos=pos + direction: self.removeOption(pos))")

            firstRow = self.generalFrame.grid_slaves(row=pos)
            secondRow = self.generalFrame.grid_slaves(row=pos + direction)

            for i in firstRow:
                grid = i.grid_info()
                i.grid(row=pos + direction, column=grid["column"])

            for i in secondRow:
                grid = i.grid_info()
                i.grid(row=pos, column=grid["column"])

    def serch(self):
        error = "Проверте данные введенные в:  "
        self.errorLable.configure(text="")

        resDict = {"order": []}
        toRemove = {"order": []}
        for option in self.options["order"]:
            try:
                resDict["order"].append(
                    {"name": option["name"], "data": option["data"].get(), "funk": option["funk"].get(),
                     "operator": option["operator"].get()})
                if not option["data"].get().isdigit() and option["data"].get() != '' and option["funk"].get() != "selector":
                    error += f"\"{self.columnNames[option['name']]}\", "
            except:
                # Нельзя изменить options в цикле
                toRemove["order"].append(option)

        error = error[:-2]
        for i in toRemove["order"]:
            self.options["order"].remove(i)

        if self.periodStart.get() != "":
            try:
                datetime.date.fromisoformat(self.periodStart.get())
            except:
                error += "\nДата начала должна быть в формате (гггг-мм-дд)  "

        if self.periodEnd.get() != "":
            try:
                datetime.date.fromisoformat(self.periodEnd.get())
            except:
                error += "\nДата окончания должна быть в формате (гггг-мм-дд)  "

        if error != "Проверте данные введенные в:":
            self.errorLable.configure(text=error)
            return

        if self.options["order"] or (self.periodStart.get(), self.periodEnd.get()).count("") != 2:
            if self.searchIn == "SearchFrame":
                return dataProceesing.clanSearch(self.lastSearchedClan["tag"], resDict,
                                             (self.periodStart.get(), self.periodEnd.get()))
            else:
                return self.constructWhere(resDict,(self.periodStart.get(), self.periodEnd.get()))
        return None

    def constructWhere(self,data,period):
        attackedValues = {"Атаковал": 1, "Не атаковал": 0}
        thValues = {"Атаковал равного": "=", "Атаковал слабого": "<", "Атаковал сильного": ">"}
        operators = {"И": "AND", "ИЛИ": "OR"}

        query = "and ("
        for option in data["order"]:
            if option['data'] == "" or option['data'] == "Не выбрано": continue
            if option['name'] == "warResult":
                if option['data'] == "Победа":
                    query += f"{operators[option['operator']] if query[-1] != '(' else ''} (clanStars > opponentStars or (clanStars = opponentStars and clanPercent > opponentPercent))"
                elif option['data'] == "Поражение":
                    query += f"{operators[option['operator']] if query[-1] != '(' else ''} (clanStars < opponentStars or (clanStars = opponentStars and clanPercent < opponentPercent))"
                elif option['data'] == "Ничья":
                    query += f"{operators[option['operator']] if query[-1] != '(' else ''} (clanStars = opponentStars and clanPercent = opponentPercent)"
                continue
            if self.searchIn == "warAttacks":
                if option['name'] == "opponentTh":
                    query += f"{operators[option['operator']] if query[-1] != '(' else ''} memberTownHall {thValues[option['data']]} defenderTownHall "
                    continue

                if option['name'] == "attacked":
                    query += f"{operators[option['operator']] if query[-1] != '(' else ''} attacked = {attackedValues[option['data']]} "
                    continue

                if option['name'] == "mirror":
                    query += dataProceesing.getMirorQuery(operators,query,option)
                    continue

            query += f"{operators[option['operator']] if query[-1] != '(' else ''} {option['name']} {option['funk']} {option['data']} "

        if (self.periodStart.get(), self.periodEnd.get()).count("") != 2 and self.searchIn not in ("warAttacks","capitalRaidMembers","clanGamesMembers"):
            query += f"{'and' if query[-1] != '(' else ''} (date(startTime) between '{'0000-00-00' if period[0] == '' else period[0]}' and '{'9999-12-31' if period[1] == '' else period[1]}' or date(endTime) between '{'0000-00-00' if period[0] == '' else period[0]}' and '{'9999-12-31' if period[1] == '' else period[1]}')"
        query += ")"
        query = query.replace("and ()", "")

        return query
