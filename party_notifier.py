from discord.ext import commands
import discord
import configparser
import os

# TODO
# - Test trigger (maybe change role)

class Party_Notifier(commands.Cog):
    '''
    This is a cog for a discord bot.
    '''

    def __init__(self, bot, bot_data):
        self.bot = bot
        self.bot_data = bot_data
        self.potential_channels = set() # Channels that CAN trigger the notification
        self.party_channels = set()     # Channels that currently have a party

        self.pot_file_name = 'party_pot_channels.txt'

        # Create file if it doesn't exist
        if not os.path.exists(bot_data.datapath + self.pot_file_name):
            os.mknod(bot_data.datapath + self.pot_file_name)
        else:
            with open(self.bot_data.datapath + self.pot_file_name, 'r') as file:
                self.potential_channels = set([int(x.strip()) for x in file.readlines()])

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

    @commands.Cog.listener()
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
        if not isinstance(before.channel, discord.VoiceChannel) and isinstance(after.channel, discord.channel.VoiceChannel):
            await self.check_starting_party(after.channel)
            return

        # CASE B
        if isinstance(before.channel, discord.VoiceChannel) and not isinstance(after.channel, discord.channel.VoiceChannel):
            await self.check_ended_party(before.channel)
            return

        # CASE C
        if isinstance(before.channel, discord.VoiceChannel) and isinstance(after.channel, discord.VoiceChannel):
            await self.check_ended_party(before.channel)
            await self.check_starting_party(after.channel)
            return


    @commands.group(brief="{mark, unmark, info, setcount}",
                    help="This does nothing on its own. Use it in combination with [mark, unmark, info, setcount]\n\nExample:\n"
                         "party mark channel name or id")
    async def party(self, ctx):
        pass

    @party.command(brief="Mark channel as potential party channel",
                   usage="channel name or id")
    async def mark(self, ctx, *, arg: discord.VoiceChannel):
        if arg.id not in self.potential_channels:
            # Add channel to set:
            self.potential_channels = self.potential_channels.union({arg.id})

            # Write new set to disk:
            with open(self.bot_data.datapath + self.pot_file_name, 'w') as file:
                file.writelines([f'{x}\n' for x in self.potential_channels])

            await ctx.send(f'**{arg.name}** was marked as a potential party channel.', delete_after=10)
        else:
            await ctx.send('Channel is already marked.', delete_after=10)

    @party.command(brief="Unmark channel as potential party channel",
                   usage="channel name or id")
    async def unmark(self, ctx, *, arg: discord.VoiceChannel):
        if arg.id in self.potential_channels:
            self.potential_channels = self.potential_channels - {arg.id}

            with open(self.bot_data.datapath + self.pot_file_name, 'w') as file:
                file.writelines([f'{x}\n' for x in self.potential_channels])

            await ctx.send(f'**{arg.name}** was unmarked as a potential party channel.', delete_after=10)
        else:
            await ctx.send(f'**{arg.name}** wasn\'t marked in the first place.', delete_after=10)

    @party.command(brief="View or change channel member-count to trigger notification",
                   usage="{<none>, <integer>}")
    async def setcount(self, ctx, arg: int):
        if arg > 0:
            # Update db:
            self.bot_data.party_count = arg

            # Update config.txt:
            config = configparser.ConfigParser()
            config.read('config.txt')
            config.set('BASE', 'party_count', str(arg))

            with open('config.txt', 'w') as configfile:
                config.write(configfile)

            await ctx.send(f"Changed trigger count to `{arg}`", delete_after=10)

    @party.command(brief="View party info")
    async def info(self, ctx):
        # Show: party_count, potential_channels, party_channels, notification_channel, notification_role

        notification_channel = self.bot.get_channel(self.bot_data.IDs['notification_channel'])
        party_role = ctx.guild.get_role(self.bot_data.IDs['party_role'])

        voice_converter = commands.VoiceChannelConverter()
        pot_channels = [await voice_converter.convert(ctx, str(x)) for x in self.potential_channels]
        party_channels = [await voice_converter.convert(ctx, str(x)) for x in self.party_channels]

        pot_str = "```\n" + "\n".join([f'{x.name}' for x in pot_channels]) + "\n```" if len(self.potential_channels) > 0 else '<none>'
        active_str = "```\n" + "\n".join([f'{x.name}' for x in party_channels]) + "\n```" if len(self.party_channels) > 0 else '<none>'

        info_str = f'Trigger count: `{self.bot_data.party_count}`\n' \
                   f'Notification channel: `{notification_channel.name}`\n' \
                   f'Notification role: `{party_role.name}`\n' \
                   f'\nList of parties:\n{active_str}' \
                   f'\nChannels that can trigger the party notification:\n{pot_str}'

        await ctx.send(info_str)
