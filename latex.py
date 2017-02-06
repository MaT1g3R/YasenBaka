"""The latex function of the bot"""
import urllib.request
import urllib.parse
from discord.ext import commands


class LaTeX:
    """Renders LaTeX equations"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def latex(self, ctx, *input_: str):
        """Renders the input LaTeX equation"""
        l = " ".join(input_)
        fn = self.generate_image_online(l)
        await self.bot.send_file(ctx.message.channel, fn)

    # More unpredictable, but probably safer for my computer.
    def generate_image_online(self, latex):
        """
        Generate latex image from latex website
        :param latex: the latex equation to be rendered
        :type latex: str
        :return: The path to rendered latex image
        :rtype: str
        """
        url = 'http://frog.isima.fr/cgi-bin/bruno/tex2png--10.cgi?'
        url += urllib.parse.quote(latex, safe='')
        fn = 'latex.png'
        urllib.request.urlretrieve(url, fn)
        return fn
    #
