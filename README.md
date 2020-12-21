# About this branch

This is a complete rewrite of the discord bot. Before every message was scanned for commands with
if/else statements which is kindof messy.
The goal of this rewrite is to use the existing command framework of the discord.py library.

Here is its documentation:
https://discordpy.readthedocs.io/en/latest/index.html

## Dependencies
The following packages should be available via `pip` and are required:
 - discord.py
 - configparser
 
 ## Setting up your bot
 To start the bot run the `main.py` file. If you do that in a terminal you will see how it creates multiple files
 and directories. Open the `config.txt` file and fill in as many values as you have. Else, leave them as they are.
 Rerun `main.py`.