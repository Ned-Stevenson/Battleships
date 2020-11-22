from game import Player, Game, horizontal, vertical
from random import randrange
from exceptions import ShipPlacementError

class AI(Player):
    def __init__(self):
        self.Ships = None
        self.Difficulty = None
        raise NotImplementedError

    def takeShot(self):
        pass

# Validation must be added here to check that the indexed coordinates remain within the constrain of the board
    def __finishShip(self, hit:tuple):
        (x, y) = hit
        # x and y are the coordinates of the hit. The above syntax unpacks the tuple into the variables
        for row in range(-1, 2):
            for col in range(-1, 2):
                # ^ is a logical xor. This will mean it will only look in a plus pattern
                if bool(row) ^ bool(col):
                    if Board[x+row][y+col] == Game.hit:
                        offset = 1
                        # This while loop extends the search in both directions in the orientation of the located hit until the end is found
                        # This end will be at either of the 2 below coordinates
                        while Board[x+row*offset][y+row*offset] == Game.hit and Board[x-row*offset][y-row*offset] == Game.hit:
                            offset += 1
                        if Board[x+row*offset][y+col*offset] == Game.empty:
                            return (x+row*offset, y+col*offset)
                        elif Board[x-row*offset][y-col*offset] == Game.empty:
                            return (x-row*offset, y-col*offset)
                        if Board[x+row*offset][y+col*offset] == Game.miss:
                            offset = -offset
                        while Board[x+row*offset][y+col*offset] == Game.hit:
                            if offset < 0:
                                offset -= 1
                            else:
                                offset += 1
                        # At this point, the other end of the ship has been found
                        if Board[x+row*offset][y+col*offset] == Game.empty:
                            return (x+row*offset, y+col*offset)
                            # If it is empty, we should fire at that coordinate
                        else:
                            # If it is not empty, the suspected ship is flanked
                            # on both ends and we can mark it as sunk
                            # To do return the length of the ship that is sunk so that we can say that it is sunk rather than False
                            return False
        # If there has not been a return by here, there is no other hit adjacent to the one we have found
        Offset = 1
        DistanceToShot = {(1, 0): 0, (-1, 0): 0, (0, 1): 0, (0, -1): 0}
        Break = False
        while not Break:
            for row in range(-1, 2):
                for col in range(-1, 2):
                    # This is the logical xor, making it only search in a plus
                    if bool(row) ^ bool(col):
                        if Board[x+row*Offset][y+col*Offset] != Game.empty:
                            DistanceToShot[(row, col)] = Offset
            Break = True
            # This loop will make break False if there is still a direction that has not hit the end
            for Direction in DistanceToShot:
                if DistanceToShot[Direction]:
                    Break = False
        MaxDistance = 0
        for Direction, Distance in DistanceToShot.items():
            if Distance >= MaxDistance:
                MaxDistance = Distance
                DirectionToFire = Direction
        deltaX, deltaY = DirectionToFire
        return (x+deltaX, y+deltaY)


    def placeShips(self):
        OrientationOptions = [horizontal, vertical]
        for ship in self.Ships:
            Orientation = OrientationOptions[randrange(0, len(OrientationOptions))]
            Placed = False
            while Placed == False:
                x = randrange(0, Game.dim)
                y = randrange(0, Game.dim)
                try:
                    Game.placeShip(super(self), ship, x, y, Orientation)
                    Placed = False
                except ShipPlacementError:
                    continue