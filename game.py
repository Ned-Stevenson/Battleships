from enum import auto

vertical = auto()
horizontal = auto()

class Grid:
    def __init__(self, width, height):
        self.__grid = [[None for _ in range(width)] for _ in range(height)]

    def __len__(self):
        return self.width*self.height

    def __getitem__(self, row):
        return self.__grid[row]
        # Returns the row. When grid[x][y] is called, getitem
        # is called with [x] and returns a list that is then indexed from [y]
    
    def __iter__(self):
        self.__n = 0
        return self

    def __next__(self):
        if self.__n >= self.width * self.height:
            raise StopIteration
        col, row = divmod(self.__n, self.width)
        self.__n += 1
        return self.__grid[row][col]

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
    
    @property
    def name(self):
        return self.__name

class Ship:
    def __init__(self, name, length, width):
        self.__name = name
        self.__length = length
        self.__width = width
    
    def __str__(self):
        return f"""Name: {self.__name}
        Length: {self.__length}
        Width: {self.__width}"""

    @property
    def name(self):
        return self.__name
    
    @property
    def width(self):
        return self.__width
    
    @property
    def length(self):
        return self.__length
        

class Game:
    dim = 8
    empty = None
    ship = auto()
    hit = auto()
    miss = auto()

    def __init__(self, player1Name, player2Name):
        self.__player1 = Player(player1Name)
        self.__player2 = Player(player2Name)
        self.__board = {
            self.__player1:Grid(Game.dim, Game.dim),
            self.__player2:Grid(Game.dim, Game.dim)}
        self.__currentPlayerTurn = self.__player1

    def placeShip(self, player:Player, ship:Ship, column:int, row:int, orientation):
        assert orientation in (horizontal, vertical)
        assert 0 <= row < Game.dim and 0 <= column < Game.dim
        if orientation == vertical:
            assert row + ship.length-1 < Game.dim and column + ship.width-1 < Game.dim
        else:
            assert column + ship.length-1 < Game.dim and row + ship.width-1 < Game.dim
        board = self.__board[player]

        if orientation == vertical:
            for y in range(ship.width):
                for x in range(ship.length):
                    assert board[row+x][column+y] == None
        else:
            for x in range(ship.width):
                for y in range(ship.length):
                    assert board[row+x][column+y] == None

        if orientation == vertical:
            for y in range(ship.width):
                for x in range(ship.length):
                    board[row+x][column+y] = Game.ship
        else:
            for x in range(ship.width):
                for y in range(ship.length):
                    board[row+x][column+y] = Game.ship


    def fire(self, column:int, row:int):
        assert 0 <= row < Game.dim and 0 <= column <Game.dim
        board = self.__board[self.playerOpponent(self.__currentPlayerTurn)]
        if board[row][column] == Game.ship:
            board[row][column] = Game.hit
            return True
        else:
            board[row][column] = Game.miss
        return False

    def playerOpponent(self, player:Player):
        if player == self.__player1:
            return self.__player2
        else:
            return self.__player1

    def changeTurn(self):
        self.__currentPlayerTurn = self.playerOpponent(self.__currentPlayerTurn)

    @property
    def board(self):
        return self.__board

    @property
    def currentPlayerTurn(self):
        return self.__currentPlayerTurn

    @property
    def winner(self):
        for player, board in self.__board.items():
            win = True
            for square in board:
                if square == Game.ship:
                    win = False
            if win == True:
                return self.playerOpponent(player)
        return None

SHIPS = [Ship("Carrier", 5, 1),
Ship("Battleship", 4, 1),
Ship("Crusier", 3, 1),
Ship("Submarine", 3, 1),
Ship("Destroyer", 2, 1)]