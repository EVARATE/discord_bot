from discord.ext import commands
import discord
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

    @commands.group(brief="Enter   help party   for subcommands")
    async def party(self, ctx):
        pass

    @party.command(brief='Mark a voice channel as a viable party channel')
    async def add(self, ctx, *, arg: discord.VoiceChannel):
        # Read existing file:
        with open(self.bot_data.datapath + 'party_channels.txt', 'r') as file:
            fileIDs = set([x.strip() for x in file.readlines()])

        # Add channel to set:
        fileIDs = fileIDs.union({str(arg.id)})

        # Write back to file:
        with open(self.bot_data.datapath + 'party_channels.txt', 'w') as file:
            file.writelines([f'{x}\n' for x in fileIDs])

        await ctx.send("Channel was marked.", delete_after=10)

    @party.command(brief='Unmark a voice channel as party channel')
    async def remove(self, ctx, *, arg: discord.VoiceChannel):
        # Read existing file:
        with open(self.bot_data.datapath + 'party_channels.txt', 'r') as file:
            fileIDs = set([x.strip() for x in file.readlines()])

        # Add channel to set:
        fileIDs = fileIDs - {str(arg.id)}

        # Write back to file:
        with open(self.bot_data.datapath + 'party_channels.txt', 'w') as file:
            file.writelines(fileIDs)

        await ctx.send("Channel was unmarked.", delete_after=10)

    @party.command(brief='Show list of marked party channels')
    async def list(self, ctx):
        with open(self.bot_data.datapath + 'party_channels.txt', 'r') as file:
            fileIDs = set([x.strip() for x in file.readlines()])

        converter = commands.VoiceChannelConverter()
        channelList = []
        for id in fileIDs:
            channel = await converter.convert(ctx, id)
            channelList.append(channel.name)

        if len(channelList) == 0:
            await ctx.send("There are no channels marked as party channels.")
            return

        lstStr = '\n'.join(channelList)
        await ctx.send('**The following Channels can trigger the party notification:**\n```\n' + lstStr + '\n```')
