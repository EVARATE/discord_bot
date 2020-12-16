"""
This file contains functions the bot needs but that are not part of the bot_client class.
This makes everything more organized.
"""
import random
import praw

def get_help_msg(prefix: str) -> str:
    # Just a very raw way of generating the help message.
    # Will probably become more procedural in the future
    # Make sure to always update this when adding new commands!

    return (":\n\
            **=== MAIN HELP MENU ===**\n\
            Regeln:\t`{0}rules`, `{0}regeln`\n\
            Hilfe:\t`{0}help`, `{0}hilfe`\n\
            Taschenrechner:\t`{0}calc <expression>`\n\
            Zufällige Zahl:\t`{0}random <range/list>`\n\
            Zitat Speichern:\t`{0}quote \"<Person>\" \"<Quote>\" \"<Optional context>\"`\n\
            Bot wiederholen lassen:\t`{0}echo <text>`\n\
            Neue Abstimmung:\t`{0}poll \"<Frage>\" \"<Option 1>\" \"<Option 2>\" ...`\n\
            Abstimmen:\t`{0}vote <pollID> <optionID>` bzw. `{0}unvote <pollID> <optionID>`\n\
            Abstimmung beenden:\t`{0}closepoll <pollID>`".format(prefix))


def startswithElement(string: str, lst: list) -> bool:
    # This function returns 'True' if str starts with at least one element
    # of list. Else it returns 'False'
    for el in lst:
        if string.startswith(el):
            return True

    # This line is only reached if no element is found
    return False


def unique_shuffle_list(originalList: list):
    randomizedList = originalList[:]
    step: int = 0
    while True:
        random.shuffle(randomizedList)
        step += 1
        if not has_el_on_same_index(randomizedList, originalList) or step >= 10000:
            return randomizedList


def has_el_on_same_index(l1: list, l2: list) -> bool:
    for i in range(min(len(l1), len(l2))):
        if l1[i] == l2[i]:
            return True
    return False


def int_in_str(string: str) -> int:
    dig = ''
    for char in string:
        if char.isdigit():
            dig += char
    return int(dig)


def bool_to_int(state: bool) -> int:
    if state:
        return 1
    else:
        return 0


def int_to_bool(num: int) -> bool:
    if num == 0:
        return False
    else:
        return True
