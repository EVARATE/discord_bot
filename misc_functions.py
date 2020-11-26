'''
This file contains functions the bot needs but that are not part of the bot_client class.
'''

import configparser

def load_config():
    configFile = configparser.ConfigParser()
    configFile.read('config.txt')


    self.token = configFile['BASE']['token']
    self.ruleChannelID = configFile['RULES']['channelID']
    self.ruleMessageID = configFile['RULES']['messageID']