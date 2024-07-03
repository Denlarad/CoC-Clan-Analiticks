import asyncio
import datetime
import sqlite3

import coc
import dataProceesing


async def main():
    async with coc.Client() as coc_client:
        try:
            await coc_client.login("", "")
        except coc.InvalidCredentials as error:
            exit(error)

        clan = await coc_client.get_current_war("#2G2YJLGQY")
        print(clan.league_group.rounds)

        war = await  coc_client.get_league_war(clan.league_group.rounds[2][3])
        for k, i in enumerate(war.clan.members):
            print(f"{i.name}. Тх: {i.town_hall} Позиция: {k + 1}")


def test():
    connection = sqlite3.connect("clanDatabase.db")

    cursor = connection.cursor()
    cursor.execute(f'''PRAGMA table_info(leagueWars);''')
    for i in cursor.fetchall():
        print(i)
    connection.close()
# asyncio.get_event_loop().run_until_complete(main())
test()
