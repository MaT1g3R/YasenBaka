"""The main bot run file"""
from shell import init

if __name__ == '__main__':
    bot, cog = init()
    bot.start_bot(cog)
