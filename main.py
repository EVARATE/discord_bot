import discord
import configparser
from discord.ext import commands
import misc_functions as misc

class bot_client(discord.Client):
    def startup(self):
        # Run this function once when the bot starts for the first time
        self.get_config()
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message received')

    def get_config(self):
        configFile = configparser.ConfigParser()
        configFile.read('config.txt')
        self.token = configFile['DEFAULT']['token']
        self.ruleChannelID = configFile['RULES']['channelID']
        self.ruleMessageID = configFile['RULES']['messageID']



    # Parameters:
    token = ''
    ruleChannelID = ''
    ruleMessageID = ''

client = bot_client()
client.get_config()
client.run(client.token)