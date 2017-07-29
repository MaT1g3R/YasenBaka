from asyncio import TimeoutError
from collections import namedtuple
from typing import Optional, Union

from discord import Member, Message, User
from discord.ext.commands import Context


class MessageContent(namedtuple('MessageContent', ('text', 'embed'))):
    __slots__ = ()


class Pageable:
    """
    An interface that provide a "paging" functionality to `discord.Message`.

    === Attributes ===
    :type message: Message
        The original `discord.Message` object.
    :type author: Union[Member, User]
        The original `discord.Message` requester.
    :type timeout: int
        Amount of seconds of inactivity before the message self destructs.
    """
    __slots__ = ('message', 'author', 'timeout', 'emojis')

    def __init__(self, message: Message, author: Union[Member, User],
                 timeout: int):
        """
        :param message: The original `discord.Message` object.

        :param author: The original `discord.Message` requester.

        :param timeout:
            Amount of seconds of inactivity before the message self destructs.
        """
        self.message = message
        self.author = author
        self.timeout = timeout
        self.emojis = ('⏪', '⏩', '❌')

    async def prev(self, ctx) -> Optional[MessageContent]:
        """
        Return the previous page.
        This should return None if there are no previous page.

        :param ctx: `discord.Context` object.

        :return: a `MessageContent` instance that represents the previous page.
        """
        raise NotImplementedError

    async def next(self, ctx) -> Optional[MessageContent]:
        """
        Return the next page.
        This should return None if there are no next page.

        :param ctx: `discord.Context` object.

        :return: a `MessageContent` instance that represents the next page.
        """
        raise NotImplementedError

    async def __do_action(self, ctx, emoji):
        """
        Edit/delete `self.message`.

        :param ctx: `discord.Context` object.

        :param emoji: the user reaction emoji.
        """
        edit = None
        if emoji == self.emojis[0]:
            edit = await self.prev(ctx)
        if emoji == self.emojis[1]:
            edit = await self.next(ctx)
        if emoji == self.emojis[2]:
            await self.message.delete()
            self.message = None
        if edit and self.message:
            await self.message.edit(content=edit.text, embed=edit.embed)

    async def __call__(self, ctx: Context):
        """
        The main loop that check for user reactions and flip pages.

        :param ctx: `discord.Context` object.
        """
        for emoji in self.emojis:
            await self.message.add_reaction(emoji)
        while True:
            if not self.message:
                return
            try:
                reaction, user = await ctx.bot.wait_for(
                    'reaction_add',
                    timeout=self.timeout
                )
                emoji = reaction.emoji
                if emoji not in self.emojis \
                        or user not in (self.author, ctx.bot.user):
                    await self.message.remove_reaction(emoji, user)
                if user == self.author:
                    await self.__do_action(ctx, emoji)
            except TimeoutError:
                await self.message.delete()
                return
