

class Grid:
    def __init__(self, width, height):
        self.__grid = [[None for _ in range(height)] for _ in range(width)]

    def __len__(self):
        return len(self.width)*len(self.height)

    def __getitem__(self, row):
        return self.__grid[row]
        # Returns the row. When grid[x][y] is called, getitem
        # is called with [x] and returns a list that is then indexed from [y]

    def expand(self, additionalColumns:int):
        for _ in range(additionalColumns):
            self.__grid.append([None for _ in range(self.height)])

    def extend(self, additionalRows:int):
        for column in self.__grid:
            for _ in range(additionalRows):
                column.append(None)

    @property
    def width(self):
        return len(self.__grid)

    @property
    def height(self):
        return len(self.__grid[0])


class Player:
    def __init__(self, name:str):
        self.__name = name


class Game:
    ship = "#"
    empty = " "
    hit = "x"
    miss = "~"
    dim = 8

    def __init__(self, player1:Player, player2:Player):
        self.__board = {
            player1:Grid(Game.dim, Game.dim),
            player2:Grid(Game.dim, Game.dim)}
        self.__currentPlayerTurn = player1
        self.__turnNumber = 1

    def placeShip(self, player:Player, ship:Ship, row:int, column:int, orientation):
        pass

    def fire(self, row:int, column:int):
        pass

    @property
    def winner(self):
        pass
