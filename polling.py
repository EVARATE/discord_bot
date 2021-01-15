import configparser
import re
import misc_functions as misc
from typing import List
import discord
from discord.ext import commands
import bot_database
import os
import glob
import types


class Poll_Commands(commands.Cog):
    """
    This is a cog for the discord bot.
    """
    def __init__(self, bot, database):
        self.bot = bot
        self.bot_data: bot_database.bot_database = database
        # self.load_all_polls() needs async
        bot.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        # self.pp = await self.get_pp() # not sure if I need this
        await self.load_all_polls()

    @commands.command(brief="Create new poll",
                      help="Create a new poll with a topic and as many options as you like.",
                      usage='"<topic>" "<option1>" "<option2>" ...')
    async def poll(self, ctx, *args):
        await ctx.message.delete()
        if len(args) < 2:
            await ctx.send('Error: Too few arguments.', delete_after=10.0)
            return
        newPoll: mo_poll = mo_poll(args[0], [x for x in args[1:]])
        newPoll.authorID = ctx.author.id
        newPoll.authorName = ctx.author.name
        newPoll.msgChannelID = ctx.channel.id
        newPoll.id = self.bot_data.nextPollID
        self.bot_data.nextPollID += 1
        pollMessage = await ctx.send(newPoll.getPollMsg(self.bot_data.prefix))
        newPoll.msgMessageID = pollMessage.id

        self.bot_data.polls.append(newPoll)
        newPoll.savePoll(f'{self.bot_data.datapath}polls/poll{newPoll.id}.txt')

    @commands.command(brief="Vote for option in poll",
                      help="Vote for an option in a poll. Voting is anonymous.",
                      usage="<pollID> <optionID>")
    async def vote(self, ctx, *args):
        await ctx.message.delete()
        if len(args) != 2:
            await ctx.send('Error: Invalid number of arguments.', delete_after=10.0)
            return
        if not (args[0].isdigit() and args[1].isdigit()):
            await ctx.send('Error: Arguments must be numbers.', delete_after=10.0)
            return
        pollID = int(args[0])
        optID = int(args[1])
        for currPoll in self.bot_data.polls:
            if currPoll.id == pollID:
                currPoll.voteOption(optID, ctx.author.id)
                await self.updatePoll(currPoll, ctx.channel.id)
                currPoll.savePoll(f'{self.bot_data.datapath}polls/poll{currPoll.id}.txt')
                return
        await ctx.send(f'Error: Couldn\'t find poll with id `{pollID}`', delete_after=10.0)

    @commands.command(brief="Unvote for option in poll",
                      help="Unvote for an option in a poll. You can vote for something else afterwards.",
                      usage="<pollID> <optionID>")
    async def unvote(self, ctx, *args):
        await ctx.message.delete()
        if len(args) != 2:
            await ctx.send('Error: Invalid number of arguments.', delete_after=10.0)
            return
        if not (args[0].isdigit() and args[1].isdigit()):
            await ctx.send('Error: Arguments must be numbers.', delete_after=10.0)
            return
        pollID = int(args[0])
        optID = int(args[1])
        for currPoll in self.bot_data.polls:
            if currPoll.id == pollID:
                currPoll.unvoteOption(optID, ctx.author.id)
                await self.updatePoll(currPoll, ctx.channel.id)
                currPoll.savePoll(f'{self.bot_data.datapath}polls/poll{currPoll.id}.txt')
                return
        await ctx.send(f'Error: Couldn\'t find poll with id `{pollID}`', delete_after=10.0)

    @commands.command(brief="Close your poll",
                      help="Close a poll you previously opened. You can only close your own polls.",
                      usage="<pollID>",
                      aliases=['pollclose'])
    async def closepoll(self, ctx, arg):
        await ctx.message.delete()
        if not arg.isdigit():
            await ctx.send('Error: Argument must be a number.', delete_after=10.0)
            return
        pollID = int(arg)
        for currPoll in self.bot_data.polls:
            if currPoll.id == pollID:
                # Check if ctx.author is admin or poll author:
                admin_role = ctx.guild.get_role(self.bot_data.IDs['admin_role'])
                if admin_role in ctx.author.roles or ctx.author.id == currPoll.authorID:
                    currPoll.isClosed = True
                    await self.updatePoll(currPoll, ctx.channel.id)
                    os.remove(f'{self.bot_data.datapath}polls/poll{currPoll.id}.txt')
                    self.bot_data.polls[:] = [x for x in self.bot_data.polls if x.id != pollID]
                    await ctx.send(f'Closed poll#-**{pollID}**')
                else:
                    await ctx.send('Error: You can only close your own polls.', delete_after=10.0)

    @commands.command(brief="Change poll settings",
                      help=f"Change settings for your existing poll.\n\nSetting            Values\
                           \ncustom_options\t  [on, off]\nmultiple_choice\t  [on, off]\n\
                            \nExample to turn on multiple choice:\t/pollset 0 multiple_choice on",
                      usage="<pollID> <setting> <value>")
    async def pollset(self, ctx, *args):
        await ctx.message.delete()
        if len(args) != 3 or not args[0].isdigit():
            await ctx.send(f"Error: Invalid syntax. See `{self.bot_data.prefix}help pollset` for instructions.", delete_after=10.0)
            return
        for poll in self.bot_data.polls:
            if poll.id == int(args[0]):
                admin_role = ctx.guild.get_role(self.bot_data.IDs['admin_role'])
                if admin_role in ctx.author.roles or ctx.author.id == poll.authorID:
                    # Parse command:
                    if args[1].lower() in ["custom_options", "custopt"]:
                        if args[2].lower() in ["on", "onn", "oon", "1", "true", "yes", "y"]:
                            poll.custOpt = True
                        elif args[2].lower() in ["off", "of", "oof", "0", "false", "no", "n"]:
                            poll.custOpt = False
                        else:
                            await ctx.send("Error: Invalid value.", delete_after=10.0)
                            return
                        await self.updatePoll(poll, ctx.channel.id)
                        poll.savePoll(f'{self.bot_data.datapath}polls/poll{poll.id}.txt')

                    elif args[1].lower() in ["multiple_choice", "multiplechoice", "multichoice", "multi"]:
                        if args[2].lower() in ["on", "onn", "oon", "1", "true", "yes", "y"]:
                            poll.multiChoice = True
                        elif args[2].lower() in ["off", "of", "oof", "0", "false", "no", "n"]:
                            poll.multiChoice = False
                        else:
                            await ctx.send("Error: Invalid value.", delete_after=10.0)
                            return
                        await self.updatePoll(poll, ctx.channel.id)
                        poll.savePoll(f'{self.bot_data.datapath}polls/poll{poll.id}.txt')
                    else:
                        await ctx.send("Error: This setting doesn't exist.", delete_after=10.0)
                else:
                    await ctx.send("Error: You do not have permission to edit this poll.", delete_after=10.0)

    @commands.command(brief="Add option to poll",
                      help="Add an option to an existing poll. Only admins and the polls author can do this unless the 'custom_options' setting is on.",
                      usage="<pollID> \"<New option>\"")
    async def polladd(self, ctx, *args):
        await ctx.message.delete()
        if len(args) != 2 or not args[0].isdigit():
            await ctx.send("Error: Invalid syntax.", delete_after=10.0)
            return

        for poll in self.bot_data.polls:
            if poll.id == int(args[0]):
                # Check validity:
                admin_role = ctx.guild.get_role(self.bot_data.IDs['admin_role'])
                if admin_role in ctx.author.roles or ctx.author.id == poll.authorID or poll.custOpt:
                    poll.addOption(args[1])
                    await self.updatePoll(poll, ctx.channel.id)
                    poll.savePoll(f'{self.bot_data.datapath}polls/poll{poll.id}.txt')
                    return
                else:
                    await ctx.send("Error: You do not have permission to add an option to this poll.", delete_after=10.0)
                    return
            else:
                await ctx.send(f"Error: Couldn't find poll with id `{args[0]}`")

    @commands.command(brief="Remove option from poll",
                      help="Remove an option from existing poll. Only admins and the polls author can do this.",
                      usage="<pollID> <optionID>")
    async def pollrem(self, ctx, *args):
        await ctx.message.delete()
        if len(args) != 2 or not args[0].isdigit() or not args[1].isdigit():
            await ctx.send("Error: Invalid syntax.", delete_after=10.0)
            return

        for poll in self.bot_data.polls:
            if poll.id == int(args[0]):
                admin_role = ctx.guild.get_role(self.bot_data.IDs['admin_role'])
                if admin_role in ctx.author.roles or ctx.author.id == poll.authorID:
                    poll.remOption(int(args[1]))
                    await self.updatePoll(poll, ctx.channel.id)
                    poll.savePoll(f'{self.bot_data.datapath}polls/poll{poll.id}.txt')
                    return
        ctx.send(f"Error: Couldn't find poll with id `{args[0]}`")

    @commands.command(brief="Move poll to different channel",
                      help="This command deletes the message of the selected poll and resends it to the channel you are in.",
                      usage="<pollID>",
                      aliases=["movepoll"])
    async def pollmove(self, ctx, arg):
        await ctx.message.delete()
        if not arg.isdigit():
            await ctx.send(f"Error: Invalid pollID: `{arg}`", delete_after=10.0)
            return
        for poll in self.bot_data.polls:
            if poll.id == int(arg):
                orig_chnl = self.bot.get_channel(poll.msgChannelID)
                try:
                    orig_msg = await orig_chnl.fetch_message(poll.msgMessageID)
                    # Delete original message:
                    await orig_msg.delete()
                except:
                    print("Warning: Moving nonexistent poll message")
                # Set IDs to new message:
                poll.msgChannelID = ctx.channel.id
                poll.msgMessageID = ctx.message.id
                # Update the message:
                await self.updatePoll(poll, ctx.channel.id)
                poll.savePoll(f'{self.bot_data.datapath}polls/poll{poll.id}.txt')
                return
        await ctx.send(f"Error: Couldn't find poll with ID `{arg}`", delete_after=10.0)

    async def updatePoll(self, currPoll: poll, backup_channelID: int):
        channel = self.bot.get_channel(currPoll.msgChannelID)

        # TODO
        # This does not work if message doesn't exist anymore
        if not (channel is None):
            try:
                message = await channel.fetch_message(currPoll.msgMessageID)
                await message.edit(content=currPoll.getPollMsg(self.bot_data.prefix))
            except:
                resendMsg = await channel.send(currPoll.getPollMsg(self.bot_data.prefix))
                currPoll.msgMessageID = resendMsg.id

        else:
            # Channel doesn't exist:
            backup_channel = self.bot.get_channel(backup_channelID)
            backupMsg = await backup_channel.send(currPoll.getPollMsg(self.bot_data.prefix))
            currPoll.msgChannelID = backup_channelID
            currPoll.msgMessageID = backupMsg.id

    async def load_all_polls(self):
        """
        This function is only called in __init__().
        It loads all polls on disk, deletes them on disk and rewrites them to make sure the files fit the
        polls in memory.
        """
        if not os.path.exists(f'{self.bot_data.datapath}polls/'):
            os.makedirs(f'{self.bot_data.datapath}polls/')
            print(f'Created directory \'{self.bot_data.datapath}polls/\'')
            return

        # Load all files and delete them afterwards
        file_list = glob.glob(f'{self.bot_data.datapath}polls/poll*.txt')
        for file in file_list:
            pollObj = mo_poll('dummy', [])
            pollObj.loadPoll(file)
            os.remove(file)
            pollObj.id = self.bot_data.nextPollID
            self.bot_data.nextPollID += 1
            self.bot_data.polls.append(pollObj)

        # Resave all files and update the corresponding messages
        for poll in self.bot_data.polls:
            poll.savePoll(f'{self.bot_data.datapath}polls/poll{poll.id}.txt')
            await self.updatePoll(poll, self.bot_data.IDs['backup_poll_channel'])
        print(f'Successfully loaded {len(self.bot_data.polls)} poll(s) from disk.')


class pollOption:
    def __init__(self):
        self.voterIDs = []

    id: int = -1
    value: str = ''
    voterIDs: List[int] = []

    def hasVoted(self, voterID: str) -> bool:
        if int(voterID) in self.voterIDs:
            return True
        return False


class mo_poll:
    id: int = -1
    topic: str = ''
    options: List[pollOption] = []

    # Metadata:
    authorName: str = ''
    authorID: int = -1
    msgChannelID: int = -1
    msgMessageID: int = -1
    isClosed: bool = False

    custOpt: bool = False
    multiChoice: bool = False

    nextOptID: int = 1

    def __init__(self, question: str, options: list):
        # This is necessary to keep the lists contained to this instance of the class:
        self.options = []

        self.topic = question
        for opt in options:
            self.addOption(opt)

    def addOption(self, newOption: str):
        if len(newOption) != 0:
            opt = pollOption()
            opt.id = self.getOptID()
            opt.value = newOption
            self.options.append(opt)

    def addExOption(self, existingOption: pollOption):
        self.options.append(existingOption)

    def remOption(self, optionID: int):
        for opt in self.options:
            if opt.id == optionID:
                self.options.remove(opt)

    def voteOption(self, optionID: int, voterID: int):
        if not self.hasVoted(voterID) or self.multiChoice:
            for opt in self.options:
                if opt.id == optionID and not opt.hasVoted(voterID):
                    opt.voterIDs.append(voterID)
                    return

    def unvoteOption(self, optionID: int, voterID: int):
        for opt in self.options:
            if opt.id == optionID and voterID in opt.voterIDs:
                opt.voterIDs.remove(voterID)
                return

    def savePoll(self, filepath: str):
        file = configparser.ConfigParser()
        file.read(filepath)
        if not file.has_section('META'):
            file.add_section('META')

        file.set('META', 'topic', self.topic)
        file.set('META', 'authorID', str(self.authorID))
        file.set('META', 'authorName', str(self.authorName))
        file.set('META', 'msgChannelID', str(self.msgChannelID))
        file.set('META', 'msgMessageID', str(self.msgMessageID))
        file.set('META', 'nextOptID', str(self.nextOptID))

        file.set('META', 'isClosed', str(misc.bool_to_int(self.isClosed)))
        file.set('META', 'custopt', str(misc.bool_to_int(self.custOpt)))
        file.set('META', 'multiChoice', str(misc.bool_to_int(self.multiChoice)))

        for opt in self.options:
            if not file.has_section(opt.value):
                file.add_section(opt.value)
            file.set(opt.value, 'id', str(opt.id))
            file.set(opt.value, 'voterIDs', str(opt.voterIDs))

        # Remove options which aren't in memory from file:
        opt_names = [x.value for x in self.options]
        for section in file.sections():
            if section != 'META' and not (section in opt_names):
                file.remove_section(section)

        with open(filepath, 'w') as configfile:
            file.write(configfile)

    def loadPoll(self, filepath: str):
        file = configparser.ConfigParser()
        file.read(filepath)
        self.topic = file['META']['topic']
        self.authorID = int(file['META']['authorID'])
        self.authorName = str(file['META']['authorName'])
        self.msgChannelID = int(file['META']['msgChannelID'])
        self.msgMessageID = int(file['META']['msgMessageID'])
        self.nextOptID = int(file['META']['nextOptID'])

        self.isClosed = misc.int_to_bool(int(file['META']['isClosed']))
        self.custOpt = misc.int_to_bool(int(file['META']['custopt']))
        self.multiChoice = misc.int_to_bool(int(file['META']['multiChoice']))

        for section in file.sections():
            if section != 'META':
                newOpt = pollOption()
                newOpt.value = section
                newOpt.id = int(file[section]['id'])
                newOpt.voterIDs = [int(z) for z in re.findall('\d+', file[section]['voterIDs'])]
                self.addExOption(newOpt)

    def getOptID(self) -> int:
        self.nextOptID += 1
        return self.nextOptID - 1

    def hasVoted(self, voterID: int) -> bool:
        for opt in self.options:
            if opt.hasVoted(str(voterID)):
                return True
        return False

    def getVoterCount(self) -> int:
        voterIDSet = set()
        for opt in self.options:
            for voterID in opt.voterIDs:
                voterIDSet.add(voterID)
        return len(voterIDSet)

    def getOptPercentage(self, optionID: int) -> float:
        totalVotes = 0
        optVotes = 0
        for opt in self.options:
            totalVotes += len(opt.voterIDs)
            if opt.id == optionID:
                optVotes = len(opt.voterIDs)
        if totalVotes == 0:
            return 0
        return optVotes / totalVotes

    def getPollMsg(self, prefix: str) -> str:
        # This function is formatted for use with a discord bot

        # Title:
        pollTitle = f'Poll#-`{self.id}` by {self.authorName}\n'

        # isClosed:
        if self.isClosed:
            topicPre = 'diff\n- [CLOSED] '
        else:
            topicPre = 'diff\n+ '

        # Settings to string:
        settings: List[str] = []
        if self.multiChoice:
            settings.append("`multiple_choice`")
        if self.custOpt:
            settings.append("`custom_options`")
        setStr = ("\nEinstellungen: " + ", ".join(settings) + "\n") if settings else '\nKeine Einstellungen.\n'

        # Options to string:
        optStr = ''
        for opt in self.options:
            optStr += f'`{opt.id}:` {opt.value}        ({len(opt.voterIDs)}/{self.getVoterCount()}) **{int(self.getOptPercentage(opt.id)*100)}%**\n'

        # Clarifications:
        if not self.isClosed:
            clar = f'\nAbstimmen mit `{prefix}vote {self.id} <optionID>`'
        else:
            clar = '\nPoll has been closed.'
        optStr += clar

        msg = f'{pollTitle}```{topicPre}{self.topic}```{setStr}\n{optStr}'

        return msg
