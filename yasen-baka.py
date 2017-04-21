"""The main bot run file"""
from shell import init

if __name__ == '__main__':
    bot, cogs = init()
    bot.start_bot(cogs)
