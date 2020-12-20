"""
This class is based on this guide:
https://gist.github.com/InterStella0/b78488fb28cadf279dfd3164b9f0cf96

https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.HelpCommand.send_command_help

It defines how the /help command behaves

    THIS FILE IS NOT USED RIGHT NOW

"""
import discord
from discord.ext import commands


class bot_helper(commands.HelpCommand):
    def get_command_signature(self, command):
        return f'{self.clean_prefix}{command.qualified_name} {command.signature}'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Help')
        for cog, commands in mapping.items():
            command_signatures = [self.get_command_signature(c) for c in commands]
            if command_signatures:
                cog_name = getattr(cog, 'qualified_name', 'No Category')
                embed.add_field(name=cog_name, value='\n'.join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

