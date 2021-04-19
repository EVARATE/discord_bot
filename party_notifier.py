from discord.ext import commands
import discord
import configparser
import os


class Party_Notifier(commands.Cog):
    '''
    This is a cog for a discord bot.
    '''

    def __init__(self, bot, bot_data):
        self.bot = bot
        self.bot_data = bot_data
        self.potential_channels = set() # Channels that CAN trigger the notification
        self.party_channels = set()     # Channels that currently have a party

        # Create file if it doesn't exist
        if not os.path.exists(bot_data.datapath + 'party_pot_channels.txt'):
            os.mknod(bot_data.datapath + 'party_pot_channels.txt')

    async def check_starting_party(self, check_channel):
        party_count = self.bot_data.party_count

        # Check if channel can have party or has ongoing party:
        if check_channel.id not in self.potential_channels or check_channel.id in self.party_channels:
            return
        # Now, check_channel is pot. party channel but has no party.

        # Check if check_channel has enough members:
        if len(check_channel.members) >= party_count:
            # Mark as active party channel:
            self.party_channels = self.party_channels.union({int(check_channel.id)})
            # Send notification:
            notification_channel = self.bot.get_channel(self.bot_data.IDs['notification_channel'])
            party_role = check_channel.guild.get_role(self.bot_data.IDs['party_role'])
            await notification_channel.send(
                f'{party_role.mention} There seems to be a party in **{check_channel.name}**')
            return

    async def check_ended_party(self, check_channel):
        # Check if channel can have party or has ongoing party:
        if check_channel.id not in self.potential_channels or check_channel.id not in self.party_channels:
            return
        # Now check_channel is pot. party channel and has party.

        # Check if check_channel has no members:
        if len(check_channel.members) == 0:
            # No members => end party.
            self.party_channels -= {int(check_channel.id)}
            # Send notification:
            notification_channel = self.bot.get_channel(self.bot_data.IDs['notification_channel'])
            await notification_channel.send(
                f'The party in **{check_channel.name} has ended.**')
            return

    @commands.Cog.listener
    async def on_voice_state_update(self, member, before, after):
        """
        Cases:
            before.chan | after.chan | case
            NOT VOICE   | voice      |  A
            voice       | NOT VOICE  |  B
            voice       | voice      |  C
            NOT VOICE   | NOT VOICE  |  D   do nothing
        """

        # CASE A
        if before.channel is not discord.VoiceChannel and after.channel is discord.VoiceChannel:
            await self.check_starting_party(after.channel)
            return

        # CASE B
        if before.channel is discord.VoiceChannel and after.channel is not discord.VoiceChannel:
            await self.check_ended_party(before.channel)
            return

        # CASE C
        if before.channel is discord.VoiceChannel and after.channel is discord.VoiceChannel:
            await self.check_ended_party(before.channel)
            await self.check_starting_party(after.channel)
            return


    @commands.group(brief="[mark, unmark, info, ...]",
                    help="This does nothing on its own. Use it in combination with [mark, unmark, info, ...]\n\nExample:\n"
                         "party mark channel name or id")
    async def party(self, ctx):
        pass

    @party.command()
    async def mark(self, ctx, *, arg: discord.VoiceChannel):
        pass

    @party.command()
    async def unmark(self, ctx, *, arg: discord.VoiceChannel):
        pass

    @party.command()
    async def count(self, ctx, *, arg):
        pass

    @party.command()
    async def info(self, ctx):
        pass
