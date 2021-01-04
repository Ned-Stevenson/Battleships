from enum import auto
from exceptions import ShotError, ShipPlacementError
from itertools import product
from random import randrange

vertical = auto()
horizontal = auto()

class Array2d:
    def __init__(self, width:int, height:int):
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
        return self.__grid[row][col], (row, col)

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

class AI(Player):
    def __init__(self, name, board, game):
        super().__init__(name)
        self.__ships = list()
        self.__difficulty = None
        self.__probabilityMap = self.__generateProbabilityMap()
        self.__board = board
        self.__game = game
        self.__huntingHit = None

    def __generateProbabilityMap(self):
        probabilityMap = Array2d(Game.dim, Game.dim)
        for ship in self.__ships:
            for orientation in (horizontal, vertical):
                maxRow = Game.dim - ship.length if orientation == vertical else Game.dim - ship.width
                maxCol = Game.dim - ship.width if orientation == vertical else Game.dim - ship.length
                for row in range(maxRow):
                    for col in range(maxCol):
                        if self.__game.IsValidPlacement(self, ship, row, col, orientation):
                            for x, y in self.__game.coveredSquares(ship, row, col, orientation):
                                probabilityMap[x][y] += 1
        return probabilityMap
    
    def __regenerateProbabilityMapRowCol(self, row, col):
        pMap = self.__probabilityMap

        # Iterate over each candidate placement of each unsunk ship that may overlap with the target square 
        for ship in self.__ships:
            for shiftLength, shiftWidth in product(range(ship.length), range(ship.wigth)):
                if self.__game.IsValidPlacement(self, ship, row - shiftLength, col - shiftWidth, vertical):
                    if ship.wouldOverlap((row - shiftLength, col - shiftWidth), (row, col), vertical):
                        decrement = True
                        # Now, we must check that the placement being considered has not already been eliminated by another shot
                        # Therefore we should iterate over very square covered by the ship and see if there are any other shots that have already eliminated it
                        for shipPart, coords in ship:
                            x, y = coords
                            if shipPart != None and self.__game.board[self][Game.ShotBoard][x+row][y+col] != Game.empty:
                                decrement = False
                        if decrement:
                            for shipPart, coords in ship:
                                if shipPart != None:
                                    x, y = coords
                                    pMap[row+x][col+y] -= 1
                if self.__game.IsValidPlacement(self, ship, row - shiftWidth, col - shiftLength, horizontal):
                    if ship.wouldOverlap((row - shiftWidth, col - shiftLength), (row, col), horizontal):
                        decrement = True
                        # Now, we must check that the placement being considered has not already been eliminated by another shot
                        # Therefore we should iterate over very square covered by the ship and see if there are any other shots that have already eliminated it
                        for shipPart, coords in ship:
                            x, y = coords[::-1]
                            if shipPart != None and self.__game.board[self][Game.ShotBoard][row+x][col+y] != Game.empty:
                                decrement = False
                        if decrement:
                            for shipPart, coords in ship:
                                if shipPart != None:
                                    x, y = coords[::-1]
                                    pMap[row+x][col+y] -= 1

    def takeShot(self):
        if self.__huntingHit != None:
            shotToFire = self.__finishShip()
            if shotToFire == None:
                shotToFire = self.__searchForShips()
        else:
            shotToFire = self.__searchForShips
        hit = self.__game.fire(*shotToFire)
        
        if hit:
            self.__huntingHit = shotToFire
        else:
            self.__regenerateProbabilityMapRowCol(*shotToFire)

    def __searchForShips(self):
        MaxProb = 0
        for prob, coords in self.__probabilityMap:
            if prob > MaxProb:
                fireCoords = coords
                MaxProb = prob
        return fireCoords

    # Validation must be added here to check that the indexed coordinates remain within the constrain of the board
    def __finishShip(self):
        x, y = self.__huntingHit
        Board = self.__board[self][Game.ShipBoard]
        # x and y are the coordinates of the hit
        for row, col in product(range(-1, 2), repeat = 2):
            # ^ is a logical xor. This will mean it will only look in a plus pattern excluding the hit
            if bool(row) ^ bool(col):
                # This means that, in the direction looked from the hit, there is another hit. That direction should be extended
                if (0<=x+row<Game.dim and 0<=y+col<Game.dim) and Board[x+row][y+col] == Game.hit:
                    offset = 1
                    # This while loop extends the search in both directions in the orientation of the located hit until the end is found
                    # This end will be at either of the 2 below coordinates
                    while (0<=x+row*offset<Game.dim and 0<=y+col*offset<Game.dim) and (0<=x-row*offset<Game.dim and 0<=y-col*offset<Game.dim) and Board[x+row*offset][y+col*offset] == Game.hit and Board[x-row*offset][y-col*offset] == Game.hit:
                        offset += 1
                    # This means that if there is an unfired square at either end of the chain, it should be fired at
                    if (0<=x+row*offset<Game.dim and 0<=y+col*offset<Game.dim) and Board[x+row*offset][y+col*offset] == Game.empty:
                        return (x+row*offset, y+col*offset)
                    elif (0<=x-row*offset<Game.dim and 0<=y-col*offset<Game.dim) and Board[x-row*offset][y-col*offset] == Game.empty:
                        return (x-row*offset, y-col*offset)
                    # This means that the closer end of the hit chain to the tracked hit was not empty or it would have been returned above, and so must be a miss.
                    # Therefore, we should look for the other end of the chain and return that 
                    distanceToFirstHit = offset
                    if (0<=x+row*offset<Game.dim and 0<=y+col*offset<Game.dim) and Board[x+row*offset][y+col*offset] == Game.miss:
                        offset = -offset
                    while (0<=x+row*offset<Game.dim and 0<=y+col*offset<Game.dim) and Board[x+row*offset][y+col*offset] == Game.hit:
                        if offset < 0:
                            offset -= 1
                        else:
                            offset += 1
                    distanceToSecondHit = abs(offset)
                    # At this point, the other end of the chain of hits has been found
                    if (0<=x+row*offset<Game.dim and 0<=y+col*offset<Game.dim) and Board[x+row*offset][y+col*offset] == Game.empty:
                        return (x+row*offset, y+col*offset)
                        # If it's not been fired at, we should fire at that coordinate
                    else:
                        # If it is not empty, the ship is flanked on both ends and we can mark it as sunk and remove it from the list
                        # We should also rebuild the probability map at this point since we should stop considering the sunk ship
                        self.__huntingHit = None
                        shipLength = distanceToFirstHit + distanceToSecondHit - 1
                        for ship in self.__ships:
                            if ship.length == shipLength:
                                self.__ships.remove(ship)
                                break
                        self.__generateProbabilityMap()
                        return None
        # If there has not been a return by here, there is no other hit adjacent to the one we have found
        
        DistanceToShot = dict()
        for row, col in product(range(-1, 2), repeat = 2):
            # This is the logical xor, making it only search in a plus
            if bool(row) ^ bool(col):
                Offset = 1
                while (0<=x+row*Offset<Game.dim and 0<=y+col*Offset<Game.dim) and Board[x+row*Offset][y+col*Offset] == Game.empty:
                    Offset += 1
                DistanceToShot[(row, col)] = Offset
        
        # This searches in all 4 directions and returns the square one step in the direction with the greatest strech of empty tiles
        MaxDistance = 0
        for Direction, Distance in DistanceToShot.items():
            if Distance > MaxDistance:
                MaxDistance = Distance
                DirectionToFire = Direction
        deltaX, deltaY = DirectionToFire
        return (x+deltaX, y+deltaY)


    def placeShips(self):
        OrientationOptions = [horizontal, vertical]
        for ship in self.__ships:
            Orientation = OrientationOptions[randrange(0, len(OrientationOptions))]
            Placed = False
            while Placed == False:
                x = randrange(0, Game.dim)
                y = randrange(0, Game.dim)
                try:
                    self.__game.placeShip(self, ship, x, y, Orientation)
                    Placed = False
                except ShipPlacementError:
                    continue

class Ship:
    def __init__(self, name, length, width):
        self.__name = name
        self.__length = length
        self.__width = width
        self.__shape = Array2d(self.__length, self.__width)
        for row, col in product(range(self.__length), range(self.__width)):
            self.__shape[col][row] = ShipPart(self)

    def __str__(self):
        return f"""Name: {self.__name}
Length: {self.__length}
Width: {self.__width}"""

    def __iter__(self):
        self.__n = 0
        return self

    def __next__(self):
        if self.__n >= self.__length * self.__width:
            raise StopIteration
        col, row = divmod(self.__n, self.__length)
        self.__n += 1
        return self.__shape[row][col], (row, col)

    def wouldOverlap(self, placementCoords, overlapCoords, orientation) -> bool:
        placeRow, placeCol = placementCoords
        overlapRow, overlapCol = overlapCoords
        row = overlapRow - placeRow
        col = overlapCol - placeCol
        if 0 <= row <= self.__length and 0 <= col <= self.__width:
            return False if self.__shape[row][col] == None else True
        else:
            return False

    @property
    def name(self):
        return self.__name
    
    @property
    def width(self):
        return self.__width
    
    @property
    def length(self):
        return self.__length
    
    @property
    def shape(self):
        return self.__shape
        
class ShipPart(Ship):
    def __init__(self, parentShip):
        self.__parentShip = parentShip
        # raise NotImplementedError

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
    ShotBoard = auto()
    ShipBoard = auto()
    
    def __init__(self, player1Name, player2Name, player1AI = False, player2AI = False):
        # The board must be initialised and provided to the AI to create it and then the board must be populated
        # as it requires an instance of the AI to use as a key
        self.__board = dict()
        self.__player1 = AI(player1Name, self.__board, self) if player1AI else Player(player1Name)
        self.__player2 = AI(player2Name, self.__board, self) if player2AI else Player(player2Name)
        # The board requires 4 seperate grids. A grid of ships and grid of shots for each player
        self.__board[self.__player1] = {Game.ShotBoard:Array2d(Game.dim, Game.dim), Game.ShipBoard:Array2d(Game.dim, Game.dim)}
        self.__board[self.__player2] = {Game.ShotBoard:Array2d(Game.dim, Game.dim), Game.ShipBoard:Array2d(Game.dim, Game.dim)}
        self.__currentPlayerTurn = self.__player1
        self.__turnNumber = 0

    def placeShip(self, player:Player, ship:Ship, column:int, row:int, orientation):
        #Checking that the ship will remain within the bounds of the board
        # This will raise an AssertionError if the ship does not remain within the board
        if not self.IsValidPlacement(player, ship, row, column, orientation):
            raise ShipPlacementError
        # This board is the grid belonging to the relevant player tracking that player's ships
        board = self.__board[player][Game.ShipBoard]

        # Placing the ship
        if orientation == vertical:
            for y in range(ship.width):
                for x in range(ship.length):
                    board[row+x][column+y] = Game.ship
        else:
            for x in range(ship.width):
                for y in range(ship.length):
                    board[row+x][column+y] = Game.ship

    def IsValidPlacement(self, player, ship, row, col, orientation) -> bool:
        """Checks constraints of the board and existing ships to see if the parameters 
        would produce a valid ship position"""
        board = self.__board[player][Game.ShipBoard]
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

        # Checking that the area that the ship will go in is empty
        # This check myst be done before the ship starts to be placed
        shipNotOverlapping = True
        if orientation == vertical:
            for y in range(ship.width):
                for x in range(ship.length):
                    if board[row+x][col+y] != None:
                        shipNotOverlapping = False
        else:
            for x in range(ship.width):
                for y in range(ship.length):
                    if board[row+x][col+y] != None:
                        shipNotOverlapping = False
        return shipNotOverlapping

    def coveredSquares(self, ship, row, column, orientation):
        coveredSquares = []
        for shipRow, shipCol in product(range(ship.width), range(ship.length)):
            deltaR = shipRow if orientation == horizontal else shipCol
            deltaC = shipCol if orientation == horizontal else shipRow
            if ship.shape[shipRow][shipCol] != None:
                coveredSquares.append((row + deltaR, column + deltaC))
        return coveredSquares

    def fire(self, column:int, row:int):
        assert 0 <= row < Game.dim and 0 <= column <Game.dim
        # The ship board is the map of enemy ships and the shot board is the current player's board
        # of shots It is needed to track the shots taken
        ShipBoard = self.__board[self.playerOpponent(self.__currentPlayerTurn)][Game.ShipBoard]
        ShotBoard = self.__board[self.__currentPlayerTurn][Game.ShotBoard]
        if ShipBoard[row][column] == Game.ship:
            ShotBoard[row][column] = Game.hit
            return True
        elif ShipBoard[row][column] == Game.empty:
            ShotBoard[row][column] = Game.miss
        else:
            raise ShotError
            # This will be returned if the player fires at a square already fired at
        return False

    def playerOpponent(self, player:Player):
        if player == self.__player1:
            return self.__player2
        else:
            return self.__player1

    def changeTurn(self):
        self.__currentPlayerTurn = self.playerOpponent(self.__currentPlayerTurn)
        self.__turnNumber += 1

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
                        if self.board[self.playerOpponent(player)][Game.ShotBoard][row][col] != Game.hit:
                            win = False
                if win == False:
                    break
                    # For each square on the board, if there is a ship, check if it is hit. If not, the player has not won
            if win == True:
                return self.playerOpponent(player)
        return None
    
    @property
    def turnNumber(self):
        return self.__turnNumber
    
    @property
    def player1(self):
        return self.__player1

    @property
    def player2(self):
        return self.__player2

SHIPS = [Ship("Carrier", 5, 1),
Ship("Battleship", 4, 1),
Ship("Crusier", 3, 1),
Ship("Submarine", 3, 1),
Ship("Destroyer", 2, 1)]