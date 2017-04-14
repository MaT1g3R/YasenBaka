"""Utility commands"""
import time

import discord
from discord.errors import Forbidden, HTTPException
from discord.ext import commands

import core.util_core as util_core


class Util:
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = self.bot.data

    @commands.command()
    async def help(self, input_: str = None):
        """Help messages"""
        if input_ is None:
            await self.bot.say(util_core.default_help(self.data.help_message))
        elif input_ in self.data.help_message:
            await self.bot.say(self.data.help_message[input_])

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_permissions(administrator=True)
    async def pmall(self, ctx, *args):
        if len(args) <= 0:
            await self.bot.say('Please enter a valid message.')
        else:
            members, content = util_core.process_pmall(ctx, list(args))
            ex_list = []
            succ_list = []
            for member in members:
                try:
                    await self.bot.send_message(member, content)
                    succ_list.append(member.name)
                except Forbidden and HTTPException:
                    ex_list.append(member.name)
            if len(ex_list) > 0:
                await self.bot.say(
                    'The PM could not be sent to the following users:'
                    ' {}'.format(', '.join(ex_list)))
            await self.bot.say('PM sent to: {}'.format(', '.join(succ_list)))

    @commands.command(pass_context=True)
    async def latex(self, ctx, *input_: str):
        """Renders the input LaTeX equation"""
        if len(input_) <= 0:
            await self.bot.say("Please enter a valid input.")
        else:
            l = " ".join(input_)
            fn = util_core.generate_latex_online(l)
            await self.bot.send_file(ctx.message.channel, fn)

    @commands.command(pass_context=True, no_pm=True)
    async def joined(self, ctx, member: discord.Member):
        """Says when a member joined."""
        if ctx.message.channel.name is not None:
            await self.bot.say(util_core.joined_time(member))

    @commands.command()
    async def anime(self, *input_: str):
        """
        search MAL for anime
        """
        await self.bot.say(util_core.anime_search(' '.join(input_)))

    @commands.command(pass_context=True, no_pm=True)
    async def avatar(self, ctx, member: discord.Member):
        """ get user avatar """
        if ctx.message.channel.name is not None:
            res = member.avatar_url if member.avatar_url != '' \
                else member.default_avatar_url
            await self.bot.say(res)

    @commands.command()
    async def stackoverflow(self, *question: str):
        """I do not take responsibility for damage caused"""
        if len(question) <= 0:
            await self.bot.say("Please enter a question!")
        else:
            await \
                self.bot.try_say(util_core.stack_answer(
                    self.data.so, ' '.join(question)))

    @commands.command()
    async def currency(self, base: str, target: str, amount: str):
        """converts currency"""
        try:
            amount_str = amount
            amount = float(amount)
            base = base.upper()
            target = target.upper()
        except ValueError:
            await self.bot.say('Please enter a valid amount')
            return

        try:
            money = util_core.convert_currency(self.data.api_keys['Currency'],
                                               base, amount, target)
            await self.bot.say(amount_str + base + ' = ' + money + target)
        except KeyError:
            await self.bot.say('Please enter valid currency codes!')

    @commands.command(pass_context=True)
    async def info(self, ctx):
        servers = self.bot.servers
        members = self.bot.get_all_members()
        channels = self.bot.get_all_channels()
        voice = self.bot.voice_clients
        user = self.bot.user
        uptime = util_core.time_elapsed(self.data.start_time)
        res = util_core.info_builder(
            ctx, servers, members, channels, voice, user, uptime)
        await self.bot.send_message(ctx.message.channel, embed=res)

    @commands.command()
    async def ping(self):
        start_time = int(round(time.time() * 1000))
        msg = await self.bot.say('Pong! :hourglass:')
        end_time = int(round(time.time() * 1000))
        await self.bot.edit_message(
            msg, 'Pong! | :timer: {}ms'.format(end_time - start_time))

    @commands.command(pass_context=True)
    async def bash(self, ctx, *args):
        if str(ctx.message.author.id) \
                in ["99271746347110400", "145735970342305792"]:
            await self.bot.say(util_core.bash_script(list(args)))
        else:
            await self.bot.say('Only my owner can use this command!')

    @commands.command(pass_context=True)
    async def update(self, ctx):
        if str(ctx.message.author.id) \
                in ["99271746347110400", "145735970342305792"]:
            await self.bot.say(util_core.bash_script(['git', 'pull']))
            util_core.bash_script(['pm2', 'restart', '16'])
        else:
            await self.bot.say('Only my owner can use this command!')
