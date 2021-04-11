from discord.ext import commands
import os


class Party_Notifier(commands.Cog):
    '''
    This is a cog for a discord bot.
    '''

    def __init__(self, bot, bot_data):
        self.bot = bot
        self.bot_data = bot_data

        # Create file if it doesn't exist
        if not os.path.exists(bot_data.datapath + 'party_channels.txt'):
            os.mknod(bot_data.datapath + 'party_channels.txt')


    @commands.command(brief='Mark a channel as a party-channel')
    async def addpartychannel(self, ctx, arg):
        pass





