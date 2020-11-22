import discord
import re # regex
import misc_functions as misc

class bot_client(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message received')

    def get_config(self):
        configFile = open('config.txt', 'r')
        rawText = configFile.read()

        # Find parameters via regex:    .+ = '.+'
        params = re.findall('.+ = \'.+\'', rawText)

        # Assign found parameters to variables:
        lineCount = 0
        while lineCount < len(params):




    # Parameters
    token = ''

client = bot_client()
client.run(bot_client.token)