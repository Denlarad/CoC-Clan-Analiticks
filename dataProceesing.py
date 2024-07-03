import datetime
import os
import pathlib
import shutil
import sqlite3
import string
import time
from datetime import date
import json
from itertools import chain
from pathlib import Path

import coc

import requests
import settings

CLAN_DATA_PATH = "clanData.json"

translationDict = {"roles": {"member": "Член", "elder": "Старейшина", "co_leader": "Соруководитель", "leader": "Лидер"},
                   "bool": {True: "Да", False: "Нет"},
                   "type": {"open": "Открытый", "inviteOnly": "По приглашению", "closed": "Закрытый"},
                   "warFrequency": {"unknown": "Неизвестно", "always": "Всегда",
                                    "more_than_once_per_week": "Дважды в неделю", "less_than_once_per_week": "Редко",
                                    "once_per_week": "Раз в неделю", "never": "Никогда", "any": "Неважно"},
                   "leagues": {"Unranked": "Нет", "Bronze League III": "Бронзовая III",
                               "Bronze League II": "Бронзовая II", "Bronze League I": "Бронзовая I",
                               "Silver League III": "Серебряная III", "Silver League II": "Серебряная II",
                               "Silver League I": "Серебряная I",
                               "Gold League III": "Золотая III", "Gold League II": "Золотая II",
                               "Gold League I": "Золотая I",
                               "Crystal League III": "Хрустальная III", "Crystal League II": "Хрустальная II",
                               "Crystal League I": "Хрустальная I",
                               "Master League III": "Мастер III", "Master League II": "Мастер II",
                               "Master League I": "Мастер I",
                               "Champion League III": "Чемпионская III", "Champion League II": "Чемпионская II",
                               "Champion League I": "Чемпионская I",
                               "Titan League III": "Титан III", "Titan League II": "Титан II",
                               "Titan League I": "Титан I",
                               "Legend League": "Мастер"},
                   "buildersLeagues": {"Unranked": "Нет", "Wood League V": "Деревянная V",
                                       "Wood League IV": "Деревянная IV", "Wood League III": "Деревянная III",
                                       "Wood League II": "Деревянная II", "Wood League I": "Деревянная I",
                                       "Clay League V": "Глиняная V", "Clay League IV": "Глиняная IV",
                                       "Clay League III": "Глиняная III",
                                       "Clay League II": "Глиняная II", "Clay League I": "Глиняная I",
                                       "Stone League V": "Каменная V", "Stone League IV": "Каменная IV",
                                       "Stone League III": "Каменная III",
                                       "Stone League II": "Каменная II", "Stone League I": "Каменная I",
                                       "Copper League V": "Медная V", "Copper League IV": "Медная IV",
                                       "Copper League III": "Медная III",
                                       "Copper League II": "Медная II", "Copper League I": "Медная I",
                                       "Brass League III": "Латунная III", "Brass League II": "Латунная II",
                                       "Brass League I": "Латунная I",
                                       "Iron League III": "Железная III", "Iron League II": "Железная II",
                                       "Iron League I": "Железная I",
                                       "Steel League III": "Стальная III", "Steel League II": "Стальная II",
                                       "Steel League I": "Стальная I",
                                       "Titanium League III": "Титановая III", "Titanium League II": "Титановая II",
                                       "Titanium League I": "Титановая I",
                                       "Platinum League III": "Платиновая III", "Platinum League II": "Титановая II",
                                       "Platinum League I": "Титановая I",
                                       "Emerald League III": "Изумрудная III", "Emerald League II": "Изумрудная II",
                                       "Emerald League I": "Изумрудная I",
                                       "Ruby League III": "Рубиновая III", "Ruby League II": "Рубиновая II",
                                       "Ruby League I": "Рубиновая I",
                                       "Diamond League": "Алмазная"}
                   }


def saveClanData(data):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute('''
                insert or replace Into clans (tag,name,reqTrophies,reqBuildersTrophies,reqTownHall,language,location,type,familyFriendly,membersCount,
                level,description,isWarLogPublic,warFrequency,warStreak,warWins,warLosses,warTies,warLeague,capitalLeague,date)
                values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,DATE('now'))''',
                   (data["tag"], data["name"], data["required_trophies"], data["required_builder_base_trophies"],
                    data["required_townhall"], data["chat_language"], data["location"],
                    translationDict["type"][data["type"]],
                    translationDict["bool"][data["family_friendly"]], data["member_count"], data["level"],
                    data["description"],
                    translationDict["bool"][data["public_war_log"]],
                    translationDict["warFrequency"][data["war_frequency"]], data["war_win_streak"], data["war_wins"],
                    data["war_losses"], data["war_ties"], translationDict["leagues"][data["war_league"]],
                    translationDict["leagues"][data["capital_league"]]))
    cursor.execute(f'''delete from members where clanTag = "{data["tag"]}"''')
    connection.commit()
    for memberTag, member in data["members"].items():
        cursor.execute('''
                            insert or replace Into members (tag,name,clanTag,trophies,league,buildersTrophies,buildersLeague,townHall,level,role,send,received,description)
                            values (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                       (memberTag, member["name"], data["tag"], member["trophies"],
                        translationDict["leagues"][member["league"]],
                        member["builder_base_trophies"],
                        translationDict["buildersLeagues"][member["builder_base_league"]], member["town_hall"],
                        member["exp_level"], translationDict["roles"][member["role"]], member["donations"],
                        member["received"], ""))
    connection.commit()
    connection.close()


def addDescriptionToMember(tag, text):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(f"update members set description = '{text}' where tag = '{tag}'")
    connection.commit()
    connection.close()

def getDescriptionToMember(tag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(f"select description from members where tag = '{tag}'")
    desc = cursor.fetchone()[0]
    connection.close()
    if desc == None: desc = ""
    return desc

def getClanData(tag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(f"select * from clans where tag = '{tag}' and date = '{str(datetime.date.today())}'")
    try:
        clanData = cursor.fetchall()[0]
        resDict = {"tag": clanData[0], "name": clanData[1], "required_trophies": clanData[2],
                   "required_builder_base_trophies": clanData[3],
                   "required_townhall": clanData[4], "chat_language": clanData[5], "location": clanData[6],
                   "type": clanData[7],
                   "family_friendly": clanData[8], "member_count": clanData[9], "level": clanData[10],
                   "description": clanData[11],
                   "public_war_log": clanData[12], "war_frequency": clanData[13], "war_win_streak": clanData[14],
                   "war_wins": clanData[15], "war_losses": clanData[16], "war_ties": clanData[17],
                   "war_league": clanData[18], "capital_league": clanData[19], "date": clanData[20]}
    except:
        resDict = {}
    connection.close()
    return resDict


def getMembersData(tag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(f"select * from members where clanTag = '{tag}'")
    membersData = cursor.fetchall()
    resDict = {}
    try:
        for member in membersData:
            resDict[member[0]] = {"tag": member[0], "name": member[1], "trophies": member[3], "league": member[4],
                                  "builder_base_trophies": member[5], "builder_base_league": member[6],
                                  "town_hall": member[7], "exp_level": member[8], "role": member[9],
                                  "donations": member[10], "received": member[11]}
    except:
        pass
    connection.close()
    return resDict


def createDataBase():
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute('''
    create table IF NOT EXISTS clans(
    tag text primary key,
    name text not null,
    reqTrophies integer not null,
    reqBuildersTrophies integer not null,
    reqTownHall integer not null,
    language text not null,
    location text not null,
    type text not null,
    familyFriendly text not null,
    membersCount integer not null,
    level integer not null,
    description text not null,
    isWarLogPublic text not null,
    warFrequency text,
    warStreak integer,
    warWins integer,
    warLosses integer,
    warTies integer,
    warLeague text,
    capitalLeague text not null,
    date date not Null)
    ''')
    connection.commit()

    cursor.execute('''
        create table IF NOT EXISTS members(
        tag text primary key,
        name text not null,
        clanTag text not null,
        trophies integer not null,
        league text not null,
        buildersTrophies integer not null,
        buildersLeague text not null,
        townHall integer not null,
        level integer not null,
        role text not null,
        send integer not null,
        received integer not null,
        description text,
        FOREIGN KEY(clanTag) REFERENCES clans(tag))
        ''')
    connection.commit()

    cursor.execute('''
        create table IF NOT EXISTS wars(
        clanTag text not null,
        clanName text not null,
        opponentTag text not null,
        opponentName text not null,
        clanStars integer not null,
        clanAttacks integer not null,
        clanPercent real not null,
        opponentStars integer not null,
        opponentAttacks integer not null,
        opponentPercent real not null,
        teamSize integer not null,
        startTime datetime,
        endTime datetime,
        isLeague integer not null,
        PRIMARY KEY (clanTag, opponentTag))
        ''')
    connection.commit()

    cursor.execute('''
            create table IF NOT EXISTS warAttacks(
            clanTag text not null,
            opponentTag text not null,
            memberTag text not null,
            memberName text not null,
            memberTownHall integer not null,
            mapPosition integer not null,
            attackNum integer not null,
            attacked integer not null,
            percent real not null,
            stars integer not null,
            defenderTag text not null,
            defenderName text not null,
            defenderTownHall integer not null,
            defenderPosition integer not null,
            attackOrder integer not null,
            FOREIGN KEY(clanTag) REFERENCES wars(clanTag)
            FOREIGN KEY(opponentTag) REFERENCES wars(opponentTag)
            FOREIGN KEY(memberTag) REFERENCES members(memberTag)
            PRIMARY KEY (clanTag, opponentTag,memberTag,opponentTag,attackNum))
            ''')
    connection.commit()

    cursor.execute('''
            create table IF NOT EXISTS leagueWars(
            clanTag text not null,
            season text not null,
            firstCWTag text,
            secondCWTag text,
            thirdCWTag text,
            fourthCWTag text,
            fifthCWTag text,
            sixthCWTag text,
            seventhCWTag text,
            firstCWName text,
            secondCWName text,
            thirdCWName text,
            fourthCWName text,
            fifthCWName text,
            sixthCWName text,
            seventhCWName text,
            FOREIGN KEY(firstCWTag,secondCWTag,thirdCWTag,fourthCWTag,fifthCWTag,sixthCWTag,seventhCWTag) REFERENCES wars(clanTag,clanTag,clanTag,clanTag,clanTag,clanTag,clanTag)
            PRIMARY KEY (clanTag, season))
            ''')
    connection.commit()

    cursor.execute('''
        create table IF NOT EXISTS capitalRaids(
        clanTag text not null,
        startTime date not null,
        endTime date not null,
        loot integer not null,
        raids integer not null,
        attacks integer not null,
        districtsDestroyed integer not null,
        offensiveReward integer not null,
        defensiveReward integer not null,
        FOREIGN KEY(clanTag) REFERENCES clans(tag)
        PRIMARY KEY (clanTag,startTime, endTime))
        ''')
    connection.commit()

    cursor.execute('''
            create table IF NOT EXISTS capitalRaidsMembers(
            clanTag text not null,
            startTime date not null,
            endTime date not null,
            tag text not null,
            name text not null,
            attacks integer not null,
            lootedGold integer not null,
            FOREIGN KEY(tag) REFERENCES members(memberTag)
            FOREIGN KEY(clanTag) REFERENCES clans(tag)
            PRIMARY KEY (clanTag,startTime, endTime,tag))
            ''')
    connection.commit()
    cursor.execute('''
        create table IF NOT EXISTS clanGames(
        clanTag text not null,
        startTime date not null,
        endTime date not null,
        earnedTier integer not null,
        earnedMedals integer not null,
        FOREIGN KEY(clanTag) REFERENCES clans(tag)
        PRIMARY KEY (clanTag,startTime, endTime))
        ''')
    connection.commit()

    cursor.execute('''
            create table IF NOT EXISTS clanGamesEarnings(
            clanTag text not null,
            startTime date not null,
            endTime date not null,
            memberTag text not null,
            name text not null,
            earnedMedals integer not null,
            FOREIGN KEY(memberTag) REFERENCES members(memberTag)
            FOREIGN KEY(clanTag) REFERENCES clans(tag)
            PRIMARY KEY (clanTag,startTime, endTime,memberTag))
            ''')
    connection.commit()
    connection.close()


class DummyOpponent:
    def __init__(self):
        self.tag = "Не было"
        self.name = "Не было"


class CWL:
    def __init__(self, clan, opponent, team_size, start_time, end_time, isCurrent=True):
        if isCurrent:
            self.clan = clan
            self.opponent = opponent
            self.team_size = team_size
            self.start_time = start_time
            self.end_time = end_time
            self.league_group = 1
            return

        self.clan = clan
        self.opponent = DummyOpponent()
        self.team_size = team_size
        self.start_time = start_time
        self.end_time = end_time
        self.league_group = 1

    def __str__(self):
        print(self.clan, self.opponent, self.start_time, self.end_time)



async def saveLeagueWarData(data, season, tag, client):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()

    wars = []

    for clanWarTag in list(chain.from_iterable(data)):

        clanWar = await client.getLeagueWar(clanWarTag)

        if (clanWar.clan.tag + clanWar.opponent.tag).count(tag) != 0:
            if clanWar.clan.tag.count(tag) != 0:
                wars.append(
                    CWL(clanWar.clan, clanWar.opponent, clanWar.team_size, clanWar.start_time, clanWar.end_time))
            else:
                wars.append(
                    CWL(clanWar.opponent, clanWar.clan, clanWar.team_size, clanWar.start_time, clanWar.end_time))
    for war in wars:
        saveWarData(war)

    for i in range(7 - len(wars)):
        wars.append(CWL("Не было", "Не было", 0, "0-0-0", "0-0-0", False))
    cursor.execute('''
                      insert or replace Into leagueWars (clanTag,season,firstCWTag,secondCWTag,thirdCWTag,fourthCWTag,fifthCWTag,sixthCWTag,
                      seventhCWTag,firstCWName,secondCWName,thirdCWName,fourthCWName,fifthCWName,sixthCWName,
                      seventhCWName)
                      values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                   (tag, season, wars[0].opponent.tag, wars[1].opponent.tag, wars[2].opponent.tag, wars[3].opponent.tag,
                    wars[4].opponent.tag, wars[5].opponent.tag, wars[6].opponent.tag, wars[0].opponent.name,
                    wars[1].opponent.name, wars[2].opponent.name, wars[3].opponent.name,
                    wars[4].opponent.name, wars[5].opponent.name, wars[6].opponent.name))
    connection.commit()
    connection.close()


def saveWarData(data):
    if data is None:
        return
    try:
        if data.start_time is None:
            return
    except:
        return
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    isLeague = 0
    if data.league_group is not None:
        isLeague = 1

    cursor.execute('''
                                insert or replace Into wars (clanTag,clanName,opponentTag,opponentName,clanStars,clanAttacks,clanPercent,
                                opponentStars,opponentAttacks,opponentPercent, teamSize,startTime,endTime,isLeague)
                                values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                   (data.clan.tag, data.clan.name, data.opponent.tag, data.opponent.name, data.clan.stars,
                    data.clan.attacks_used,
                    data.clan.destruction, data.opponent.stars, data.opponent.attacks_used,
                    data.opponent.destruction, data.team_size, str(data.start_time.time), str(data.end_time.time),
                    isLeague))

    cursor.execute(f"delete from warAttacks where clanTag = '{data.clan.tag}' and opponentTag = '{data.opponent.tag}'")
    connection.commit()

    # enumerate для позиции - На ЛКВ позиции по клану, а не по выбранным членам, member.map_position тогда бесполезен
    for pos, member in enumerate(data.clan.members):
        madeAttacks = len(member.attacks)
        if not member.attacks or (madeAttacks == 1 and isLeague == 0):
            for i in range(0 + madeAttacks, 2 - isLeague):
                cursor.execute('''
                                                insert or replace Into warAttacks (clanTag,opponentTag,memberTag,memberName,memberTownHall,
                                                mapPosition,attackNum,attacked,percent,stars,defenderTag,defenderName,defenderTownHall,defenderPosition,attackOrder)
                                                values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                               (data.clan.tag, data.opponent.tag, member.tag, member.name, member.town_hall,
                                pos + 1,
                                i + 1, 0, 0, 0, "Не атаковал", "Не атаковал",
                                0,
                                0, 0))
        for i, attack in enumerate(member.attacks):
            opponent = {"tag": "", "name": "", "th": "", "pos": ""}
            for enemPos, defend in enumerate(data.opponent.members):
                if defend.tag == attack.defender_tag:
                    opponent["tag"] = defend.tag
                    opponent["name"] = defend.name
                    opponent["th"] = defend.town_hall
                    opponent["pos"] = enemPos + 1
            cursor.execute('''
                              insert or replace Into warAttacks (clanTag,opponentTag,memberTag,memberName,memberTownHall,
                              mapPosition,attackNum,attacked,percent,stars,defenderTag,defenderName,defenderTownHall,defenderPosition,attackOrder)
                              values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                           (data.clan.tag, data.opponent.tag, member.tag, member.name, member.town_hall,
                            pos + 1,
                            i + 1, 1, attack.destruction, attack.stars, opponent["tag"], opponent["name"],
                            opponent["th"],
                            opponent["pos"], attack.order))
    connection.commit()
    connection.close()


def getLeagueWarData(tag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(f"select * from leagueWars where clanTag = '{tag}' order by season DESC")
    leagueData = cursor.fetchall()
    resDict = {}
    try:
        for war in leagueData:
            resDict[war[1]] = {"1CW": {"tag": war[2], "name": war[9]}, "2CW": {"tag": war[3], "name": war[10]},
                               "3CW": {"tag": war[4], "name": war[11]}, "4CW": {"tag": war[5], "name": war[12]},
                               "5CW": {"tag": war[6], "name": war[13]}, "6CW": {"tag": war[7], "name": war[14]},
                               "7CW": {"tag": war[8], "name": war[15]}}
    except:
        pass
    connection.close()
    return resDict


def getWarsData(tag, opponents=[], query=None):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    separator = "','"

    if not opponents:
        cursor.execute(f"select * from wars where clanTag = '{tag}' {query} order by datetime(startTime) DESC")
    else:
        cursor.execute(
            f"select * from wars where clanTag = '{tag}' and opponentTag in ('{separator.join([str(i) for i in opponents])}') order by datetime(startTime) DESC")
    warData = cursor.fetchall()
    resDict = {}
    try:
        for war in warData:
            resDict[war[2]] = {"clanTag": war[0], "clanName": war[1], "opponentTag": war[2],
                               "opponentName": war[3], "clanStars": war[4], "clanAttacks": war[5],
                               "clanPercent": round(war[6], 2), "opponentStars": war[7], "opponentAttacks": war[8],
                               "opponentPercent": round(war[9], 2), "teamSize": war[10], "startDate": war[11],
                               "endDate": war[12]}
    except:
        pass
    connection.close()
    return resDict


def getAttacksSummaryData(tag, opponents=[]):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    separator = "','"
    cursor.execute(
        f"select memberName from warAttacks where clanTag = '{tag}' and opponentTag in ('{separator.join([str(i) for i in opponents])}')")

    allParticipants = [i[0] for i in cursor.fetchall()]
    resData = {}
    resDict = {}
    for count, war in enumerate(opponents):
        resData[count] = {}
        cursor.execute(
            f"select memberName,stars,percent,attacked,mapPosition,attackOrder,memberTownHall,defenderTownHall,(mapPosition = defenderPosition),memberTag from warAttacks where clanTag = '{tag}' and opponentTag = '{war}'")
        warData = cursor.fetchall()
        for data in warData:
            isMirror = ""
            isTh = ""
            if not data[8]:
                isTaken, who = getIfMirrorWasBeaten(tag, war, data[4], data[5])
                if isTaken:
                    if who == data[9]:
                        isMirror = "Уже забрал зеркало"
                    else:
                        isMirror = "Зеркало забрали"
                else:
                    isMirror = "Не атаковал зеркало"
            else:
                isMirror = "Атаковал зеркало"

            if data[6] == data[7]:
                isTh = "Равный тх"
            elif data[6] > data[7]:
                isTh = "Атаковал тх слабее"
            else:
                isTh = "Атаковал тх сильнее"
            resData[count][data[0]] = {"stars": data[1], "percent": data[2], "attacked": data[3], "isMirror": isMirror,
                                       "isTh": isTh, "tag": data[9], "wasNot": 0}

        for member in allParticipants:
            resDict[member] = {}
            if member not in resData[count]:
                resData[count][member] = {"wasNot": 1}

        for war, data in resData.items():
            for name, member in data.items():
                resDict[name][war] = member
    return resDict


def getWarAttacksData(clanTag, opponentTag, query=None):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(f"select * from warAttacks where clanTag = '{clanTag}' and opponentTag = '{opponentTag}' {query}")
    warAttacksData = cursor.fetchall()
    resDict = {}
    isAttacked = {True: "Атаковал", False: "Не атаковал"}
    try:
        for attack in warAttacksData:
            resDict[attack[2] + str(attack[6]) + attack[1]] = {"memberTag": attack[2], "memberName": attack[3],
                                                               "memberTownHall": attack[4],
                                                               "mapPosition": attack[5], "attackNum": attack[6],
                                                               "attacked": isAttacked[attack[7]],
                                                               "percent": attack[8],
                                                               "stars": attack[9], "defenderTag": attack[10],
                                                               "defenderName": attack[11],
                                                               "defenderTownHall": attack[12],
                                                               "defenderPosition": attack[13],
                                                               "order": attack[14]}
    except:
        pass
    connection.close()
    return resDict


def getMembersWarAttacksData(clanTag, memberTag, query=None):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(
        f"select warAttacks.*,wars.startTime,wars.endTime from warAttacks inner join wars on wars.clanTag=warAttacks.clanTag and wars.opponentTag=warAttacks.opponentTag where warAttacks.clanTag = '{clanTag}' and warAttacks.memberTag = '{memberTag}' {query} order by datetime(wars.startTime) DESC")
    warAttacksData = cursor.fetchall()
    resDict = {}
    isAttacked = {True: "Атаковал", False: "Не атаковал"}
    try:
        for attack in warAttacksData:
            resDict[str(attack[6]) + attack[1]] = {"opponentTag": attack[1], "memberTag": attack[2],
                                                   "memberName": attack[3],
                                                   "memberTownHall": attack[4],
                                                   "mapPosition": attack[5], "attackNum": attack[6],
                                                   "attacked": isAttacked[attack[7]],
                                                   "percent": attack[8],
                                                   "stars": attack[9], "defenderTag": attack[10],
                                                   "defenderName": attack[11],
                                                   "defenderTownHall": attack[12], "defenderPosition": attack[13],
                                                   "order": attack[14], "startTime": attack[15], "endTime": attack[16]}
    except:
        pass
    connection.close()
    return resDict


def saveCapitalRaidData(data, tag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()

    for raid in data:
        cursor.execute('''
                          insert or replace Into capitalRaids (clanTag,startTime,endTime,loot,raids,attacks,districtsDestroyed,offensiveReward,defensiveReward)
                          values (?,?,?,?,?,?,?,?,?)''',
                       (tag, str(datetime.datetime.strptime(str(raid.start_time.time), "%Y-%m-%d %H:%M:%S").date()),
                        str(datetime.datetime.strptime(str(raid.end_time.time), "%Y-%m-%d %H:%M:%S").date()),
                        raid.total_loot,
                        raid.completed_raid_count,
                        raid.attack_count, raid.destroyed_district_count, raid.offensive_reward, raid.defensive_reward))

        for member in raid.members:
            cursor.execute('''
                              insert or replace Into capitalRaidsMembers (clanTag,startTime,endTime,tag,name,attacks,lootedGold)
                              values (?,?,?,?,?,?,?)''',
                           (tag, str(datetime.datetime.strptime(str(raid.start_time.time), "%Y-%m-%d %H:%M:%S").date()),
                            str(datetime.datetime.strptime(str(raid.end_time.time), "%Y-%m-%d %H:%M:%S").date()),
                            member.tag,
                            member.name, member.attack_count, member.capital_resources_looted))

    connection.commit()
    connection.close()


def saveClanGameData(data, tag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()

    for clanGame in data.values():
        cursor.execute('''
                          insert or replace Into clanGames (clanTag,startTime,endTime,earnedTier,earnedMedals)
                          values (?,?,?,?,?)''',
                       (tag, str(clanGame["startTime"]), str(clanGame["endTime"]), clanGame["earnedTier"],
                        clanGame["earnedMedals"]))

    connection.commit()
    connection.close()


def saveClanGameMemberData(data, tag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()

    for member in data.values():
        cursor.execute('''
                          insert or replace Into clanGamesEarnings (clanTag,startTime,endTime,memberTag,name,earnedMedals)
                          values (?,?,?,?,?,?)''',
                       (tag, str(member["startTime"]), str(member["endTime"]), member["tag"], member["name"],
                        member["earnedMedals"]))

    connection.commit()
    connection.close()


def deleteClanGameData(tag, start, end):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(f"delete from clanGames where startTime = '{start}' and endTime = '{end}' and clanTag = '{tag}' ")
    cursor.execute(
        f"delete from clanGamesEarnings where startTime = '{start}' and endTime = '{end}' and clanTag = '{tag}'")
    connection.commit()
    connection.close()


def deleteClanGameMemberData(tag, start, end, member):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(
        f"delete from clanGamesEarnings where startTime = '{start}' and endTime = '{end}' and clanTag = '{tag}' and memberTag = '{member}'")
    connection.commit()
    connection.close()


def getClanGamesData(tag, query=None):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(f"select * from clanGames where clanTag = '{tag}' {query} order by datetime(startTime) DESC")
    gameData = cursor.fetchall()
    resDict = {}
    try:
        for game in gameData:
            resDict[game[1] + game[2]] = {"startTime": game[1], "endTime": game[2], "earnedTier": game[3],
                                          "earnedMedals": game[4]}
    except:
        pass
    connection.close()
    return resDict


def getClanGamesMembersData(tag, startTime, endTime, query=None):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(
        f"select * from clanGamesEarnings where startTime = '{startTime}' and endTime = '{endTime}' and clanTag = '{tag}' {query}")
    gameData = cursor.fetchall()
    resDict = {}
    try:
        for member in gameData:
            resDict[member[3]] = {"tag": member[3], "name": member[4], "earnedMedals": member[5]}
    except:
        pass
    connection.close()
    return resDict


def getCapitalData(tag, query=""):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()

    cursor.execute(f"select * from capitalRaids where clanTag = '{tag}' {query} order by datetime(startTime) DESC")
    raidData = cursor.fetchall()
    resDict = {}
    try:
        for raid in raidData:
            resDict[raid[1] + raid[2]] = {"startTime": raid[1], "endTime": raid[2], "loot": raid[3],
                                          "raids": raid[4], "attacks": raid[5], "districtsDestroyed": raid[6],
                                          "offensiveReward": raid[7], "defensiveReward": raid[8]}
    except:
        pass
    connection.close()
    return resDict


def getCapitalRaidDetailsData(tag, startTime, endTime, query=""):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(
        f"select * from capitalRaidsMembers where startTime = '{startTime}' and endTime = '{endTime}' and clanTag = '{tag}' {query}")
    raidData = cursor.fetchall()
    resDict = {}
    try:
        for raid in raidData:
            resDict[raid[3]] = {"tag": raid[3], "name": raid[4], "attacks": raid[5], "loot": raid[6]}
    except:
        pass
    connection.close()
    return resDict


def getWarAttacksSummary(tag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(
        f"select warAttacks.memberTag,warAttacks.memberName,avg(warAttacks.stars),avg(warAttacks.percent),sum(warAttacks.attacked),count(warAttacks.attacked)-sum(warAttacks.attacked),members.role from warAttacks inner join members on warAttacks.memberTag = members.tag where warAttacks.clanTag = '{tag}' group by warAttacks.memberTag having count(warAttacks.memberTag) >= 10 order by avg(warAttacks.stars) DESC")
    resData = cursor.fetchall()
    resDict = {}
    try:
        for member in resData:
            resDict[member[0]] = {"tag": member[0], "name": member[1], "stars": member[2], "percents": member[3],
                                  "attacks": member[4], "missed": member[5], "role": member[6]}
    except:
        pass
    connection.close()
    return resDict


def getClanGamesStat(clanTag, memberTag, query=None):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    resDict = {'games': {}}

    cursor.execute(
        f"select * from clanGamesEarnings where memberTag = '{memberTag}' and clanTag = '{clanTag}' {query} order by datetime(startTime) DESC")
    games = cursor.fetchall()
    medals = []

    try:
        for game in games:
            medals.append(game[5])
            resDict['games'][str(game[1])] = {"start": game[1], "end": game[2], "earnedMedals": game[5]}
    except:
        pass
    resDict['count'] = len(resDict['games'])
    if len(medals) != 0:
        resDict['avg'] = sum(medals) / len(medals)
    else:
        resDict['avg'] = 0
    connection.close()
    return resDict


def getClanCapitalStat(clanTag, memberTag, query=None):
    if query is None: query = ""
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    resDict = {'raids': {}}

    cursor.execute(
        f"select * from capitalRaidsMembers where tag = '{memberTag}' and clanTag = '{clanTag}' {query} order by datetime(startTime) DESC")
    games = cursor.fetchall()
    gold = []
    attacks = []
    try:
        for game in games:
            gold.append(game[6])
            attacks.append(game[5])
            resDict['raids'][str(game[1])] = {"start": game[1], "end": game[2], "attacks": game[5], "gold": game[6]}
    except:
        pass
    resDict['count'] = len(resDict['raids'])
    if len(gold) != 0:
        resDict['avgAttacks'] = sum(attacks) / len(attacks)
        resDict['avgGold'] = sum(gold) / len(gold)
    else:
        resDict['avgGold'] = 0
        resDict['avgAttacks'] = 0

    connection.close()
    return resDict


def getWarAttackCountStat(clanTag, memberTag):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()

    cursor.execute(
        f"select count(*) from warAttacks where memberTag = '{memberTag}' and clanTag = '{clanTag}'")
    warAttacksCount = cursor.fetchall()[0][0]

    cursor.execute(
        f"select count(opponentTag) from warAttacks where memberTag = '{memberTag}' and clanTag = '{clanTag}' group by opponentTag")
    wasInWars = len(cursor.fetchall())

    cursor.execute(
        f"select wars.opponentTag from wars join warAttacks on wars.opponentTag=warAttacks.opponentTag where wars.endTime > datetime('now') and warAttacks.memberTag = '{memberTag}'")
    isWar = cursor.fetchall()
    try:
        opponent = isWar[0][0]
        isCurrentlyInWar = 1
    except:
        opponent = ""
        isCurrentlyInWar = 0

    cursor.execute(
        f"select * from warAttacks where memberTag = '{memberTag}' and clanTag = '{clanTag}' and ((opponentTag = '{opponent}' and attacked = 1) or opponentTag != '{opponent}')")
    warAttacks = cursor.fetchall()

    cursor.execute(
        f"select count(*) from wars")
    wars = cursor.fetchall()[0][0]

    resDict = {"wars": wars, "warAttacksCount": warAttacksCount, "wasInWars": wasInWars,
               "isCurrentlyInWar": isCurrentlyInWar, "warAttacks": warAttacks}
    connection.close()
    return resDict


def getIfMirrorWasBeaten(calnTag, opponentTag, pos, order):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    cursor.execute(
        f"select * from warAttacks where opponentTag = '{opponentTag}' and clanTag = '{calnTag}' and defenderPosition={pos}")
    for attack in cursor.fetchall():
        if attack[14] < order:
            connection.close()
            return True, attack[2]
    connection.close()
    return False, ""


# TODO Если делать через having то не имеет смысла И/ИЛИ с другими условиями необходимо сделать запрос в where который
#  может определять было зеркало атакованною или нет и было ли атакованно этим же членом
# Задача селектора по зеркалу
# Option("mirror", "Зеркало", {"row": , "column": }, "selector",["Не выбрано", "Атаковал Зеркало", "Не атаковал зеркало", "Зеркало было атаковано", "Сам забрал зеркало"])
def getMirorQuery(operators, query, values):
    if values['data'] == "Атаковал Зеркало":
        return f"{operators[values['operator']] if query[-1] != '(' else ''} warAttacks.mapPosition = warAttacks.defenderPosition"
    else:
        return f"{operators[values['operator']] if query[-1] != '(' else ''} (warAttacks.mapPosition != warAttacks.defenderPosition" \
               f" and warAttacks.attackOrder {'!=' if values['data'] == 'Не атаковал зеркало' else '='} (select b.attackOrder from warAttacks b where b.defenderPosition=warAttacks.defenderPosition" \
               f" and b.opponentTag = warAttacks.opponentTag and b.clanTag = warAttacks.clanTag {'and b.memberTag = warAttacks.memberTag' if values['data'] == 'Сам забрал зеркало' else ''}))"


# Чтобы можно было использовать и/или с расчетными велечинами в условии с не расчетными величинами
def getHavingQuery(operators, name, values, funk, query):
    if name == "starsAVG":
        return f"{operators if query[-1] != '(' else ''} members.tag in (select c.memberTag from warAttacks c where c.clanTag='#2G2YJLGQY' group by c.memberTag having avg(c.stars) {funk} {values})"
    elif name == "percentAVG":
        return f"{operators if query[-1] != '(' else ''} members.tag in (select d.memberTag from warAttacks d where d.clanTag=warAttacks.clanTag group by d.memberTag having avg(d.percent) {funk} {values})"
    elif name == "attacksMissed":
        return f"{operators if query[-1] != '(' else ''} members.tag in (select e.memberTag from warAttacks e where e.clanTag=warAttacks.clanTag group by e.memberTag having count(e.memberTag) - sum(e.attacked) {funk} {values})"
    elif name == "attacks":
        return f"{operators if query[-1] != '(' else ''} members.tag in (select f.memberTag from warAttacks f where f.clanTag=warAttacks.clanTag group by f.memberTag having sum(f.attacked) {funk} {values})"
    elif name == "lootedGoldAVG":
        return f"{operators if query[-1] != '(' else ''} members.tag in (select g.tag from capitalRaidsMembers g where g.clanTag=capitalRaidsMembers.clanTag group by g.tag having avg(g.lootedGold) {funk} {values})"
    elif name == "attacksAVG":
        return f"{operators if query[-1] != '(' else ''} members.tag in (select h.tag from capitalRaidsMembers h where h.clanTag=capitalRaidsMembers.clanTag group by h.tag having avg(h.attacks) {funk} {values})"
    elif name == "earnedMedalsAVG":
        return f"{operators if query[-1] != '(' else ''} members.tag in (select j.memberTag from clanGamesEarnings j where j.clanTag=clanGamesEarnings.clanTag group by j.memberTag having avg(j.earnedMedals) {funk} {values})"


def clanSearch(tag, data, period):
    connection = sqlite3.connect('clanDatabase.db')
    cursor = connection.cursor()
    query = ""
    query += f"select members.tag,members.name,"
    resData = {"columns": ["tag", "name"]}
    operators = {"И": "AND", "ИЛИ": "OR"}
    # Выборка по member в любом случае для вывода данных по членам на данный момент, даже если хранится инфа по кикнутым
    isUsedTable = {"war": 0, "cg": 0, "cc": 0}

    for i in data["order"]:
        if resData["columns"].count(i['name']) == 0 and i["name"] in (
                "opponentTh", "mirror", "attacksMissed", "attacks", "percentAVG", "starsAVG"):
            isUsedTable["war"] = 1
            if i['name'].count('AVG') != 0:
                query += f" avg(warAttacks.{i['name'].replace('AVG', '')}) as {i['name']},"
            elif i['name'] == "opponentTh":
                if i["data"] == "Не выбрано": continue
                query += f" sum(warAttacks.attacked),"
            elif i['name'] == "attacksMissed":
                query += f" count(warAttacks.memberTag) - sum(warAttacks.attacked) as attacksMissed,"
            elif i['name'] == "attacks":
                query += f" sum(warAttacks.attacked) as attacks,"
            elif i['name'] == "mirror":
                if i["data"] == "Не выбрано": continue
                query += f" sum(warAttacks.attacked),"
            else:
                query += f" warAttacks.{i['name']},"

        elif resData["columns"].count(i['name']) == 0 and i["name"] in (
                "received", "send", "role", "level", "townHall"):
            query += f"members.{i['name']},"

        elif resData["columns"].count(i['name']) == 0 and i["name"] in ("lootedGoldAVG", "attacksAVG"):
            isUsedTable["cc"] = 1
            if i['name'] == "lootedGoldAVG":
                query += f" avg(capitalRaidsMembers.{i['name'].replace('AVG', '')}) as {i['name']},"
            elif i['name'] == "attacksAVG":
                query += f" avg(capitalRaidsMembers.{i['name'].replace('AVG', '')}) as {i['name']},"

        elif resData["columns"].count(i['name']) == 0 and i["name"] in "earnedMedalsAVG":
            isUsedTable["cg"] = 1
            if i['name'] == "earnedMedalsAVG":
                query += f" avg(clanGamesEarnings.{i['name'].replace('AVG', '')}) as {i['name']},"

        resData["columns"].append(i['name'])

    query = query[:-1]
    query += " from members "

    if isUsedTable["war"]:
        query += f" inner join warAttacks on members.tag=warAttacks.memberTag "
        if period[0] != '' or period[1] != '':
            query += f" left join wars on warAttacks.opponentTag=wars.opponentTag and warAttacks.clanTag=wars.clanTag"

    if isUsedTable["cg"]:
        query += f" inner join clanGamesEarnings on members.tag=clanGamesEarnings.memberTag "

    if isUsedTable["cc"]:
        query += f" inner join capitalRaidsMembers on members.tag=capitalRaidsMembers.tag "

    query += f" where members.clanTag='{tag}' "
    isWhereRequeried = 0
    for i in resData["columns"]:
        if i != "attacksMissed" and i != "attacks" and i.count("AVG") == 0:
            isWhereRequeried += 1
    if isWhereRequeried > 2:
        query += " and("

    endingCols = []
    attackedValues = {"Атаковал": 1, "Не атаковал": 0}
    thValues = {"Атаковал равного": "=", "Атаковал слабого": "<", "Атаковал сильного": ">"}

    for values in data["order"]:

        if not values["data"].replace(" ", "").replace(".", "").replace(",", "").isnumeric() and values[
            "funk"] != "selector":
            continue
        if values["funk"] == "":
            values["funk"] = "="

        if values['name'] in ("received", "send", "role", "level", "townHall"):
            if values["funk"] == "selector" and values["data"] != "Не выбрано":
                query += f"{operators[values['operator']] if query[-1] != '(' else ''} members.{values['name']} = '{values['data']}' "
                continue
            query += f"{operators[values['operator']] if query[-1] != '(' else ''} members.{values['name']} {values['funk']} {values['data']} "

        elif values['name'] in ("opponentTh", "mirror", "attacksMissed", "attacks", "percentAVG", "starsAVG"):
            if values["funk"] == "selector" and values["data"] != "Не выбрано":
                if values['name'] == "attacked":
                    query += f"{operators[values['operator']] if query[-1] != '(' else ''} warAttacks.{values['name']} = '{attackedValues[values['data']]}' "
                elif values['name'] == "opponentTh":
                    query += f"{operators[values['operator']] if query[-1] != '(' else ''} warAttacks.memberTownHall {thValues[values['data']]} warAttacks.defenderTownHall "
                elif values['name'] == "mirror":

                    query += getMirorQuery(operators, query, values)
                continue
            if values['name'].count('AVG') != 0 or values['name'] in ("attacksMissed", "attacks"):
                query += getHavingQuery(operators[values['operator']], values['name'], values['data'], values['funk'],
                                        query)
            else:
                query += f"{operators[values['operator']] if query[-1] != '(' else ''} warAttacks.{values['name']} {values['funk']} {values['data']} "

        else:
            if values['name'].count('AVG') != 0:
                query += getHavingQuery(operators[values['operator']], values['name'], values['data'], values['funk'],
                                        query)

    if period[0] != '' or period[1] != '':
        if isUsedTable["war"]:
            query += f"and (date(wars.startTime) between '{'0000-00-00' if period[0] == '' else period[0]}' and '{'9999-12-31' if period[1] == '' else period[1]}' or date(wars.endTime) between '{'0000-00-00' if period[0] == '' else period[0]}' and '{'9999-12-31' if period[1] == '' else period[1]}')"

        if isUsedTable["cg"]:
            query += f"and (date(clanGamesEarnings.startTime) between '{'0000-00-00' if period[0] == '' else period[0]}' and '{'9999-12-31' if period[1] == '' else period[1]}' or date(clanGamesEarnings.endTime) between '{'0000-00-00' if period[0] == '' else period[0]}' and '{'9999-12-31' if period[1] == '' else period[1]}')"

        if isUsedTable["cc"]:
            query += f"and (date(capitalRaidsMembers.startTime) between '{'0000-00-00' if period[0] == '' else period[0]}' and '{'9999-12-31' if period[1] == '' else period[1]}' or date(capitalRaidsMembers.endTime) between '{'0000-00-00' if period[0] == '' else period[0]}' and '{'9999-12-31' if period[1] == '' else period[1]}')"

    if isWhereRequeried > 2:
        query += ")"

    query = query.replace("and()", "")
    possibleCols = {"starsAVG", "percentAVG", "attacksMissed", "attacks", "mirror", "opponentTh", "attacksAVG",
                    "lootedGoldAVG", "earnedMedalsAVG"}

    if possibleCols.intersection(set(resData["columns"])):
        query += " group by members.tag"

    cursor.execute(query)

    for member in cursor.fetchall():
        resData[member[0]] = member
    connection.close()
    return resData


def dumpDataBase():
    try:
        Path("Databases/copy").mkdir(parents=True, exist_ok=True)
        shutil.copy(f'clanDatabase.db', f'Databases/copy/clanDatabase_{time.strftime("%Y_%m_%d-%H_%M_%S")}.db')
        return f"База выгружена в: \n {os.path.abspath(f'Databases/copy/')}"
    except:
        return f"Ошибка выгрузки базы данных"


def loadDataBase(path):
    try:
        backupDatabase()
    except:
        return "Ошибка сохранения бэкапа, при загрузке БД"
    try:
        conection = sqlite3.connect('clanDatabase.db')
        cursor = conection.cursor()
        cursor.execute(f"attach database '{path}' as newDB")
        cursor.execute("insert or replace Into main.clans select * from newDB.clans")
        cursor.execute("insert or replace Into main.members select * from newDB.members")
        cursor.execute("insert or replace Into main.wars select * from newDB.wars")
        cursor.execute("insert or replace Into main.warAttacks select * from newDB.warAttacks")
        cursor.execute("insert or replace Into main.leagueWars select * from newDB.leagueWars")
        cursor.execute("insert or replace Into main.capitalRaids select * from newDB.capitalRaids")
        cursor.execute("insert or replace Into main.capitalRaidsMembers select * from newDB.capitalRaidsMembers")
        cursor.execute("insert or replace Into main.clanGames select * from newDB.clanGames")
        cursor.execute("insert or replace Into main.clanGamesEarnings select * from newDB.clanGamesEarnings")
        conection.commit()
        conection.close()
        return "База загружена\nнайдите или обновите клан для отображения"
    except:
        return "Ошибка загрузки базы данных"


def backupDatabase():
    Path(f'Databases/backups/{time.strftime("%Y_%m")}').mkdir(parents=True, exist_ok=True)
    # сохранение 1 бэкапа за месяц
    if settings.getSetting("lastBackupMonth") != time.strftime("%Y_%m"):
        backups = os.listdir(f'Databases/backups/{settings.getSetting("lastBackupMonth")}')
        backCount = len(backups)
        for k, i in enumerate(backups):
            if k == backCount - 1: break
            os.remove(i)

    settings.saveSetting("lastBackupMonth", time.strftime("%Y_%m"))

    shutil.copy(f'clanDatabase.db',
                f'Databases/backups/{time.strftime("%Y_%m")}/clanDatabase_backup_{time.strftime("%Y_%m_%d-%H_%M_%S")}.db')

# createDataBase()
