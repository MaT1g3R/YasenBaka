import json

import aiohttp

uri = 'https://discordbots.org/api'


class Botsorgapi:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.key = self.bot.data.api_keys['Botsorgapi']

    def __unload(self):
        self.bot.loop.create_task(self.session.close())

    async def send(self):
        dump = json.dumps({
            'shard_id': str(self.bot.shard_id),
            'shard_count': str(self.bot.shard_count),
            'server_count': len(self.bot.servers)
        })
        head = {
            'authorization': self.key,
            'content-type': 'application/json'
        }

        url = '{0}/bots/{1}/stats'.format(uri, self.bot.user.id)

        async with self.session.post(url, data=dump, headers=head) as resp:
            print('returned {0.status} for {1}'.format(resp, dump))

    async def on_server_join(self, server):
        await self.send()

    async def on_server_remove(self, server):
        await self.send()

    async def on_ready(self):
        await self.send()
