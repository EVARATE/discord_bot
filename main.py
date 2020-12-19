"""
If you don't know what the fuck is going on here then I humbly suggest you read the documentation:
https://discordpy.readthedocs.io/en/latest/index.html#
"""

import configparser
import glob
import os
import random
import re  # regex
from typing import List # Make everything typesafe, please
import discord
import sys
import mathParser
import misc_functions as misc
import polling
import asyncio


# Modify class:
class bot_client(discord.Client):
    def startup(self):
        # Run this function once when the bot starts for the first time
        self.get_config()
        self.loadAllPolls()

    def get_config(self):
        try:
            configFile = configparser.ConfigParser()
            configFile.read('config.txt')
            self.token = configFile['BASE']['token']
            self.prefix = configFile['BASE']['prefix']
            self.panic_msg = configFile['BASE']['panic_msg']
            self.ruleChannelID = int(configFile['RULES']['channelID'])
            self.ruleMessageID = int(configFile['RULES']['messageID'])
            self.quoteChannelID = int(configFile['QUOTES']['channelID'])
            self.adminRoleID = int(configFile['BASE']['admin_roleID'])
            self.activityName = configFile['ACTIVITY']['name']
            self.echo_lock = misc.int_to_bool(int(configFile['LOCKS']['echo_lock']))
        except:
            print('Error: Your "config.txt" is invalid. Aborting.')
            sys.exit()


    def loadAllPolls(self):
        if not os.path.exists('polls'):
            os.makedirs('polls')
            print('Created polls/ directory.')
            return
        pollFiles = glob.glob('polls/poll*.txt')
        for file in pollFiles:
            pollObj = polling.poll("dummy", [])
            pollObj.loadPoll(file)
            pollObj.id = self.nextPollID
            self.nextPollID += 1
            self.polls.append(pollObj)
        self.cleanupPollFiles()

    def savePoll(self, poll: polling.poll, cleanup=True):
        poll.savePoll(f"polls/poll{poll.id}.txt")
        if cleanup:
            self.cleanupPollFiles()

    def cleanupPollFiles(self):
        # delete all disk files and resave them:
        diskFileList = glob.glob('polls/poll*.txt')
        for file in diskFileList:
            os.remove(file)
        # resave them:
        for poll in self.polls:
            self.savePoll(poll, False)

        # Compares IDs of polls on disk with those in memory
        # and deletes the ones that are not in memory from disk

    async def updatePoll(self, pollID: int):
        for poll in self.polls:
            if poll.id == pollID:
                channel = client.get_channel(poll.msgChannelID)
                try:
                    message = await channel.fetch_message(poll.msgMessageID)
                    await message.edit(content=poll.getPollMsg(self.prefix))
                except:
                    newMsg = await channel.send(poll.getPollMsg(self.prefix))
                    poll.msgMessageID = newMsg.id
                return

    # Parameters:
    token: str = ''
    prefix: str = ''
    panic_msg: str = ''
    ruleChannelID: int = -1
    ruleMessageID: int = -1
    quoteChannelID: int = -1
    adminRoleID: int = -1
    activityName: str = ''

    # Variables
    mood: str = 'neutral'
    polls: List[polling.poll] = []
    nextPollID: int = 0

    # Locks
    echo_lock: bool = False


# Callbacks:
client = bot_client()


@client.event
async def on_ready():
    print(f'{client.user} is now online.')
    game = discord.Game(client.activityName)
    await client.change_presence(status=discord.Status.online, activity=game)
    for poll in client.polls:
        await client.updatePoll(poll.id)


@client.event
async def on_message(message):
    # Bot doesn't answer itself:
    if message.author == client.user:
        return

    # === INTERPRET CHAT ===

    if re.search('69|sixty[ -]*nine|neun[ -]*und[ -]*sechzig', message.clean_content.lower()):
        await message.channel.send("Nice!")

    # look for commands:
    if message.content.startswith(client.prefix):
        # Remove prefix and make lowercase:
        uCmd = message.content[len(client.prefix):].lower()

        # HELP
        if misc.startswithElement(uCmd, ["help", "hilfe"]):
            await message.channel.send(misc.get_help_msg(client.prefix))
            return

        # RULES
        if misc.startswithElement(uCmd, ["rules", "regel"]):
            ruleChannel = client.get_channel(client.ruleChannelID)
            ruleMsg = await ruleChannel.fetch_message(client.ruleMessageID)
            await message.channel.send(ruleMsg.content)
            return

        # CALC
        if uCmd.startswith("calc"):
            expression = message.content[len(client.prefix + "calc"):]
            nsp = mathParser.NumericStringParser()
            try:
                result = nsp.eval(expression)
            except:
                result = client.panic_msg
                print(f"Invalid command: {message.content}")

            await message.channel.send(result)
            return

        # RANDOM
        if misc.startswithElement(uCmd, ["random"]):
            # Valid cases:
            # 1. /random               -> [0,1]
            # 2. /random a b           -> [a,b]
            # 3. /random a b c d ...   -> a or b or c or d or ...

            # Turn all ',' into '.':
            uCmd = re.sub(',', '.', uCmd)
            # Find all numbers in command:
            nums = re.findall("\d+\.?\d*", uCmd)

            # Convert to floats:
            flnums = [float(z) for z in nums]

            try:
                if len(flnums) == 0:
                    # CASE 1
                    answer = str(random.random())
                elif len(flnums) == 2:
                    # CASE 2
                    if flnums[0].is_integer() and flnums[1].is_integer():
                        # If they are ints
                        answer = str(random.randrange(int(flnums[0]), int(flnums[1])))
                    else:
                        # If they are floats
                        answer = str(random.uniform(flnums[0], flnums[1]))
                elif len(flnums) > 2:
                    # CASE 3
                    answer = str(random.choice(nums))
                else:
                    answer = client.panic_msg
            except:
                answer = client.panic_msg
            await message.channel.send(answer)
            return

        # QUOTES
        if misc.startswithElement(uCmd, ["quote", "zitat"]):
            quote = re.findall('".+?"', message.clean_content)
            # Check valid syntax:
            if len(quote) < 2 or len(quote) > 3:
                await message.channel.send(client.panic_msg)
                return

            prof_name: str = quote[0].lower().strip('"')
            prof_quote: str = quote[1]
            if len(quote) == 3:
                prof_context: str = quote[2]
            else:
                prof_context: str = '"No Context given"'

            # Read quote count for that prof:
            ifile = configparser.ConfigParser()
            ifile.read("quotes.txt")
            try:
                quote_count: int = int(ifile[prof_name]['count'])
            except:
                quote_count: int = 0

            try:
                ofile = configparser.ConfigParser()
                ofile.read('quotes.txt')
                if not ofile.has_section(prof_name):
                    ofile.add_section(prof_name)
                ofile.set(prof_name, 'count', str(quote_count + 1))
                ofile.set(prof_name, 'q#' + str(quote_count), prof_quote + " " + prof_context)

                with open('quotes.txt', 'w') as configfile:
                    ofile.write(configfile)
                await message.channel.send("Saved quote.")
            except:
                await message.channel.send(client.panic_msg)
                print(f"Error handling quote: {message.content}")
                return
            # Send to quote Channel:
            if client.quoteChannelID != -1:
                msg = f":\n**Person:** {prof_name}\n**Zitat:** {prof_quote}\n**Kontext:** {prof_context}"
                channel = client.get_channel(client.quoteChannelID)
                await channel.send(msg)
            return

        # POLLING
        if misc.startswithElement(uCmd, ['poll', 'vote', 'unvote', 'closepoll']):
            # Delete Message for anonymity:
            await message.delete()
            if uCmd.startswith('poll'):
                args = re.findall('".+?"', message.clean_content)
                if len(args) <= 1:
                    await message.channel.send("Error: Not enough arguments!", delete_after=5.0)
                    print(f"Invalid poll syntax: {message.clean_content[(len(client.prefix) + 4):]}")
                    return
                newPoll = polling.poll(args[0].strip('"'), [z.strip('"') for z in args[1:]])
                newPoll.authorID = message.author.id
                newPoll.authorName = message.author.name
                newPoll.msgChannelID = message.channel.id
                newPoll.id = client.nextPollID
                client.nextPollID += 1
                dcMessage = await message.channel.send(newPoll.getPollMsg(client.prefix))
                newPoll.msgMessageID = dcMessage.id

                client.polls = client.polls + [newPoll]
                client.savePoll(newPoll)
            elif uCmd.startswith('vote'):
                # /vote <pollID> <optID>

                args = re.findall('\d+', message.clean_content)
                if len(args) != 2:
                    await message.channel.send("Error: Invalid number of arguments!", delete_after=5.0)
                    print(f"Invalid vote syntax: {message.clean_content[(len(client.prefix) + 4):]}")
                    return
                pollID = int(args[0])
                optID = int(args[1])
                for poll in client.polls:
                    if poll.id == pollID:
                        poll.voteOption(optID, message.author.id)
                        await client.updatePoll(pollID)
                        client.savePoll(poll)
                        return

            elif uCmd.startswith('unvote'):
                # /vote <pollID> <optID>

                args = re.findall('\d+', message.clean_content)
                if len(args) != 2:
                    await message.channel.send('Error: Invalid number of arguments!', delete_after=5.0)
                    print(f"Invalid unvote syntax: {message.clean_content[(len(client.prefix) + 4):]}")
                    return
                pollID = int(args[0])
                optID = int(args[1])
                for poll in client.polls:
                    if poll.id == pollID:
                        poll.unvoteOption(optID, message.author.id)
                        await client.updatePoll(pollID)
                        client.savePoll(poll)
                        return

            elif uCmd.startswith('closepoll'):
                args = re.findall('\d+', message.clean_content)
                if len(args) != 1:
                    await message.channel.send('Error: Invalid number of arguments!', delete_after=5.0)
                    return
                pollID = int(args[0])
                for poll in client.polls:
                    if poll.id == pollID:
                        if poll.authorID != message.author.id:
                            await message.channel.send('Error: You are not the poll author!', delete_after=5.0)
                            return
                        poll.isClosed = True
                        await client.updatePoll(pollID)
                        os.remove(f'polls/poll{poll.id}.txt')
                        client.polls[:] = [x for x in client.polls if x.id != pollID]
                        await message.channel.send(f'Closed poll#-{pollID}', delete_after=5.0)

            return

        # ECHO
        if uCmd.startswith('echo') and not uCmd.startswith('echolock'):
            if not client.echo_lock:
                text = message.clean_content[(len(client.prefix) + 4):]
                await message.delete()
                await message.channel.send(text)
                return
            adm_role = discord.utils.get(message.guild.roles, id=client.adminRoleID)
            if adm_role in message.author.roles:
                text = message.clean_content[(len(client.prefix) + 4):]
                await message.delete()
                await message.channel.send(text)
                return
            else:
                await message.channel.send('This command is currently locked.', delete_after=5.0)
                return

        # ECHO LOCK
        if uCmd.startswith('echolock'):
            # Only admins can do this:
            adm_role = discord.utils.get(message.guild.roles, id=client.adminRoleID)
            if not adm_role in message.author.roles:
                await message.channel.send('You do not have permission for this command!', delete_after=5.0)
                await message.delete()
                return
            # /echolock         -> [status]
            # /echolock toggle  -> [status]

            if misc.startswithElement(uCmd[8:].lstrip(), ['toggle', 'switch', 'change']):
                client.echo_lock = not client.echo_lock
                lockStr = 'Unlocked' if client.echo_lock else 'Locked'
                await message.channel.send(f'`{client.prefix}echo` is now {lockStr}')
                # Update config.txt:
                file = configparser.ConfigParser()
                file.read('config.txt')
                file.set('LOCKS', 'echo_lock', str(misc.bool_to_int(client.echo_lock)))
                with open('config.txt', 'w') as configfile:
                    file.write(configfile)

            else:
                lockStr = 'Unlocked' if client.echo_lock else 'Locked'
                await message.channel.send(f'`{client.prefix}echo` is {lockStr}')
            return

        # TEST
        if uCmd.startswith('test'):
            retMSG = await message.channel.send('0')
            for i in range(120):
                await asyncio.sleep(1)
                await retMSG.edit(content=str(i))
            return

        # COUNTDOWN
        if uCmd.startswith('countdown'):
            nums = re.findall('\d+', uCmd)
            count: int = 10 if len(nums) == 0 else int(nums[0])
            if count > 500:
                await message.channel.send('Dude, I don\'t have all day!')
                return

            msg = await message.channel.send(f'Countdown: {count}')
            while count > 0:
                count += -1
                await asyncio.sleep(1)
                await msg.edit(content=(f'Countdown: {count}' if count != 0 else '**NOW**'))
            return

        # Eastereggs
        if misc.startswithElement(uCmd, ['music', 'play', 'skip', 'queue']):
            await message.channel.send("I'm not the droid you're looking for!")
            return

        if uCmd.startswith('cry'):
            client.mood = 'crying'
            await message.channel.send(" :sob: I'm crying now. You made me cry. Are you happy now? :sob:")
            return

        if uCmd == 'sorry' or uCmd == 'sry':
            if client.mood != 'neutral':
                client.mood = 'neutral'
                await message.channel.send('Fuck off! :unamused:')
            else:
                await message.channel.send('it\'s fine')
            return

        if uCmd == 'rage':
            client.mood = "angry"
            await message.channel.send('Grrrrrr :rage:')
            return

        if uCmd.startswith('captcha'):
            await message.channel.send('I\'m not a robot I swear!')
            return

        if uCmd.startswith('putin'):
            await message.channel.send('All hail Putin! \n\t\t\t⣿⣿⣿⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣵⣿⣿⣿⠿⡟⣛⣧⣿⣯⣿⣝⡻⢿⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⠋⠁⣴⣶⣿⣿⣿⣿⣿⣿⣿⣦⣍⢿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⢷⠄⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⢼⣿⣿⣿⣿\n\
            ⢹⣿⣿⢻⠎⠔⣛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⣿⣿⣿⣿\n\
            ⢸⣿⣿⠇⡶⠄⣿⣿⠿⠟⡛⠛⠻⣿⡿⠿⠿⣿⣗⢣⣿⣿⣿⣿\n\
            ⠐⣿⣿⡿⣷⣾⣿⣿⣿⣾⣶⣶⣶⣿⣁⣔⣤⣀⣼⢲⣿⣿⣿⣿\n\
            ⠄⣿⣿⣿⣿⣾⣟⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⢟⣾⣿⣿⣿⣿\n\
            ⠄⣟⣿⣿⣿⡷⣿⣿⣿⣿⣿⣮⣽⠛⢻⣽⣿⡇⣾⣿⣿⣿⣿⣿\n\
            ⠄⢻⣿⣿⣿⡷⠻⢻⡻⣯⣝⢿⣟⣛⣛⣛⠝⢻⣿⣿⣿⣿⣿⣿\n\
            ⠄⠸⣿⣿⡟⣹⣦⠄⠋⠻⢿⣶⣶⣶⡾⠃⡂⢾⣿⣿⣿⣿⣿⣿\n\
            ⠄⠄⠟⠋⠄⢻⣿⣧⣲⡀⡀⠄⠉⠱⣠⣾⡇⠄⠉⠛⢿⣿⣿⣿\n\
            ⠄⠄⠄⠄⠄⠈⣿⣿⣿⣷⣿⣿⢾⣾⣿⣿⣇⠄⠄⠄⠄⠄⠉⠉\n\
            ⠄⠄⠄⠄⠄⠄⠸⣿⣿⠟⠃⠄⠄⢈⣻⣿⣿⠄⠄⠄⠄⠄⠄⠄\n\
            ⠄⠄⠄⠄⠄⠄⠄⢿⣿⣾⣷⡄⠄⢾⣿⣿⣿⡄⠄⠄⠄⠄⠄⠄\n\
            ⠄⠄⠄⠄⠄⠄⠄⠸⣿⣿⣿⠃⠄⠈⢿⣿⣿⠄⠄⠄⠄⠄⠄⠄')
            return

        if misc.startswithElement(uCmd, ['trump', 'donald', 'orangeman']):
            await message.channel.send('STOP THE COUNT! \n\t\t\t⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠋⠉⡉⣉⡛⣛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠄⠄⠄⠄⠄⢀⣸⣿⣿⡿⠿⡯⢙⠿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⡿⠄⠄⠄⠄⠄⡀⡀⠄⢀⣀⣉⣉⣉⠁⠐⣶⣶⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⡇⠄⠄⠄⠄⠁⣿⣿⣀⠈⠿⢟⡛⠛⣿⠛⠛⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⡆⠄⠄⠄⠄⠄⠈⠁⠰⣄⣴⡬⢵⣴⣿⣤⣽⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣿⡇⠄⢀⢄⡀⠄⠄⠄⠄⡉⠻⣿⡿⠁⠘⠛⡿⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⡿⠃⠄⠄⠈⠻⠄⠄⠄⠄⢘⣧⣀⠾⠿⠶⠦⢳⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⣿⣶⣤⡀⢀⡀⠄⠄⠄⠄⠄⠄⠻⢣⣶⡒⠶⢤⢾⣿⣿⣿⣿⣿⣿⣿\n\
            ⣿⣿⣿⣿⡿⠟⠋⠄⢘⣿⣦⡀⠄⠄⠄⠄⠄⠉⠛⠻⠻⠺⣼⣿⠟⠋⠛⠿⣿⣿\n\
            ⠋⠉⠁⠄⠄⠄⠄⠄⠄⢻⣿⣿⣶⣄⡀⠄⠄⠄⠄⢀⣤⣾⣿⣿⡀⠄⠄⠄⠄⢹\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢻⣿⣿⣿⣷⡤⠄⠰⡆⠄⠄⠈⠉⠛⠿⢦⣀⡀⡀⠄\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⢿⣿⠟⡋⠄⠄⠄⢣⠄⠄⠄⠄⠄⠄⠄⠈⠹⣿⣀\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠘⣷⣿⣿⣷⠄⠄⢺⣇⠄⠄⠄⠄⠄⠄⠄⠄⠸⣿\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠹⣿⣿⡇⠄⠄⠸⣿⡄⠄⠈⠁⠄⠄⠄⠄⠄⣿\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢻⣿⡇⠄⠄⠄⢹⣧⠄⠄⠄⠄⠄⠄⠄⠄⠘')
            return

        if uCmd.startswith('reverse') or uCmd.startswith('undo') or uCmd.startswith('Konter'):
            await message.channel.send("take that! \n\t\t\t⠐⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠂\n\
            ⠄⠄⣰⣾⣿⣿⣿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣆⠄⠄\n\
            ⠄⠄⣿⣿⣿⡿⠋⠄⡀⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠋⣉⣉⣉⡉⠙⠻⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣿⣇⠔⠈⣿⣿⣿⣿⣿⡿⠛⢉⣤⣶⣾⣿⣿⣿⣿⣿⣿⣦⡀⠹⠄⠄\n\
            ⠄⠄⣿⣿⠃⠄⢠⣾⣿⣿⣿⠟⢁⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⣿⣿⣿⠟⢁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⣿⡟⠁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⠋⢠⣾⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⡿⠁⣰⣿⣿⣿⣿⣿⣿⣿⣿⠗⠄⠄⠄⠄⣿⣿⣿⣿⣿⣿⣿⡟⠄⠄\n\
            ⠄⠄⣿⡿⠁⣼⣿⣿⣿⣿⣿⣿⡿⠋⠄⠄⠄⣠⣄⢰⣿⣿⣿⣿⣿⣿⣿⠃⠄⠄\n\
            ⠄⠄⡿⠁⣼⣿⣿⣿⣿⣿⣿⣿⡇⠄⢀⡴⠚⢿⣿⣿⣿⣿⣿⣿⣿⣿⡏⢠⠄⠄\n\
            ⠄⠄⠃⢰⣿⣿⣿⣿⣿⣿⡿⣿⣿⠴⠋⠄⠄⢸⣿⣿⣿⣿⣿⣿⣿⡟⢀⣾⠄⠄\n\
            ⠄⠄⢀⣿⣿⣿⣿⣿⣿⣿⠃⠈⠁⠄⠄⢀⣴⣿⣿⣿⣿⣿⣿⣿⡟⢀⣾⣿⠄⠄\n\
            ⠄⠄⢸⣿⣿⣿⣿⣿⣿⣿⠄⠄⠄⠄⢶⣿⣿⣿⣿⣿⣿⣿⣿⠏⢀⣾⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⣶⣶⣶⣿⣿⣿⣿⣿⣿⣿⠋⣠⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣼⣿⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢁⣴⣿⣿⣿⣿⣿⣿⣿⠄⠄\n\
            ⠄⠄⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢁⣴⣿⣿⣿⣿⠗⠄⠄⣿⣿⠄⠄\n\
            ⠄⠄⣆⠈⠻⢿⣿⣿⣿⣿⣿⣿⠿⠛⣉⣤⣾⣿⣿⣿⣿⣿⣇⠠⠺⣷⣿⣿⠄⠄\n\
            ⠄⠄⣿⣿⣦⣄⣈⣉⣉⣉⣡⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⠉⠁⣀⣼⣿⣿⣿⠄⠄\n\
            ⠄⠄⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣾⣿⣿⡿⠟⠄⠄\n\
            ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄")
            return

        # This line is only reached if no command has been recognized. Act accordingly:
        await message.channel.send(f'I am afraid I can\'t do that {message.author.name}.')
        print(f"Unrecognized command: {message.content}")


client.startup()
client.run(client.token)
