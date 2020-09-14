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
        self.__sea = " "
        self.__hit = "X"
        self.__miss = "/"
        self.__icons = {Game.empty: self.__sea, Game.ship: self.__ship,
        Game.hit: self.__hit, Game.miss: self.__miss}
        self.__game = Game(input("Input player 1 name: "), input("Input player 2 name: "))
    
    def printBoard(self, player, showShips = True):
        s = "  A B C D E F G H\n"
        h = "-"*(2*Game.dim+1)
        for row in range(Game.dim):
            r = f"{row+1}|"
            for col in range(Game.dim):
                iconToShow = self.__icons[self.__game.board[player][row][col]]
                if not showShips and iconToShow == self.__ship:
                    iconToShow = self.__sea
                r += iconToShow +"|"
            s += " " + h + "\n" + r + "\n"
        s += h
        print(s)

    def run(self):
        for player in self.__game.board:
            shipsToPlace = SHIPS[::]
            for ship in SHIPS:
                print(f"Ships left to be placed: {', '.join([ship.name for ship in shipsToPlace])}")
                self.printBoard(player)
                print(f"{player.name}, place your ships!")
                while True:
                    orientationString = input(f"Vertical or horizontal orientation for {ship.name}? v/h: ")
                    coords = input(f"Input the coordinates of the {ship.name} eg. B6: ")
                    x, y = ord(coords[0].upper())-65, int(coords[1])-1
                    if orientationString.lower() == "v":
                        orientation = vertical
                        break
                    elif orientationString.lower() == "h":
                        orientation = horizontal
                        break
                    else:
                        print("That was not a valid input")
                self.__game.placeShip(player, ship, x, y, orientation)
                shipsToPlace.remove(ship)
        
        while self.__game.winner == None:
            repeat = "n"
            print(f"{self.__game.currentPlayerTurn.name}, it's your turn to fire!")
            self.printBoard(self.__game.currentPlayerTurn, showShips = False)
            while repeat != "y":
                coords = input(f"Input the coordinates to fire at eg. B6: ")
                x, y = ord(coords[0].upper())-65, int(coords[1])-1
                repeat = input(f"Are you sure you want to fire at {coords.upper()}? y/n ").lower()
            if self.__game.fire(int(x), int(y)):
                print("Hit!")
            else:
                print("Miss")
            self.__game.changeTurn()
        print(f"{self.__game.playerOpponent(self.__game.currentPlayerTurn).name} is the winner!")
        print(f"{self.__game.winner}\'s board:")
        self.printBoard(self.__game.winner)
        print(f"{self.__game.playerOpponent(self.__game.winner)}\'s board:")
        self.printBoard(self.__game.playerOpponent(self.__game.winner))