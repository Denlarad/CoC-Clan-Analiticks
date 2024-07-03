import asyncio
import coc


class RequestClient:

    async def create(self, email, password):
        self.cocClient = coc.Client()
        try:
            await self.cocClient.login(email, password)
        except coc.InvalidCredentials as error:
            exit(error)

    async def getClanInfo(self, tag):
        try:
            if tag[0] != "#": tag = "#" + tag
            clan = await self.cocClient.get_clan(tag)
            return clan
        except:
            return False

    async def getWarInfo(self, tag):
        try:
            if tag[0] != "#": tag = "#" + tag
            war = await self.cocClient.get_current_war(tag)
            return war
        except:
            return False

    async def getWarLeagueInfo(self, tag):
        try:
            if tag[0] != "#": tag = "#" + tag
            war = await self.cocClient.get_current_war(tag)
            return [war.league_group.rounds,war.league_group.season]
        except:
            return False

    async def getLeagueWar(self, warTag):
        try:
            if warTag[0] != "#": warTag = "#" + warTag
            war = await self.cocClient.get_league_war(warTag)
            return war
        except:
            return False

    async def getCapitalRaids(self, tag):
        try:
            if tag[0] != "#": tag = "#" + tag
            raids = await self.cocClient.get_raid_log(tag)
            return raids
        except:
            return False