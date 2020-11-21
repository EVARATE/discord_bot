import discord


class bot_client(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message received')


token = ""
client = bot_client()
client.run(token)