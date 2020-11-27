'''
If you don't know what the fuck is going on here then I humbly suggest you read the documentation:
https://discordpy.readthedocs.io/en/latest/index.html#

'''


import discord
import configparser
import mathParser
import misc_functions as misc

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
        self.activityName = configFile['ACTIVITY']['name'].strip('"')



    # Parameters:
    token = ''
    prefix = ''
    ruleChannelID = -1
    ruleMessageID = -1
    activityName = ''

    #Variables
    mood = 'neutral'

# Callbacks:
client = bot_client()

@client.event
async def on_ready():
    print('{0.user} is now online.'.format(client))
    game = discord.Game(client.activityName)
    await client.change_presence(status=discord.Status.online, activity = game)


@client.event
async def on_message(message):
    # Bot doesn't answer itself:
    if message.author == client.user:
        return

    # === INTERPRET CHAT ===

    # look for commands:
    if message.content.startswith(client.prefix):
        # Remove prefix and make lowercase:
        usr_command = message.content[len(client.prefix):].lower()

        # HELP
        if usr_command.startswith("help"):
            await message.channel.send(misc.get_help_msg(client.prefix))
            return

        # RULES
        if usr_command.startswith("rules"):
            ruleChannel = client.get_channel(client.ruleChannelID)
            ruleMsg = await ruleChannel.fetch_message(client.ruleMessageID)
            await message.channel.send(ruleMsg.content)
            return

        # CALC
        if message.content.startswith(client.prefix + "calc"):
            expression = message.content[len(client.prefix + "calc"):]
            nsp = mathParser.NumericStringParser()
            try:
                result = nsp.eval(expression)
            except:
                result = "Invalid expression"
                print("Invalid command: {0}".format(message.content))

            await message.channel.send(result)
            return

        # Eastereggs
        if usr_command == "music" or message.content.startswith(client.prefix + "play"):
            await message.channel.send("I'm not the droid you're looking for!")
            return

        if usr_command.startswith('cry'):
            client.mood = 'crying'
            await message.channel.send(" :sob: I'm crying now. You made me cry. Are you happy now? :sob:")
            return

        if usr_command == 'sorry' or usr_command == 'sry':
            if client.mood == 'crying':
                client.mood = 'neutral'
                await message.channel.send('Fuck off! :unamused:')
            else:
                await message.channel.send('it\'s fine')
            return


        if usr_command.startswith('captcha'):
            await message.channel.send('I\'m not a robot I swear!')
            return

        if usr_command.startswith('putin'):
            await message.channel.send('⣿⣿⣿⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n\
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

        # This line is only reached if no command has been recognized. Act accordingly:
        await message.channel.send('I am afraid I can\'t do that {0.author.name}.'.format(message))
        print("Unrecognized command: {0}".format(message.content))
client.startup()
client.run(client.token)