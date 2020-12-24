import configparser
from typing import List, Dict
import polling
import misc_functions as misc
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
    activity_name: str = ''
    IDs: Dict[str, int] = {}
    locks: Dict[str, bool] = {}
    polls: List[polling.mo_poll] = []
    nextPollID: int = 0



    def __init__(self):
        # Initialize empty arrays:
        self.IDs = {}
        self.polls = []
        self.locks = {}

        # 'config.txt' must be in local directory, create it if not
        if not os.path.exists('config.txt'):
            # Create template file:
            config = configparser.ConfigParser()
            config.add_section('BASE')
            config.add_section('IDs')
            config.add_section('LOCKS')

            config.set('BASE', 'token', '-1')
            config.set('BASE', 'prefix', '/')
            config.set('BASE', 'datapath', 'data/')
            config.set('BASE', 'activity_name', '-1')

            config.set('IDs', 'admin_role', '-1')
            config.set('IDs', 'rule_channel', '-1')
            config.set('IDs', 'rule_message', '-1')
            config.set('IDs', 'quote_channel', '-1')
            config.set('IDs', 'backup_poll_channel', '-1')

            config.set('LOCKS', 'echo', '0')

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
                self.activity_name = config['BASE']['activity_name']

                for (ID_key, val) in config.items('IDs'):
                    self.IDs[ID_key] = int(val)

                for (lock_key, val) in config.items('LOCKS'):
                    self.locks[lock_key] = misc.int_to_bool(val)

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
        print('Successfully loaded \'config.txt\'.')
