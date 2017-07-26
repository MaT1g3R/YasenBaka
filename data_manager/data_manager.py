from collections import OrderedDict
from difflib import get_close_matches
from sqlite3 import Connection
from typing import List, Optional

from discord.utils import get


class DataManager:
    """
    A SQLite3 data manager.
    """
    __slots__ = ('connection', 'nsfw', 'prefix', 'shame', 'skip_count')

    def __init__(self, connection: Connection):
        """
        Initialize the instance of DataManager.
        :param connection: the SQLite3 Connection object.
        """
        self.connection = connection
        self.nsfw = self.get_nsfw_tags()
        self.prefix = self.get_all_prefix()
        self.shame = self.get_all_shame()
        self.skip_count = self.get_all_skips()

    def get_all_prefix(self) -> dict:
        """
        Get all prefix from the db.
        :return: a dict of {guild_id: prefix}
        """
        cur = self.connection.execute('SELECT * FROM prefix')
        rows = cur.fetchall()
        return {i: p for i, p in rows} if rows else {}

    def get_prefix(self, guild_id: str) -> Optional[str]:
        """
        Get guild prefix by id.
        :param guild_id: the guild id.
        :return: the guild prefix if there is any else None.
        """
        return self.prefix.get(guild_id, None)

    def set_prefix(self, guild_id: str, prefix: str):
        """
        Set the prefix for a guild.
        :param guild_id: the guild id.
        :param prefix: the prefix.
        """
        if self.prefix.get(guild_id, None) == prefix:
            return
        self.prefix[guild_id] = prefix
        self.connection.execute(
            'REPLACE INTO prefix VALUES(?, ?)', (guild_id, prefix)
        )
        self.connection.commit()

    def get_all_shame(self) -> dict:
        """
        Get a dict of all player data in shame.
        :return: a dict of
        {guild_id: {member_id: {'region': region, 'player_id': player_id}}}
        """
        cur = self.connection.execute('SELECT * FROM shame')
        rows = cur.fetchall()
        if not rows:
            return {}
        res = {}
        for g, m, r, p in rows:
            if g not in res:
                res[g] = {}
            if m not in res[g]:
                res[g][m] = {}
            res[g][m][r] = p
        return res

    def get_shame(self, guild_id: str,
                  member_id: str, region: str) -> Optional[str]:
        """
        Get the player data for a member.
        :param guild_id: the guild id.
        :param member_id: the member id.
        :param region: the player region.
        :return: the player id found.
        """
        assert region in ('NA', 'EU', 'AS', 'RU')
        try:
            return self.shame[guild_id][member_id][region]
        except KeyError:
            return None

    def set_shame(self, guild_id: str, member_id: str, region: str,
                  player_id: str):
        """
        Set the player data for a member.
        :param guild_id: the guild id.
        :param member_id: the member id.
        :param region: the region.
        :param player_id: the player id.
        """
        assert region in ('NA', 'EU', 'AS', 'RU')
        if self.get_shame(guild_id, member_id, region) == player_id:
            return
        if guild_id not in self.shame:
            self.shame[guild_id] = {}
        if member_id not in self.shame[guild_id]:
            self.shame[guild_id][member_id] = {}
        self.shame[guild_id][member_id][region] = player_id
        self.connection.execute(
            'REPLACE INTO shame VALUES (?,?,?,?)',
            (guild_id, member_id, region, player_id)
        )
        self.connection.commit()

    def delete_shame(self, guild_id: str, member_id: str, region: str):
        """
        Delete a shame entry from the db.
        :param guild_id: the guild id.
        :param member_id: the member id.
        :param region: the region.
        """
        assert region in ('ALL', 'NA', 'EU', 'AS', 'RU')
        if region == 'ALL':
            sql = 'DELETE FROM shame WHERE guild_id=? AND member_id=?'
            self.connection.execute(sql, (guild_id, member_id))
            try:
                self.shame[guild_id].pop(member_id)
            except KeyError:
                pass
        else:
            sql = ('DELETE FROM shame '
                   'WHERE guild_id=? AND member_id=? AND region=?')
            self.connection.execute(sql, (guild_id, member_id, region))
            try:
                self.shame[guild_id][member_id].pop(region)
            except KeyError:
                pass
        self.connection.commit()

    def get_shame_list(self, members, guild_id: str) -> Optional[OrderedDict]:
        """
        Get shamelist for a given guild.
        :param members: the list of discord Member objects in the guild list.
        :param guild_id: the guild id.
        :return: an OrderedDict of {region: player discord name}
        """
        guild = self.shame.get(guild_id, None)
        if not guild:
            return
        bad = []
        res = OrderedDict({
            'NA': [],
            'EU': [],
            'AS': [],
            'RU': []
        })
        for member_id, val in guild.items():
            if not val or not any(val.values()):
                continue
            member = get(members, id=int(member_id))
            if not member:
                bad.append(member_id)
                continue
            for r in val:
                if val[r]:
                    res[r].append(str(member))
        for bad_id in set(bad):
            self.delete_shame(guild_id, bad_id, 'ALL')
        return res if any(res.values()) else None

    def get_nsfw_tags(self) -> dict:
        """
        Get all nsfw tags stored.
        :return: a dict of {site: tags}
        """
        cur = self.connection.execute('SELECT * FROM nsfw')
        rows = cur.fetchall()
        if not rows:
            return {}
        res = {}
        for site, tag in rows:
            if site not in res:
                res[site] = []
            res[site].append(tag)
        return res

    def set_nsfw_tags(self, site: str, tags: List[str]):
        """
        Set nsfw tags for a site.
        :param site: the site.
        :param tags: the list of tags.
        """
        if site not in self.nsfw:
            self.nsfw[site] = []
        new = []
        for tag in tags:
            if tag not in self.nsfw[site]:
                self.nsfw[site].append(tag)
                new.append(tag)
        if new:
            self.connection.executemany(
                'INSERT INTO nsfw(site, tag) VALUES (?, ?)',
                [(site, t) for t in new]
            )
            self.connection.commit()

    def match_tag(self, site: str, tag: str) -> Optional[str]:
        """
        Try to match user input tag with one from the db.
        :param site: the site of the tag.
        :param tag: the user input tag.
        :return: a tag from the db if match was success, else None
        """
        if site not in self.nsfw:
            return
        if tag in self.nsfw[site]:
            return tag
        res = get_close_matches(tag, self.nsfw[site], 1, cutoff=0.4)
        return res[0] if res else None

    def tag_exist(self, site: str, tag: str) -> bool:
        """
        Check if a tag exists.
        :param site: the site name.
        :param tag: the tag.
        :return: True if the tag exists.
        """
        return site in self.nsfw and tag in self.nsfw[site]

    def get_all_skips(self) -> dict:
        """
        Get all skip count for all guilds.
        :return: a dict of {guild_id: skip count}
        """
        cur = self.connection.execute('SELECT * FROM skip_count')
        rows = cur.fetchall()
        return {id_: count for id_, count in rows} if rows else {}

    def get_skip(self, guild_id: str) -> Optional[int]:
        """

        :param guild_id:
        :return:
        """
        return self.skip_count.get(guild_id, None)

    def set_skip(self, guild_id: str, count: int):
        """
        Set the skip count for a guild.
        :param guild_id: the guild id.
        :param count: the count.
        """
        if self.skip_count.get(guild_id, None) == count:
            return
        self.skip_count[guild_id] = count
        self.connection.execute(
            'REPLACE INTO skip_count VALUES (?, ?)', (guild_id, count)
        )
        self.connection.commit()
