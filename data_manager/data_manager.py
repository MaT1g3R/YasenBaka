from difflib import get_close_matches
from sqlite3 import Connection
from typing import List, Optional


class DataManager:
    """
    A SQLite3 data manager.
    """
    def __init__(self, connection: Connection):
        """
        Initialize the instance of DataManager.
        :param connection: the SQLite3 Connection object.
        """
        self.connection = connection
        self.nsfw = self.get_nsfw_tags()
        self.prefix = self.get_all_prefix()
        self.shame = self.get_all_shame()

    def get_all_prefix(self) -> dict:
        """
        Get all prefix from the db.
        :return: a dict of {guild_id: prefix}
        """
        cur = self.connection.execute('SELECT * FROM prefix')
        rows = cur.fetchall()
        if not rows:
            return {}
        return {i: p for i, p in rows}

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
            res[g][m] = {
                'region': r,
                'player_id': p
            }

        return res

    def get_shame(self, guild_id: str, member_id: str) -> dict:
        """
        Get the player data for a member.
        :param guild_id: the guild id.
        :param member_id: the member id.
        :return: a dict of {'region': region, 'player_id': player_id}
        """
        try:
            return self.shame[guild_id][member_id]
        except KeyError:
            return {}

    def set_shame(self, guild_id: str, member_id: str, region: str,
                  player_id: str):
        """
        Set the player data for a member.
        :param guild_id: the guild id.
        :param member_id: the member id.
        :param region: the region.
        :param player_id: the player id.
        """
        new = {'region': region, 'player_id': player_id}
        if self.get_shame(guild_id, member_id) == new:
            return
        if guild_id not in self.shame:
            self.shame[guild_id] = {}
        if member_id not in self.shame[guild_id]:
            self.shame[guild_id][member_id] = {}
        self.shame[guild_id][member_id] = new
        self.connection.execute(
            'REPLACE INTO shame VALUES (?,?,?,?)',
            (guild_id, member_id, region, player_id)
        )
        self.connection.commit()

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
