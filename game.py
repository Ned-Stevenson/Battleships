from enum import auto
from exceptions import ShotError, ShipPlacementError

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
        
class ShipPart(Ship):
    def __init__(self):
        self.__parentShip = None
        raise NotImplementedError

    def onHit(self):
        """Calls a function in the parent ship that tells it that it has been 
        hit, so that it can decrement it's remaining health and return if the ship has been sunk.
        returns False if the ship hit has not been sunk and a Ship object if it has been sunk"""
        return self.__parentShip.hit() # to do


class Game:
    dim = 8
    empty = None
    ship = auto()
    hit = auto()
    miss = auto()

    def __init__(self, player1Name, player2Name):
        self.__player1 = Player(player1Name)
        self.__player2 = Player(player2Name)
        # The board requires 4 seperate grids. A grid of ships and grid of shots for each player
        # A tuple is used with ships in position 0 and shots in position 1
        self.__board = {
            self.__player1:(Grid(Game.dim, Game.dim), Grid(Game.dim, Game.dim)),
            self.__player2:(Grid(Game.dim, Game.dim), Grid(Game.dim, Game.dim))}
        self.__currentPlayerTurn = self.__player1

    def placeShip(self, player:Player, ship:Ship, column:int, row:int, orientation):
        #Checking that the ship will remain within the bounds of the board
        # This will raise an AssertionError if the ship does not remain within the board
        if not self.IsValidPlacement(ship, row, column, orientation):
            raise ShipPlacementError
        # This board is the grid belonging to the relevant player tracking that player's ships
        board = self.__board[player][0]
        # Checking that the area that the ship will go in is empty
        # This check myst be done before the ship starts to be placed
        if orientation == vertical:
            for y in range(ship.width):
                for x in range(ship.length):
                    assert board[row+x][column+y] == None
        else:
            for x in range(ship.width):
                for y in range(ship.length):
                    assert board[row+x][column+y] == None

        # Placing the ship
        if orientation == vertical:
            for y in range(ship.width):
                for x in range(ship.length):
                    board[row+x][column+y] = Game.ship
        else:
            for x in range(ship.width):
                for y in range(ship.length):
                    board[row+x][column+y] = Game.ship

    def IsValidPlacement(self, ship, row, col, orientation):
        if orientation not in (horizontal, vertical):
            return False
        # Check the initial point is within the constrains of the board
        if not (0 <= row < Game.dim and 0 <= col < Game.dim):
            return False
        
        if orientation == vertical:
            if row + ship.length-1 < Game.dim and col + ship.width-1 < Game.dim:
                pass
            else:
                return False
        else:
            if col + ship.length-1 < Game.dim and row + ship.width-1 < Game.dim:
                pass
            else:
                return False
        return True

    def fire(self, column:int, row:int):
        assert 0 <= row < Game.dim and 0 <= column <Game.dim
        # The ship board is the map of enemy ships and the shot board is the current player's board
        # of shots It is needed to track the shots taken
        ShipBoard = self.__board[self.playerOpponent(self.__currentPlayerTurn)][0]
        ShotBoard = self.__board[self.__currentPlayerTurn][1]
        if ShipBoard[row][column] == Game.ship:
            ShotBoard[row][column] = Game.hit
            return True
        elif ShipBoard[row][column] == Game.empty:
            ShotBoard[row][column] = Game.miss
        else:
            return ShotError
            #This will be returned if the player fires at a square already fired at
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
        # Itterating through each board of ships and checking to see if any ships remain
        for player, playerBoard in self.__board.items():
            shipBoard = playerBoard[0]
            win = True
            for row in range(Game.dim):
                for col in range(Game.dim):
                    square = shipBoard[row][col]
                    if square == Game.ship:
                        if self.board[self.playerOpponent(player)][1][row][col] != Game.hit:
                            win = False
                if win == False:
                    break
                    # For each square on the board, if there is a ship, check if it is hit. If not, the player has not won
            if win == True:
                return self.playerOpponent(player)
        return None

SHIPS = [Ship("Carrier", 5, 1),
Ship("Battleship", 4, 1),
Ship("Crusier", 3, 1),
Ship("Submarine", 3, 1),
Ship("Destroyer", 2, 1)]