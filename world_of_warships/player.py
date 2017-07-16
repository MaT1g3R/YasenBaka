from logging import WARN
from typing import Optional

from discord import Embed
from wowspy import Region, WowsAsync

from scripts.helpers import get_date
from world_of_warships import _CONVERT_REGION
from world_of_warships.embed_builder import get_shame_embed
from world_of_warships.wtr import choose_colour, wtr_absolute


class Player:
    def __init__(self, id_: str, region: Region, logger,
                 stats=None, recent_stats=None, recent_date=None,
                 ship_stats=None):
        """
        :param id_: the player id.
        :param region: the player region.
        :param logger: the logger.

        :param stats: the player stats, optional.
        :param recent_stats: player recent stats, optional.
        :param recent_date: player recent stats date, optional.
        :param ship_stats: player ship stats, optional.
        """
        self.region = region
        self.player_id: str = id_
        self.region_db, self.region_today = _CONVERT_REGION[region]
        self.stats = stats
        self.recent_stats = recent_stats
        self.recent_date = recent_date
        self.ship_stats = ship_stats
        self.logger = logger
        self.nick = stats.get('nickname', None) if stats else None
        self.hidden = False
        self.wtr = None
        self.clan = None
        self.__embed = None

    @property
    def warships_today_sig(self) -> str:
        """
        :return: Player warshipstoday signiture url.
        """
        return (f'http://{self.region_today}.warshipstoday.com/signature/'
                f'{self.player_id}/dark.png')

    @property
    def warships_today_url(self) -> str:
        """
        :return: Player profile url on warshipstoday.
        """
        return (f'https://{self.region_today}.warships.today/'
                f'player/{self.player_id}/{self.nick}')

    async def get_embed(self, wows_api: WowsAsync,
                        expected, coeff, ship_dict) -> Optional[Embed]:
        """
        Get player stats embed.
        :param wows_api: the WowsAsync instance.
        :param expected: the expected server average.
        :param coeff: the coefficents used in WTR calculation.
        :param ship_dict: a dict of {ship_id: tier}
        :return: player stats embed if any.
        """

        if self.hidden:
            return
        updated = await self.update(wows_api, expected, coeff, ship_dict)
        if not updated and self.__embed is not None:
            return self.__embed
        colour = choose_colour(self.wtr)
        tmp_embed = Embed(colour=colour)
        embed = get_shame_embed(
            tmp_embed, self.stats, self.wtr, self.nick, self.clan,
            self.recent_stats, self.recent_date, self.warships_today_url
        )
        self.__embed = embed
        return embed

    async def fetch(self, wows_api: WowsAsync) -> Optional[tuple]:
        """
        Fetch the all time player data.
        :param wows_api: the WowsAsync instance.
        :return: the all time player stats.
        """
        try:
            alltime_resp = await wows_api.player_personal_data(
                self.region, int(self.player_id),
                fields='hidden_profile,statistics.pvp,nickname',
                language='en'
            )
        except Exception as e:
            self.logger.log(WARN, str(e))
            return None, None
        try:
            data = alltime_resp['data'][self.player_id]
            if not data:
                return None, None
        except (KeyError, TypeError):
            return None, None
        if data.get('hidden_profile', False):
            self.hidden = True
            return None, data.get('nickname', None)
        try:
            return data['statistics']['pvp'], data['nickname']
        except (KeyError, TypeError):
            return None, None

    async def fetch_recent(self, wows_api: WowsAsync) -> tuple:
        """
        Fetch the recent player stats.
        :param wows_api: the WowsAsync instance.
        :return: a tuple of (recent player stats, stats date)
        """
        dates = [get_date(diff) for diff in range(8)]
        try:
            resp = await wows_api.player_statistics_by_date(
                self.region, int(self.player_id), dates=','.join(dates),
                language='en', fields='pvp'
            )
            if not resp:
                return None, None
        except Exception as e:
            self.logger.log(WARN, str(e))
            return None, None
        try:
            date_stats = resp['data'][self.player_id]['pvp']
            if not date_stats:
                return None, None
        except (KeyError, TypeError):
            return None, None
        recent = {}
        final_date = None
        for date in dates:
            stats = date_stats.get(date, None)
            if not stats:
                continue
            battle_diff = self.stats.get('battles', 0) - stats.get('battles', 0)
            if battle_diff:
                recent = stats
                final_date = date
                break
        res = {}
        for key, val in recent.items():
            if key in self.stats:
                diff = self.stats[key] - val if isinstance(val, int) else val
                res[key] = diff
        return res, final_date

    async def fetch_ship_stats(self, wows_api: WowsAsync) -> Optional[dict]:
        """
        Fetch the player stats break down by ships.
        :param wows_api: the WowsAsync instance.
        :return: the player stats break down by ships.
        """
        try:
            resp = await wows_api.statistics_of_players_ships(
                self.region, account_id=int(self.player_id), language='en',
                fields='pvp.battles,pvp.damage_dealt,pvp.wins,'
                       'pvp.survived_battles,pvp.torpedoes,pvp.frags,'
                       'pvp.main_battery,pvp.second_battery,pvp.ships_spotted,'
                       'pvp.planes_killed,pvp.xp,pvp.capture_points,'
                       'pvp.dropped_capture_points,ship_id'
            )
            if not resp:
                return
        except Exception as e:
            self.logger.log(WARN, str(e))
            return
        try:
            data = resp['data'][self.player_id]
        except (KeyError, TypeError):
            return
        return {entry['ship_id']: entry['pvp'] for entry in data}

    async def fetch_clan(self, wows_api: WowsAsync) -> Optional[str]:
        """
        Fetch player's clan name.
        :param wows_api: the WowsAsync instance.
        :return: the clan name, if any.
        """
        try:
            clan = await wows_api.player_clan_data(
                self.region, int(self.player_id), extra='clan',
                fields='clan.name', language='en'
            )
        except Exception as e:
            self.logger.log(WARN, str(e))
            return
        try:
            return clan['data'][str(self.player_id)]['clan']['name']
        except (KeyError, TypeError):
            return

    async def update(self, wows_api: WowsAsync,
                     expected, coeff, ship_dict) -> bool:
        """
        Update the player stats.
        :param wows_api: the WowsAsync instance.
        :param expected: the expected server average.
        :param coeff: the coefficents used in WTR calculation.
        :param ship_dict: a dict of {ship_id: tier}
        :return: True if updated.
        """
        all_time, nick = await self.fetch(wows_api)
        clan = await self.fetch_clan(wows_api)
        if not all_time:
            return False
        name_change = self.nick != nick or self.clan != clan
        self.nick = nick
        self.clan = clan
        if self.stats and all_time.get('battles') == self.stats.get('battles'):
            return name_change
        self.stats = all_time
        try:
            recent_stats, recent_date = await self.fetch_recent(wows_api)
        except Exception as e:
            self.logger.log(WARN, str(e))
            recent_stats, recent_date = None, None
        if recent_stats:
            self.recent_stats = recent_stats
        if recent_date:
            self.recent_date = recent_date
        ship_stats = await self.fetch_ship_stats(wows_api)
        if ship_stats:
            self.ship_stats = ship_stats
        if ship_stats:
            self.wtr = await wtr_absolute(
                expected, coeff, ship_stats, ship_dict
            )
        return True
