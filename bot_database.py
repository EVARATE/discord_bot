import configparser
from typing import List, Dict
import polling
import os
import glob
import sys


class bot_database:
    """
    This class has nothing to do with the bot directly. It just stores all kinds of variables and other data
    the bot needs.
    """
    token: str = ''
    prefix: str = ''
    datapath: str = ''
    IDs: Dict[str, int] = {}
    polls: List[polling.mo_poll] = []
    nextPollID: int = 0

    def __init__(self):
        # Initialize empty arrays:
        self.IDs = {}
        self.polls = []

        # 'config.txt' must be in local directory, create it if not
        if not os.path.exists('config.txt'):
            # Create template file:
            config = configparser.ConfigParser()
            config.add_section('BASE')
            config.add_section('IDs')

            config.set('BASE', 'token', '-1')
            config.set('BASE', 'prefix', '/')
            config.set('BASE', 'datapath', 'data/')

            config.set('IDs', 'admin_role', '-1')
            config.set('IDs', 'rule_channel', '-1')
            config.set('IDs', 'rule_message', '-1')
            config.set('IDs', 'quote_channel', '-1')
            config.set('IDs', 'backup_poll_channel', '-1')

            with open('config.txt', 'w') as configfile:
                config.write(configfile)

            print('Created \'config.txt\'. Please enter available values (or \'-1\' if unavailable) and restart.')
            sys.exit()
        else:
            # Try to read 'config.txt':
            try:
                config = configparser.ConfigParser()
                config.read('config.txt')
                self.token = config['BASE']['token']
                self.prefix = config['BASE']['prefix']
                self.datapath = config['BASE']['datapath']

                for (ID_key, val) in config.items('IDs'):
                    self.IDs[ID_key] = int(val)

            except:
                print('Error reading \'config.txt\'. Please fix it or delete it to generate a new one. Aborting.')
                sys.exit()

        if not os.path.exists(self.datapath):
            os.makedirs(self.datapath)
            print(f'Created directory: \'{self.datapath}\'')

        # Final checks:
        if len(self.token) != 59:
            print('Error: Invalid token. Aborting.')
            sys.exit()
        print('Successfully loaded database.')
