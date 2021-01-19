from discord.ext import commands
from typing import Dict


class connect_four(commands.Cog):
    '''
    This is a cog for a discord bot.
    '''
    def __init__(self, bot, prefix: str):
        self.bot = bot
        self.prefix = prefix

    @commands.command(brief="Create new game")
    async def fwnew(self, ctx):
        await ctx.message.delete()
        game = connect_four_game(0, ctx.author.id, ctx.author.name)
        await ctx.send(game.getBoardStr())


class connect_four_game:
    def __init__(self, gameID: int, player1ID: int, player1Name: str):
        self.gameMatrix = [[' ', ' ', ' ', ' ', ' ', ' ', ' '],
                           [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                           [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                           [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                           [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                           [' ', ' ', ' ', ' ', ' ', ' ', ' ']]
        self.id = gameID
        self.player1: Dict = {'id': -1, 'name': '', 'chip_count': 21}   # Player1 will be assigned later, this is just
        self.player2: Dict = {'id': -1, 'name': '', 'chip_count': 21}   # a template

        self.addPlayer(player1ID, player1Name)

    def addPlayer(self, playerID: int, playerName: str):
        if self.player1['id'] == -1:
            self.player1['id'] = playerID
            self.player1['name'] = playerName
        elif self.player2['id'] == -1:
            self.player2['id'] = playerID
            self.player2['name'] = playerName

    def getBoardStr(self):
        player1Str: str = self.player1['name']
        player2Str: str = self.player2['name']

        m = self.gameMatrix

        return f'**Four Wins:** Game - `{self.id}`\n' \
               f'Player 1  (`X`): {player1Str}\n' \
               f'Player 2 (`O`): {player2Str}\n' \
               f'```\n' \
               f'   1     2     3     4     5     6     7\n' \
               f'|  {m[0][0]}  |  {m[0][1]}  |  {m[0][2]}  |  {m[0][3]}  |  {m[0][4]}  |  {m[0][5]}  |  {m[0][6]}  |\n' \
               f'|-----|-----|-----|-----|-----|-----|-----|\n' \
               f'|  {m[1][0]}  |  {m[1][1]}  |  {m[1][2]}  |  {m[1][3]}  |  {m[1][4]}  |  {m[1][5]}  |  {m[1][6]}  |\n' \
               f'|-----|-----|-----|-----|-----|-----|-----|\n' \
               f'|  {m[2][0]}  |  {m[2][1]}  |  {m[2][2]}  |  {m[2][3]}  |  {m[2][4]}  |  {m[2][5]}  |  {m[2][6]}  |\n' \
               f'|-----|-----|-----|-----|-----|-----|-----|\n' \
               f'|  {m[3][0]}  |  {m[3][1]}  |  {m[3][2]}  |  {m[3][3]}  |  {m[3][4]}  |  {m[3][5]}  |  {m[3][6]}  |\n' \
               f'|-----|-----|-----|-----|-----|-----|-----|\n' \
               f'|  {m[4][0]}  |  {m[4][1]}  |  {m[4][2]}  |  {m[4][3]}  |  {m[4][4]}  |  {m[4][5]}  |  {m[4][6]}  |\n' \
               f'|-----|-----|-----|-----|-----|-----|-----|\n' \
               f'|  {m[5][0]}  |  {m[5][1]}  |  {m[5][2]}  |  {m[5][3]}  |  {m[5][4]}  |  {m[5][5]}  |  {m[5][6]}  |\n' \
               f'|#####|#####|#####|#####|#####|#####|#####|' \
               f'```\nEnd'
