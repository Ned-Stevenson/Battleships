from game import Game, SHIPS, vertical, horizontal

class Ui:
    def __init__(self):
        pass

class Gui(Ui):
    def __init__(self):
        raise NotImplementedError

class Terminal(Ui):
    def __init__(self):
        self.__ship = "#"
        self.__sea = "~"
        self.__hit = "X"
        self.__miss = "/"
        self.__game = Game(input("Input player 1 name: "), input("Input player 2 name: "))
    
    def printBoard(self, player):
        s = ""
        h = "-"*(2*Game.dim+1)
        for row in range(Game.dim):
            r = "|"
            for col in range(Game.dim):
                r += Game.icons[self.__game.board[player][row][col]]+"|"
            s += h + "\n" + r + "\n"
        s += h
        return s

    def run(self):
        for player in self.__game.board:
            for ship in SHIPS:
                self.printBoard(player)
                orientationString = input(f"Vertical or horizontal orientation for {ship.name}? v/h: ")
                x, y = input(f"Input the coordinates of the {ship.name} eg. 4,6: ").split(",")
                orientation = vertical if orientationString.lower() == "v" else horizontal
                self.__game.placeShip(player, ship, int(x), int(y), orientation)
        
        while not self.__game.winner:
            repeat = "n"
            while repeat != "y":
                x, y = input("Input the coordinates to fire at in the form x, y eg. 2,4: ").split(",")
                repeat = input("Are you sure you want to fire at {x},{y}? y/n ").lower()
            self.__game.fire(int(x), int(y))
            self.__game.changeTurn()
            self.printBoard(self.__game.currentPlayerTurn)