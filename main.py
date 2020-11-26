'''
If you don't know what the fuck is going on here then I humbly suggest you read the documentation:
https://discordpy.readthedocs.io/en/latest/index.html#

'''


import discord
from discord.ext import commands
import configparser
import random


# Modify class:
class bot_client(discord.Client):
    def startup(self):
        # Run this function once when the bot starts for the first time
        self.get_config()


    def get_config(self):
        configFile = configparser.ConfigParser()
        configFile.read('config.txt')
        self.token = configFile['BASE']['token']
        self.prefix = configFile['BASE']['prefix']
        self.ruleChannelID = int(configFile['RULES']['channelID'])
        self.ruleMessageID = int(configFile['RULES']['messageID'])



    # Parameters:
    token = ''
    prefix = ''
    ruleChannelID = -1
    ruleMessageID = -1


# Callbacks:
client = bot_client()

@client.event
async def on_ready():
    print('{0.user} is now online.'.format(client))
    game = discord.Game("mit deinen Nerven")
    await client.change_presence(status=discord.Status.online, activity = game)

@client.event
async def on_message(message):
    # Bot doesn't answer itself:
    if message.author == client.user:
        return

    # === INTERPRET CHAT ===

    # Very hidden easter eggs:
    if message.content.lower() == 'open the pod bay doors hal':
        await message.channel.send('I am afraid I can\'t do that {0.author.name}.'.format(message))


    # look for commands:
    if message.content.startswith(client.prefix):
        rand = random.random()
        if rand < 0.01:
            await message.channel.send('I am afraid I can\'t do that {0.author.name}.'.format(message))
            return

        # RULES
        if message.content.startswith(client.prefix + "help"):
            ruleChannel: discord.abc.GuildChannel = client.get_channel(client.ruleChannelID)
            ruleMsg = await ruleChannel.fetch_message(client.ruleMessageID)
            await message.channel.send(ruleMsg.content)


client.startup()
client.run(client.token)