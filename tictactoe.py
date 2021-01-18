import misc_functions as misc
from typing import List
import discord
from discord.ext import commands
import bot_database
import random
import re


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
    async def tnew(self, ctx):
        await ctx.message.delete()
        # leave all other games:
        for game in self.tttGames:
            if game.removePlayer(ctx.author.id):
                await self.updateGameMsg(game)

        # Create new game:
        newGame = tttGame(self.get_ttt_ID(), ctx.author.id, ctx.author.name)

        # Create new Message:
        gameMsg = await ctx.send(newGame.getBoardStr(self.bot_data.prefix))
        newGame.msgChannelID = gameMsg.channel.id
        newGame.msgMessageID = gameMsg.id

        self.tttGames.append(newGame)

    @commands.command(brief="Join an open game",
                      help="Join an open Tic Tac Toe game.",
                      usage="<gameID>")
    async def tjoin(self, ctx, arg):
        await ctx.message.delete()
        # Check syntax:
        if not arg.isdigit():
            await ctx.send(f'Error: Invalid gameID: `{arg}`', delete_after=10.0)
            return

        # Leave all other games:
        for game in self.tttGames:
            if game.removePlayer(ctx.author.id):
                await self.updateGameMsg(game)

        # Join game if it exists:
        for game in self.tttGames:
            if game.id == int(arg):
                game.addPlayer(ctx.author.id, ctx.author.name)
                await self.updateGameMsg(game)
                return

        await ctx.send(f'Error: Couldn\'t find game with id `{arg}`', delete_after=10.0)

    @commands.command(brief="Play a move",
                      help="Play a move in the game you are in.\n\nExample:\t/t A1\n\n'1a' and '1A' are also valid.",
                      usage="<coordinate>")
    async def t(self, ctx, arg):
        await ctx.message.delete()
        # Check syntax:
        if len(arg) != 2 or not re.match('[abcABC][123]|[123][abcABC]', arg):
            await ctx.send("Error: Coordinates must be two digits/letters such as `A1` or `a1`.", delete_after=10.0)
            return

        if arg[0].lower() in ['a', 'b', 'c'] and arg[1] in ['1', '2', '3']:
            letterFirst = True
        elif arg[1].lower() in ['a', 'b', 'c'] and arg[0] in ['1', '2', '3']:
            letterFirst = False
        else:
            await ctx.send("Error: Coordinates must be two digits/letters such as `A1` or `a1`.", delete_after=10.0)
            return

        # Find game player is in:
        for game in self.tttGames:
            if ctx.author.id in [game.player1['id'], game.player2['id']]:
                if letterFirst:
                    game.makeMove(ctx.author.id, int(arg[1]) - 1, game.charToCoord(arg[0]) - 1)
                else:
                    game.makeMove(ctx.author.id, int(arg[0]) - 1, game.charToCoord(arg[1]) - 1)
                await self.updateGameMsg(game)

    @commands.command(brief="Leave all games.",
                      help="Leave all games you are in.",
                      aliases=['tquit', 'texit'])
    async def tleave(self, ctx):
        for game in self.tttGames:
            if game.removePlayer(ctx.author.id):
                self.updateGameMsg(game)

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
    def __init__(self, gameID: int, player1ID: int, player1Name: str):
        # Setup:
        self.msgChannelID: int = -1
        self.msgMessageID: int = -1

        self.id: int = gameID
        self.player1: Dict = {'name': '', 'id': -1}  # Player will be added later. This is just a template
        self.player2: Dict = {'name': '', 'id': -1}
        self.isPlayer1Turn: bool = False
        self.isRunning: bool = False
        self.gameMatrix = [[' ', ' ', ' '],
                           [' ', ' ', ' '],
                           [' ', ' ', ' ']]

        self.addPlayer(player1ID, player1Name)

    def addPlayer(self, playerID: int, playerName: str):
        if self.player1['id'] == -1:
            self.player1['id'] = playerID
            self.player1['name'] = playerName
        elif self.player2['id'] == -1:
            self.player2['id'] = playerID
            self.player2['name'] = playerName
        else:
            return

        if -1 not in [self.player1['id'], self.player2['id']]:
            self.isRunning = True
            self.restartGame()

    def removePlayer(self, playerID: int) -> bool:  # True if player was removed
        if self.player1['id'] == playerID:
            # Move player2 to player1 and delete player2:
            self.player1['id'] = self.player2['id']
            self.player1['name'] = self.player2['name']
            self.player2['id'] = -1
            self.player2['name'] = ''
            self.isRunning = False
            return True
        elif self.player2['id'] == playerID:
            # Just remove player2:
            self.player2['id'] = -1
            self.player2['name'] = ''
            self.isRunning = False
            return True
        return False

    def restartGame(self):
        if -1 not in [self.player1['id'], self.player2['id']]:
            self.gameMatrix = [[' ', ' ', ' '],
                               [' ', ' ', ' '],
                               [' ', ' ', ' ']]
            self.isPlayer1Turn = random.choice([True, False])

    def makeMove(self, playerID: int, xcoord: int, ycoord: int):
        if self.checkWin() != '':
            self.gameMatrix = [[' ', ' ', ' '],
                               [' ', ' ', ' '],
                               [' ', ' ', ' ']]

        if playerID == self.player1['id'] and self.isPlayer1Turn and self.gameMatrix[xcoord][ycoord] == ' ':
            self.gameMatrix[xcoord][ycoord] = 'X'
            self.isPlayer1Turn = not self.isPlayer1Turn
        elif playerID == self.player2['id'] and not self.isPlayer1Turn and self.gameMatrix[xcoord][ycoord] == ' ':
            self.gameMatrix[xcoord][ycoord] = 'O'
            self.isPlayer1Turn = not self.isPlayer1Turn

    def getBoardStr(self, prefix: str):
        player1Str = self.player1['name'] if self.player1[
                                                 'id'] != -1 else f'*Waiting for Player 1 via* `{prefix}tjoin {self.id}`'
        player2Str = self.player2['name'] if self.player2[
                                                 'id'] != -1 else f'*Waiting for Player 2 via* `{prefix}tjoin {self.id}`'

        winChar = self.checkWin()
        if winChar == 'X':
            winStr = f'{self.player1["name"]} has won!!!'
        elif winChar == 'O':
            winStr = f'{self.player2["name"]} has won!!!'
        elif winChar == 'd':
            winStr = 'Game was a draw.'
        else:
            winStr = ''

        return f'**Tic Tac Toe:** Game - `{self.id}`\n' \
               f'Player1:  (`X`): {f"**{player1Str}**" if self.isPlayer1Turn else player1Str}\n' \
               f'Player2: (`O`): {f"**{player2Str}**" if not self.isPlayer1Turn else player2Str}\n\n' \
               f'```\n' \
               f'      1     2     3\n' \
               f'A     {self.gameMatrix[0][0]}  |  {self.gameMatrix[1][0]}  |  {self.gameMatrix[2][0]}\n' \
               f'    -----|-----|-----\n' \
               f'B     {self.gameMatrix[0][1]}  |  {self.gameMatrix[1][1]}  |  {self.gameMatrix[2][1]}\t{winStr}\n' \
               f'    -----|-----|-----\n' \
               f'C     {self.gameMatrix[0][2]}  |  {self.gameMatrix[1][2]}  |  {self.gameMatrix[2][2]}\n' \
               f'```{ "Play any move to restart the game." if winChar != "" else ""}\n' \
               f'Play via e.g. `{prefix}t A1` for A1'

    def checkWin(self) -> str:  # returns either ['X', 'O', 'd', ''], 'd' stands for 'draw'
        for sym in ['X', 'O']:

            checkDraw = True
            for line in self.gameMatrix:
                for el in line:
                    if el == ' ':
                        checkDraw = False

            if [sym, sym, sym] in [[self.gameMatrix[0][0], self.gameMatrix[1][0], self.gameMatrix[2][0]],  # Horizontal
                                   [self.gameMatrix[0][1], self.gameMatrix[1][1], self.gameMatrix[2][1]],
                                   [self.gameMatrix[0][2], self.gameMatrix[1][2], self.gameMatrix[2][2]],
                                   [self.gameMatrix[0][0], self.gameMatrix[0][1], self.gameMatrix[0][2]],  # Vertical
                                   [self.gameMatrix[1][0], self.gameMatrix[1][1], self.gameMatrix[1][2]],
                                   [self.gameMatrix[2][0], self.gameMatrix[2][1], self.gameMatrix[2][2]],
                                   [self.gameMatrix[0][0], self.gameMatrix[1][1], self.gameMatrix[2][2]],  # Diagonal
                                   [self.gameMatrix[2][0], self.gameMatrix[1][1], self.gameMatrix[0][2]]]:
                retVal = sym
            elif checkDraw:
                retVal = 'd'
            else:
                retVal = ''
        return retVal

    def charToCoord(self, char: str) -> int:
        char = char.lower()
        if char == 'a':
            return 1
        elif char == 'b':
            return 2
        else:
            return 3

