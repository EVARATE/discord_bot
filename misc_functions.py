"""
This file contains functions the bot needs but that are not part of the bot_client class.
This makes everything more organized.
"""
import random

def get_help_msg(prefix: str) -> str:
    # Just a very raw way of generating the help message.
    # Will probably become more procedural in the future
    # Make sure to always update this when adding new commands!

    return (":\n\
            **=== MAIN HELP MENU ===**\n\
            Regeln:\t`{0}rules`, `{0}regeln`\n\
            Hilfe:\t`{0}help`, `{0}hilfe`\n\
            Taschenrechner:\t`{0}calc <expression>`\n\
            Zufällige Zahl:\t`{0}random <range/list>`".format(prefix))

def startswithElement(string: str, lst: list) -> bool:
    # This function returns 'True' if str starts with at least one element
    # of list. Else it returns 'False'
    for el in lst:
            if string.startswith(el):
                return True

    # This line is only reached if no element is found
    return False
