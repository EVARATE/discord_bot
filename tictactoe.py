import misc_functions as misc
from typing import List
import discord
from discord.ext import commands
import bot_database
import random


class tic_tac_toe(commands.Cog):
    """
    This is a discord cog.
    """
    tttGames = []
    next_ttt_ID = 0

    def __init__(self, bot, database):
        self.bot = bot
        self.bot_data: bot_database.bot_database = database
        self.tttGames: List[tttGame] = []

    @commands.command(brief="Create new Game",
                      help="Create a new Tic Tac Toe game. One more player must join to play.")
    async def tttnew(self, ctx):
        await ctx.message.delete()

        for game in self.tttGames:
            if ctx.author.id == game.player1ID:
                game.player1ID = -1
                game.player1Name = ''
                await self.updateGameMsg(game)
            elif ctx.author.id == game.player2ID:
                game.player2ID = -1
                game.player2Name = ''
                await self.updateGameMsg(game)

        newtttGame = tttGame(self.get_ttt_ID(), ctx.author.name, ctx.author.id)
        gameMsg = await ctx.send(newtttGame.getBoardStr(self.bot_data.prefix))
        newtttGame.msgChannelID = gameMsg.channel.id
        newtttGame.msgMessageID = gameMsg.id
        self.tttGames.append(newtttGame)

    @commands.command(brief="Join an open game",
                      help="Join an open Tic Tac Toe game.",
                      usage="<gameID>")
    async def tttjoin(self, ctx, arg):
        await ctx.message.delete()
        if not arg.isdigit():
            await ctx.send(f"Error: Invalid gameID: `{arg}`", delete_after=10.0)
            return

        # Exit any other games author is in:
        for game in self.tttGames:
            if ctx.author.id == game.player1ID:
                game.player1ID = -1
                game.player1Name = ''
                await self.updateGameMsg(game)
            elif ctx.author.id == game.player2ID:
                game.player2ID = -1
                game.player2Name = ''
                await self.updateGameMsg(game)

        for game in self.tttGames:
            if game.id == int(arg) and not game.isRunning:
                game.addPlayer2(ctx.author.name, ctx.author.id)
                game.startGame()
                await self.updateGameMsg(game)
            else:
                await ctx.send(f"Couldn't find open game with id `{arg}`", delete_after=10.0)

    @commands.command(brief="Play a move",
                      help="Play a move in the game you are in.\n\nExample:\t/ttt A1\n\n'1a' and '1A' are also valid.",
                      usage="<coordinate>")
    async def ttt(self, ctx, arg):
        await ctx.message.delete()
        if len(arg) != 2:
            ctx.send("Error: only two letters/digits allowed. E.g. `A1` or `a1`", delete_after=10.0)
            return
        if  arg[0].lower() in ['a', 'b', 'c'] and arg[1] in ['1', '2', '3']:
            letterFirst = True
        elif arg[1].lower() in ['a', 'b', 'c'] and arg[0] in ['1', '2', '3']:
            letterFirst = False
        else:
            ctx.send("Error: Coordinates must be e.g. `A1` or `a1`", delete_after=10.0)
            return

        for game in self.tttGames:
            # Find game in which author is player:
            if ctx.author.id in [game.player1ID, game.player2ID]:
                if letterFirst:
                    game.makeMove(ctx.author.name, game.charToYcoord(arg[0]) - 1, int(arg[1]) - 1)
                else:
                    game.makeMove(ctx.author.name, game.charToYcoord(arg[1]) - 1, int(arg[0]) - 1)

                await self.updateGameMsg(game)
                return
        await ctx.send("Error playing move.", delete_after=5.0)

    async def updateGameMsg(self, game):
        channel = self.bot.get_channel(game.msgChannelID)

        if not (channel is None):
            try:
                message = await channel.fetch_message(game.msgMessageID)
                await message.edit(content=game.getBoardStr(self.bot_data.prefix))
            except:
                resendMsg = await channel.send(game.getBoardStr(self.bot_data.prefix))
                game.msgMessageID = resendMsg.id
        else:
            print(f"Couldn't find channel and message of ttt_game '{tttGame.id}'")

    def get_ttt_ID(self) -> int:
        self.next_ttt_ID += 1
        return self.next_ttt_ID - 1


class tttGame:
    id: int = -1
    player1Name: str = ""
    player2Name: str = ""
    player1ID: int = -1
    player2ID: int = -1
    player1sTurn: bool = False

    gameMatrix = []
    isRunning: bool = False

    msgChannelID: int = -1
    msgMessageID: int = -1

    def __init__(self, gameID: int, player1Name: str, player1ID: int):
        self.gameMatrix = [[' ', ' ', ' '],
                           [' ', ' ', ' '],
                           [' ', ' ', ' ']]
        self.isRunning = False
        self.id = gameID
        self.player1Name = player1Name
        self.player1ID = player1ID
        self.player1sTurn = False

    def addPlayer2(self, player2Name: str, player2ID: int):
        if not self.isRunning:
            self.player2Name = player2Name
            self.player2ID = player2ID

    def startGame(self):
        self.isRunning = True
        rnd = random.random()
        self.player1sTurn = True if rnd < 0.5 else False

    def makeMove(self, playerName: str, ycoord: int, xcoord: int):
        activePlayer = self.isActivePlayer(playerName)
        freeSlot = True if self.gameMatrix[xcoord][ycoord] == ' ' else False
        if activePlayer and freeSlot:
            if self.player1sTurn:
                self.gameMatrix[xcoord][ycoord] = 'X'
            else:
                self.gameMatrix[xcoord][ycoord] = 'O'
            self.player1sTurn = not self.player1sTurn
            self.checkWinner()

    def checkWinner(self):
        pass

    def getBoardStr(self, prefix: str):
        if not self.isRunning or self.player2ID == -1:
            player2Str = f"*Waiting for player 2 via*  `{prefix}tttjoin {self.id}`"
        else:
            player2Str = f"**{self.player2Name}**" if not self.player1sTurn else self.player2Name

        return f'**Tic Tac Toe**\t\tGame-`{self.id}`' \
               f'\nPlayer 1  (`X`):    {f"**{self.player1Name}**" if self.player1sTurn else self.player1Name}' \
               f'\nPlayer 2 (`O`):    {player2Str}' \
               f'\n\n```\n' \
               f'      1     2     3\n' \
               f'A     {self.gameMatrix[0][0]}  |  {self.gameMatrix[1][0]}  |  {self.gameMatrix[2][0]}\n' \
               f'    -----|-----|-----\n' \
               f'B     {self.gameMatrix[0][1]}  |  {self.gameMatrix[1][1]}  |  {self.gameMatrix[2][1]}\n' \
               f'    -----|-----|-----\n' \
               f'C     {self.gameMatrix[0][2]}  |  {self.gameMatrix[1][2]}  |  {self.gameMatrix[2][2]}\n' \
               f'```\nPlay via e.g. `{prefix}ttt A1` for A1'

    def isActivePlayer(self, playerName: str) -> bool:
        if self.player1sTurn and playerName == self.player1Name:
            return True
        elif not self.player1sTurn and playerName == self.player2Name:
            return True
        else:
            return False

    def charToYcoord(self, char: str) -> int:
        char = char.lower()
        if char == 'a':
            return 1
        elif char == 'b':
            return 2
        else:
            return 3
