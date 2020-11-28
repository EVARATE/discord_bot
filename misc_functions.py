"""
This file contains functions the bot needs but that are not part of the bot_client class.
This makes everything more organized.
"""


def get_help_msg(prefix: str) -> str:
    # Just a very raw way of generating the help message.
    # Will probably become more procedural in the future
    # Make sure to always update this when adding new commands!

    return (":\n\
            **=== MAIN HELP MENU ===**\n\
            Regeln:\t`{0}rules`\n\
            Hilfe:\t`{0}help`\n\
            Taschenrechner:\t`{0}calc`/hel\n".format(prefix))
