from asyncio import sleep
from datetime import date
from json import dumps, load
from pathlib import Path
from typing import List, Optional

from aiohttp_wrapper import SessionManager
from discord import Embed
from wowspy import Region, WowsAsync

from data import data_path
from scripts.helpers import combine_objects
from world_of_warships.embed_builder import build_clan_embed
from world_of_warships.player import Player
from world_of_warships.wtr import CONVERT_REGION, choose_colour, \
    coeff_all_region, get_ship_dicts, wtr_absolute


class WowsManager:
    __slots__ = ('logger', 'wows_api', 'expected_and_coeff', 'ship_dict',
                 'players', 'e_and_c_path', 'ship_path')

    def __init__(self, wows_api: WowsAsync, logger):
        """
        :param wows_api: WowsAsync instance.
        :param logger: the logger.
        """
        self.logger = logger
        self.wows_api = wows_api
        self.expected_and_coeff = None
        self.ship_dict = None
        self.players = {
            Region.NA: {},
            Region.EU: {},
            Region.RU: {},
            Region.AS: {}
        }
        self.e_and_c_path = data_path.joinpath('expected_and_coeff.json')
        self.ship_path = data_path.joinpath('ship_dict.json')

    @classmethod
    async def wows_manager(cls, session_manager: SessionManager,
                           wows_api: WowsAsync, logger):
        """
        Get an instance of WowsManager. Use this instead of __init__
        :param session_manager: SessionManager instance.
        :param wows_api: WowsAsync instance.
        :param logger: the logger.
        :return: a new instance of WowsManager
        """
        instance = cls(wows_api, logger)
        await instance.update_data(session_manager)
        return instance

    def expected(self, region):
        return self.expected_and_coeff[CONVERT_REGION[region]]['expected']

    def coeff(self, region):
        return self.expected_and_coeff[CONVERT_REGION[region]]['coefficients']

    def check_data(self):
        return self.expected_and_coeff and self.ship_dict

    async def __update_data(self, coro, path: Path) -> Optional[dict]:
        """
        Helper method to update data used in wtr calculations.
        Dumps the new data to file if new data if fetched.
        :param coro: the coroutine to be called.
        :param path: the path to the json file.
        :return: the new data if any.
        """
        try:
            data = await coro
        except Exception as e:
            self.logger.warn(str(e))
        else:
            with path.open('w+') as f:
                f.write(dumps(data))
            return data

    async def update_data(self, session_manager: SessionManager):
        """
        Update data used for wtr calculations.
        :param session_manager: SessionManager instance.
        """
        generic = 'Updating data from'
        self.logger.info(f'{generic} Warships Today.')
        coeff = await self.__update_data(
            coeff_all_region(session_manager), self.e_and_c_path
        )
        if coeff:
            self.expected_and_coeff = coeff
            self.logger.info(f'{generic} Warships Today success.')
        else:
            self.logger.warn(f'{generic} from Warships Today failed.')
            with self.e_and_c_path.open() as f:
                self.expected_and_coeff = load(f)

        assert self.expected_and_coeff is not None

        self.logger.info(f'{generic} from Wargaming.')
        ships = await self.__update_data(
            get_ship_dicts(self.wows_api), self.ship_path
        )
        if ships:
            self.ship_dict = ships
            self.logger.info(f'{generic} from Wargaming success.')
        else:
            self.logger.warn(f'{generic} from Wargaming failed.')

    async def get_player(self, region: Region, id_: str) -> Player:
        """
        Get a player by region and id.
        :param region: the player region.
        :param id_: the player id.
        :return: the player.
        """
        if id_ not in self.players[region]:
            self.players[region][id_] = Player(region, id_, self.logger)
        player = self.players[region][id_]
        while player.updating:
            await sleep(0)
        return player

    async def get_clan_players(self, region: Region, ids: List[int]):
        """
        Get a list of players by ids.
        :param region: the region.
        :param ids: the list of ids.
        :return: the list of Player if they have ship stats.
        """
        players = []
        for id_ in ids:
            new = await self.get_player(region, str(id_))
            new.ship_stats = await new.fetch_ship_stats(self.wows_api)
            if new.ship_stats:
                players.append(new)
        for player in players:
            player.updating = True
        return players

    async def clan_meta(self, region: Region, id_: int) -> Optional[dict]:
        """
        Get clan meta data.
        :param region: the region.
        :param id_: the clan id.
        :return: the clan meta data if any.
        """
        try:
            resp = await self.wows_api.clan_details(
                region, id_, language='en',
                fields='creator_name,description,name,tag,members_ids,'
                       'members_count,is_clan_disbanded,leader_name,created_at'
            )
        except Exception as e:
            self.logger.warn(str(e))
            return
        else:
            return resp.get('data', {}).get(str(id_))

    async def clan_embed(self, region, players: List[Player],
                         clan_meta: dict) -> Embed:
        """
        Generate a clan embed.
        :param region: the region.
        :param players: the list of Players in the clan.
        :param clan_meta: the clan meta data.
        :return: the clan Embed.
        """
        clan_sats = combine_objects(*[p.ship_stats for p in players])
        wtr = await wtr_absolute(
            self.expected(region),
            self.coeff(region),
            clan_sats,
            self.ship_dict[region.name]
        )
        name = clan_meta.get('name', 'None') or 'None'
        description = clan_meta.get('description', 'None') or 'None'
        tag = clan_meta.get('tag', 'None') or 'None'
        active = not clan_meta.get('is_clan_disbanded', True)
        created_at = clan_meta.get('created_at', None)
        creation_date = (date.fromtimestamp(created_at).strftime('%Y-%m-%d')
                         if created_at else 'Unknown')
        creator_name = clan_meta.get('creator_name', 'None') or 'None'
        leader_name = clan_meta.get('leader_name', 'None') or 'None'
        member_count = clan_meta.get('members_count', 'None') or 'None'
        colour = choose_colour(wtr)
        embed = build_clan_embed(
            Embed(colour=colour), combine_objects(*list(clan_sats.values())),
            name, description, wtr, tag, active, creation_date,
            creator_name, leader_name, member_count
        )
        return embed

    async def player_embed(self, region: Region, player_id):
        """
        Get an embed for player stats.
        :param region: the region.
        :param player_id: the player id.
        :return: the Embed or a warships today signiture for fallback.
        """
        player = await self.get_player(region, str(player_id))
        embed = await player.get_embed(
            self.wows_api, self.expected(region), self.coeff(region),
            self.ship_dict[region.name]
        )
        return embed or player.warships_today_sig

    async def cache_players(self, region: Region, players: List[Player]):
        """
        Cache players' stats into Player objects.
        :param region: the region.
        :param players: a list of Players.
        """
        for player in players:
            try:
                await player.update(
                    self.wows_api,
                    self.expected(region),
                    self.coeff(region),
                    self.ship_dict[region.name], False
                )
            except Exception as e:
                self.logger.warn(str(e))
            player.updating = False

    async def process_clan(self, region: Region, clan_id: int):
        """
        Process a request for getting clan info.
        :param region: the region.
        :param clan_id: the clan id.
        """
        if not self.check_data():
            msg = 'Data needed for WTR calculation not available'
            self.logger.warn(f'{type(self)}: {msg}')
            return msg, None

        meta = await self.clan_meta(region, clan_id)
        player_ids = meta.get('members_ids', [])
        players = await self.get_clan_players(region, player_ids)
        if not players:
            return Embed(
                title='Error',
                description="The clan doesn't have any players.",
                colour=0x930D0D
            ), None
        return await self.clan_embed(region, players, meta), players
