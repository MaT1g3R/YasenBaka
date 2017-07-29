from typing import Optional, Tuple, Union

from discord import Embed, Member, Message, User
from discord.ext.commands import Context

from core import MessageContent, Pageable
from music.music_util import add_embed_options, playlist_embed


class PlayList(Pageable):
    """
    An interactive playlist.
    """
    __slots__ = ('player', 'cur_page')

    def __init__(self, message: Message, author: Union[Member, User], player):
        """

        :param message: the initial playlist message.
        :param author: the requester for the playlist.
        :param player: the music player.
        :type player: AbstractMusicPlayer
        """
        self.player = player
        self.cur_page = 1
        super().__init__(message, author, 60)

    def __get_page_index(self, diff: int) -> Tuple[int, int]:
        """
        Get the start and end page index for `self.cur_page` + `diff`
        :param diff: the difference to change the page by.
        :return: the start and end page index for `self.cur_page` + `diff`
        """
        end = 10 * (self.cur_page + diff)
        return end - 10, end

    def __embed(self, section: list, ctx: Context) -> Optional[Embed]:
        """
        Get an embed for the give section of `Entry`.

        :param section: a list of `Entry` to put in the embed.

        :param ctx: the `discord.Context` object.

        :return: an embed for the give section of `Entry`, if any.
        """
        embed = playlist_embed(
            ctx, self.cur_page, self.player.total_page,
            self.player.current, section
        )
        if embed:
            return add_embed_options(embed)

    def __get_page(self, diff: int, ctx: Context) -> Optional[MessageContent]:
        """
        Get a page with page number `diff` away than `self.cur_page`
        If the page is not empty, also add `diff` to `self.cur_page`

        :param diff: the difference in page number.

        :param ctx: the `discord.Context` object.

        :return: a `MessageContent` instance repersenting the page, if any.
        """
        start, end = self.__get_page_index(diff)
        if start < 0:
            return
        lst = self.player.lst
        section = lst[start:end]
        if not section:
            return
        self.cur_page += diff
        return MessageContent(embed=self.__embed(section, ctx), text=None)

    async def next(self, ctx: Context) -> Optional[MessageContent]:
        """
        See `Pageable.next`
        """
        return self.__get_page(1, ctx)

    async def prev(self, ctx: Context) -> Optional[MessageContent]:
        """
        See `Pageable.prev`
        """
        return self.__get_page(-1, ctx)
