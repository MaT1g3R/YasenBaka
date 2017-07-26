from random import choice

from discord.ext import commands
from discord.ext.commands import BucketType, Context

from bot import Yasen
from core.fun_core import generate_dice_rolls, parse_repeat, parse_salt


class Fun:
    """
    Class to hold `Fun` commands.
    """
    __slots__ = ('bot',)

    def __init__(self, bot: Yasen):
        """
        Initialize the instance of this class.
        :param bot: the bot instance.
        """
        self.bot = bot

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def repeat(self, ctx: Context, n=None, *, msg=None):
        """
        Description: Repeat a message x number of times, where 1 <= x <= 5.
        Usage: "`{prefix}repeat 3 my message`"
        Cooldown: Once every 5 seconds per user.
        """
        try:
            _n, _msg = parse_repeat(n, msg)
        except ValueError as e:
            await ctx.send(str(e))
        else:
            for _ in range(_n):
                await ctx.send(_msg)

    @commands.command()
    async def roll(self, ctx: Context, dice: str = ''):
        """
        Description: Rolls dice in NdN format.
        Usage: "`{prefix}roll 5d6` This rolls a D6 5 times."
        """
        await ctx.send(generate_dice_rolls(dice.lower()))

    @commands.command()
    async def choose(self, ctx: Context, *choices: str):
        """
        Description: "Chooses between multiple choices. Choices are separated
        by spaces."
        Usage: "`{prefix}choose 0 1 2 3`"
        """
        if not choices:
            await ctx.send('Please enter some choices for me to choose from.')
        else:
            await ctx.send(choice(choices))

    @commands.command()
    async def salt(self, ctx: Context, num: str = None, prob: str = None):
        """
        Description: "Chance of an event happening given number of trials and
        the probability of the event."
        Usage: "`{prefix}salt 10 0.03` this is the same as
        `{prefix}salt 10 3%`"
        """
        n, p, is_percent = parse_salt(num, prob)
        if n is None or p is None:
            await ctx.send('Please enter a vaild number of trials and a '
                           'vaild probability (in decimal or percentage)')
            return
        res = 1 - (1 - p) ** n
        if is_percent:
            await ctx.send(f'**{res*100:.3g}%** chance.')
        else:
            await ctx.send(f'**{res:.3g}** probability.')
