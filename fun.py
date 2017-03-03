"""Commands for fun"""
from discord.ext import commands
import random
from helpers import read_kana_files


class Fun:
    """Commands for fun"""
    def __init__(self, bot):
        self.kanna_files = read_kana_files()
        self.bot = bot

    @commands.command(pass_context=True)
    async def kyubey(self, ctx):
        """Madoka is best anime ever"""
        await self.bot.say('／人◕ ‿‿ ◕人＼')

    @commands.command(pass_context=True)
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        await self.bot.say(result)

    @commands.command(pass_context=True)
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple choices."""
        await self.bot.say(random.choice(choices))

    @commands.command(pass_context=True)
    async def salt(self, ctx, percentage: str, tries: int):
        """ chance of an event happeneing """
        percentage = float(percentage.replace('%', ''))/100 if '%' in percentage else float(percentage)
        res = round((1 - (1 - percentage)**tries)*100, 2)
        await self.bot.say('about {}% of dropping'.format(res))

    @commands.command(pass_context=True)
    async def repeat(self, ctx, n: int, *message: str):
        """ repeat message n times, n <= 5 """
        if n > 5:
            await self.bot.say("Are you trying to break me?")
            return
        for _ in range(n):
            await self.bot.say(' '.join(message))

    @commands.command(pass_context=True)
    async def kanna(self, ctx):
        """
        Randomly display a kanna image to the channel
        :param ctx: Context
        :type ctx: ctx
        :return: nothing
        :rtype: None
        """
        fn = random.choice(self.kanna_files)
        await self.bot.send_file(ctx.message.channel, fn)
