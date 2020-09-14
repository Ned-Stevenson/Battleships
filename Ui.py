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
        self.__playerPasswords = {}
    
    def printBoard(self, player, showShips = True):
        s = "  A B C D E F G H\n"
        h = " " + "-"*(2*Game.dim+1)
        for row in range(Game.dim):
            r = f"{row+1}|"
            for col in range(Game.dim):
                iconToShow = self.__icons[self.__game.board[player][row][col]]
                if not showShips and iconToShow == self.__ship:
                    iconToShow = self.__sea
                r += iconToShow +"|"
            s += h + "\n" + r + "\n"
        s += h
        print(s)

    def run(self):
        for player in self.__game.board:
            password = input(f"{player.name}, input the password to view your ship deployment: ")
            self.__playerPasswords[player] = password
            shipsToPlace = SHIPS[::]
            for ship in SHIPS:
                print(f"Ships left to be placed: {', '.join([ship.name for ship in shipsToPlace])}")
                self.printBoard(player)

                validPlacement = False
                while validPlacement == False:
                    orientationString = input(f"Vertical or horizontal orientation for {ship.name}? v/h: ")
                    coords = input(f"Input the coordinates of the {ship.name} eg. B6: ")
                    x, y = ord(coords[0].upper())-65, int(coords[1])-1

                    if orientationString.lower() == "v":
                        orientation = vertical
                        validPlacement = True
                    elif orientationString.lower() == "h":
                        orientation = horizontal
                        validPlacement = True
                    else:
                        print("Invalid orientation")
                        continue
                    
                    try:
                        self.__game.placeShip(player, ship, x, y, orientation)
                    except AssertionError:
                        print("That was not a valid placement")
                        validPlacement = False
                
                shipsToPlace.remove(ship)
        
        while self.__game.winner == None:
            player = self.__game.currentPlayerTurn
            repeat = "y"
            print(f"{player.name}, it's your turn!")
            self.printBoard(player, showShips = False)

            while True:
                choise = self.turnMenu()
                if choise == 1:
                    while repeat != "y":
                        coords = input(f"Input the coordinates to fire at eg. B6: ")
                        x, y = ord(coords[0].upper())-65, int(coords[1])-1
                        repeat = input(f"Are you sure you want to fire at {coords.upper()}? y/n ").lower()
                    try:
                        if self.__game.fire(int(x), int(y)):
                            print("Hit!")
                        else:
                            print("Miss")
                    except AssertionError:
                        print("Invalid coordinates")
                        continue
                    self.__game.changeTurn()
                    break

                elif choise == 2:
                    password = input("Input your password: ")
                    if password == self.__playerPasswords[player]:
                        self.printBoard(player, showShips=True)
                    else:
                        print("That was the wrong password")
                
                elif choise == 3:
                    for ship in SHIPS:
                        print(str(ship)+"\n")

        print(f"{self.__game.playerOpponent(player).name} is the winner!")
        print(f"{self.__game.winner}\'s board:")
        self.printBoard(self.__game.winner)
        print(f"{self.__game.playerOpponent(self.__game.winner)}\'s board:")
        self.printBoard(self.__game.playerOpponent(self.__game.winner))

    def turnMenu(self):
        print("""Options:
        1) Fire
        2) View Ship Placement
        3) View Fleet Details""")
        while True:
            try:
                choise = int(input())
                break
            except ValueError:
                continue
        return choise