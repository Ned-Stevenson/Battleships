from game import Game, SHIPS, vertical, horizontal ,Array2d
from exceptions import ShotError
from tkinter import Tk, Frame, Button, Grid, Label, Entry, Text, StringVar, N, S, E, W, X, Y, BOTH, TOP, BOTTOM, DISABLED, SOLID
from itertools import product
from enum import auto

class Ui:
    def __init__(self):
        self._ship = "#"
        self._sea = " "
        self._hit = "X"
        self._miss = "/"
        self._icons = {Game.empty: self._sea, Game.ship: self._ship,
        Game.hit: self._hit, Game.miss: self._miss}

class Gui(Ui): #To Do

    shipPlacement = auto()
    shotsBeingTaken = auto()

    def __init__(self):
        super(Gui, self).__init__()
        self._defaultText = ("Consolas", 20)
        self._background = "navy"
        self._text = "white"
        self._defaultLayout = {"bg":self._background, "fg": self._text, "font":("Consolas", 20)}
        #Preparing the window and the main menu frame
        root = Tk()
        root.overrideredirect(True) # Makes the application borderless
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        root.title("Battleships")
        frame = Frame(root)
        frame.pack(fill = BOTH, expand = True)
        # These buttons will be displayed on the main menu
        Button(frame, text = "Play Game", command = self.__playGameMenu, **self._defaultLayout).grid(row = 0, column = 0, sticky = N + S + E + W)
        Button(frame, text = "Settings", command = self.__settings, **self._defaultLayout).grid(row = 1, column = 0, sticky = N + S + E + W)
        Button(frame, text = "User stats", command = self.__userStats, **self._defaultLayout).grid(row = 2, column = 0, sticky = N + S + E + W)
        Button(frame, text = "Exit", command = root.quit, **self._defaultLayout).grid(row = 3, column = 0, sticky = N + S + E + W)

        # Weighting the rows and columns to make all of the buttons on the screen of equal size
        frame.grid_columnconfigure(0, weight = 1)
        for i in range(4):
            frame.grid_rowconfigure(i, weight = 1)

        self._root = root
        self._mainMenu = frame
        self._currentFrame = frame
    
    def run(self):
        self._root.mainloop()
    
    def __playGameMenu(self):
        # Unrender the previous frame and replace it with the game menu frame
        self._mainMenu.pack_forget()
        frame = Frame(self._root, bg = self._background)
        frame.pack(fill = BOTH, expand = True)
        self._currentFrame = frame

        # Adding widgets to the frame using the grid placement
        player1Box = Entry(frame, font = self._defaultText)
        player1Box.insert(0, "Player 1")
        player2Box = Entry(frame, font = self._defaultText)
        player2Box.insert(0, "Player 2")
        player1Box.grid(row = 0, column = 0)
        player2Box.grid(row = 1, column = 0)
        # This lambda, when called, will simply apply the player names to the game GUI constructor
        startGame = lambda: self.__startGame(player1Box.get(), player2Box.get())
        Button(frame, text = "Start game", command = startGame, **self._defaultLayout).grid(row = 0, column = 1, rowspan = 2, sticky = N+S+E+W)
        Button(frame, text = "Return to main menu", command = self.__returnToMainMenu, **self._defaultLayout).grid(row = 2, column = 0, columnspan = 2, sticky = N+S+E+W)

        for i in range(3):
            frame.grid_rowconfigure(i, weight = 1)
        frame.grid_columnconfigure(0, weight = 2)
        frame.grid_columnconfigure(1, weight = 1)

    def __startGame(self, player1Name, player2Name):
        game = Game(player1Name, player2Name)
        self.__game = game
        # Creating a frame for the whole window and placing a board frame within the larger frame
        self._currentFrame.pack_forget()
        frame = Frame(self._root, bg = self._background)
        frame.bind_all("r", self.__toggleOrientation)

        board = Frame(frame, bg = self._background)
        board.grid(row = 0, column = 0, sticky = N+S+E+W, rowspan = 3)
        self.__boardFrame = board
        
        frame.grid_rowconfigure(0, weight = 2)
        frame.grid_columnconfigure(0, weight = 4)
        frame.grid_columnconfigure(1, weight = 1)
        frame.grid_columnconfigure(2, weight = 1)

        # Creating the tiling of buttons as well as the row and column labels
        self.__buttons = Array2d(Game.dim, Game.dim)
        for row, col in product(range(Game.dim+1), range(Game.dim+1)):
            if row == 0:
                if col == 0:
                    # Ensuring nothing unexpected is placed in the top left corner
                    continue
                else:
                    Label(board, text = chr(col+64), **self._defaultLayout).grid(row = row, column = col, sticky = N+S+E+W)
            elif col == 0:
                Label(board, text = str(row), **self._defaultLayout).grid(row = row, column = col, sticky = N+S+E+W)
            else:
                row -= 1
                col -= 1
                # To do Create a function or lambda to be called when the button is pressed
                b = StringVar()
                b.set(self._icons[game.board[game.currentPlayerTurn][Game.ShotBoard][row][col]])
                # Get the shot status of the location and player in question and look up the character to represent it
                press = lambda r=row,c=col : self.__boardButtonPress(r, c)
                hover = lambda event, r=row, c=col : self.__hoverOverSquare(r, c)
                unhover = lambda event, r=row, c=col : self.__removeShipShadow(r, c)
                
                button = Button(
                    board,
                    textvariable = b,
                    command = press,
                    **self._defaultLayout
                )
                button.grid(row = row+1, column = col+1, sticky = N+S+E+W)
                button.bind("<Enter>", hover)
                button.bind("<Leave>", unhover)
                self.__buttons[row][col] = b

        # Ensuring all the tiles in the grid are square
        for row in range(Game.dim+1):
            board.grid_rowconfigure(row, weight = 1)
        for col in range(Game.dim+1):
            board.grid_columnconfigure(col, weight = 1)

        # The console will be a list of events like a computer console that will remind the player what has happened
        # It will be a frame with Labels packed onto the frame after each event
        console = Frame(frame, bg = "black")
        console.grid(row = 0, column = 1, sticky = N+S+E+W)
        console.grid_columnconfigure(0, weight = 1)
        self.__consoleFrame = console
        self.__consoleLabelCount = 0
        # To Do Implement adding messages to the console when an event occurs

        self.__shipPlacementOrientation = horizontal
        self.__boardMode = Gui.shipPlacement
        self.__selectedShip = None

        shipIcons = Frame(frame, bg = self._background)
        shipIcons.grid(row = 0, column = 2, sticky = N+S+E+W)
        shipIcons.grid_columnconfigure(0, weight = 1)
        self.__shipIconsFrame = shipIcons

        for index, ship in enumerate(SHIPS):
            cmd = lambda s=ship, i=index: self.__setSelectedShip(s, i)
            shipText = ship.name.upper() + "\n\n" + "\n".join([self._ship * ship.length for _ in range(ship.width)])
            shipButton = Button(shipIcons, fg = "gray20", text = shipText, font = ("Inconsolata", 20), borderwidth = 2, relief = SOLID, command = cmd)
            shipButton.grid(row = index, column = 0, sticky = N+S+E+W)
            shipIcons.grid_rowconfigure(index, weight = 1)

        frame.pack(fill = BOTH, expand = True)
        self._currentFrame = frame

        Button(frame, **self._defaultLayout, command = self.__returnToMainMenu, text = "Return to main menu").grid(row = 1, column = 1, sticky = N+S+E+W, columnspan = 2)
        Button(frame, **self._defaultLayout, text = "Save Game").grid(row = 2, column = 1, sticky = N+S+E+W, columnspan = 2)

    def __boardButtonPress(self, row, col):
        if self.__boardMode == Gui.shipPlacement:
            self.__placeShip(row, col)

    def __setSelectedShip(self, ship, shipIndex):
        for i in range(len(SHIPS)):
            shipButton = self.__shipIconsFrame.grid_slaves(row = i, column = 0)[0]
            if shipButton.cget("state") != DISABLED:
                shipButton.config(bg = "SystemButtonFace")
        self.__selectedShip = ship
        shipButton = self.__shipIconsFrame.grid_slaves(row = shipIndex, column = 0)[0]
        shipButton.config(bg = "gray")

    def __toggleOrientation(self, *args):
        self.__removeShipShadow(self.__hoverRow, self.__hoverColumn, orientation=self.__shipPlacementOrientation)
        self.__shipPlacementOrientation = vertical if self.__shipPlacementOrientation == horizontal else horizontal
        self.__createShipShadow(self.__hoverRow, self.__hoverColumn)

    def __hoverOverSquare(self, row, col):
        if self.__selectedShip != None:
            self.__hoverRow = row
            self.__hoverColumn = col
            self.__createShipShadow(row, col)

    def __placeShip(self, row, column):
        if self.__selectedShip != None:
            self.__game.placeShip(self.__game.currentPlayerTurn, self.__selectedShip, column, row, self.__shipPlacementOrientation)
            shipIndex = SHIPS.index(self.__selectedShip)
            shipSelectionButton = self.__shipIconsFrame.grid_slaves(shipIndex, 0)[0]
            shipSelectionButton.config(state = DISABLED, bg = "gray20")
            self.__selectedShip = None

    def __createShipShadow(self, row, column):
        if self.__game.IsValidPlacement(self.__game.currentPlayerTurn, self.__selectedShip, row, column, self.__shipPlacementOrientation):
            newColour = "gray"
        else:
            newColour = "red"
        for square in self.__game.coveredSquares(self.__selectedShip, row, column, self.__shipPlacementOrientation):
            r, c = square
            if 0 <= r < Game.dim and 0 <= c < Game.dim:
                self.__buttons[r][c].set(self._ship)
                button = self.__boardFrame.grid_slaves(row = r+1, column = c+1)[0]
                button.config(fg = newColour)

    def __removeShipShadow(self, row, column, orientation=None):
        if self.__selectedShip != None:
            if orientation == None:
                orientation = self.__shipPlacementOrientation
            for square in self.__game.coveredSquares(self.__selectedShip, row, column, orientation):
                r, c = square
                if 0 <= r < Game.dim and 0 <= c < Game.dim:
                    self.__buttons[r][c].set(self._icons[self.__game.board[self.__game.currentPlayerTurn][Game.ShipBoard][r][c]])
                    button = self.__boardFrame.grid_slaves(row = r+1, column = c+1)[0]
                    button.config(fg = "gray")

    def __gameFireOnButtonSelect(self, row, col):
        #To do. Finish implementation of console
        m = f"Shot taken by {self.__game.currentPlayerTurn.name} at {row}, {col}"
        print(m)
        message = Label(self.__consoleFrame, bg = "white", fg = "green", text = m, anchor = W)
        message.grid(column = 0, row = self.__consoleLabelCount, sticky = E+W)
        self.__consoleLabelCount += 1

        self.__game.fire(col, row)
        self.__game.changeTurn()

    def __settings(self): #To Do Change text colour and button colour
        # This removes the main menu from the root window
        self._mainMenu.pack_forget()
        # Preparing and adding the frame to the screen
        message = "Sorry, settings are not yet available"
        frame = Frame(self._root)
        frame.pack(fill = BOTH, expand = True)
        Label(frame, text = message, **self._defaultLayout).grid(row = 0, column = 0, sticky = N+S+E+W)
        Button(frame, text = "Return to main menu", command = self.__returnToMainMenu, **self._defaultLayout).grid(row = 1, column = 0, sticky = N+S+E+W)
        # This means that the row of the grid containing the text will always be 3 times larger than the row for the button
        frame.grid_rowconfigure(0, weight = 3)
        frame.grid_rowconfigure(1, weight = 1)
        frame.grid_columnconfigure(0, weight = 1)
        self._currentFrame = frame

    def __userStats(self): #To Do Change text colour and button colour
        # This removes the main menu from the root window
        self._mainMenu.pack_forget()
        # Preparing and adding the frame to the screen
        message = "Sorry, user stats are not yet available"
        frame = Frame(self._root)
        frame.pack(fill = BOTH, expand = True)
        Label(frame, text = message, **self._defaultLayout).grid(row = 0, column = 0, sticky = N+S+E+W)
        Button(frame, text = "Return to main menu", command = self.__returnToMainMenu, **self._defaultLayout).grid(row = 1, column = 0, sticky = N+S+E+W)
        # This means that the row of the grid containing the text will always be 3 times larger than the row for the button
        frame.grid_rowconfigure(0, weight = 3)
        frame.grid_rowconfigure(1, weight = 1)
        frame.grid_columnconfigure(0, weight = 1)
        self._currentFrame = frame
    
    def __returnToMainMenu(self):
        self._currentFrame.pack_forget()
        self._mainMenu.pack(fill = BOTH, expand = True)


class Terminal(Ui):
    def __init__(self):
        super(Terminal, self).__init__()
        self.__game = Game(input("Input player 1 name: "), input("Input player 2 name: "))
        self.__playerPasswords = {}
    
    def printBoard(self, player, showShips = False):
        s = "  A B C D E F G H\n"
        h = " " + "-"*(2*Game.dim+1)
        boardIndex = Game.ShipBoard if showShips else Game.ShotBoard
        Board = self.__game.board[player][boardIndex]
        # Produce a representation of each row in board using a lookup dictionary
        for row in range(Game.dim):
            r = f"{row+1}|"
            for col in range(Game.dim):
                iconToShow = self._icons[Board[row][col]]
                r += iconToShow +"|"
            s += h + "\n" + r + "\n"
        s += h
        print(s)

    def run(self):
        for player in self.__game.board:
            password = input(f"{player.name}, input the password to view your ship deployment: ")
            self.__playerPasswords[player] = password
            # Copy of the ships required to prevent issues caused by reference list assignment and itteration
            shipsToPlace = SHIPS[::]
            for ship in SHIPS:
                print(f"Ships left to be placed: {', '.join([ship.name for ship in shipsToPlace])}")
                self.printBoard(player, showShips = True)

                validPlacement = False
                # Placement validation
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
                
                # Remove the ship just placed from the list of remaining ships
                shipsToPlace.remove(ship)
        
        while self.__game.winner == None:
            player = self.__game.currentPlayerTurn
            repeat = "n"
            print(f"{player.name}, it's your turn!")
            self.printBoard(player, showShips = False)

            while True:
                choise = self.turnMenu()
                if choise not in ("2", "3"):
                    while repeat != "y":
                        if choise == "1":
                            fireCoords = input("Input the coordinates to fire at eg. B6: ")
                        else:
                            fireCoords = choise
                        x, y = ord(fireCoords[0].upper())-65, int(fireCoords[1])-1
                        repeat = input(f"Are you sure you want to fire at {fireCoords.upper()}? y/n ").lower()

                    try:
                        if self.__game.fire(int(x), int(y)):
                            print("Hit!")
                        else:
                            print("Miss")
                    except (AssertionError, ShotError) as e:
                        if e == AssertionError:
                            print("Invalid coordinates")
                        else:
                            print(f"You have already fired at {fireCoords}. Please select another locations to fire at")
                        choise = "1" # Causes the game to prompt for a new coordinate to fire at
                        continue
                    self.__game.changeTurn()
                    break

                elif choise == "2":
                    password = input("Input your password: ")
                    if password == self.__playerPasswords[player]:
                        self.printBoard(player, showShips=True)
                    else:
                        print("That was the wrong password")
                
                elif choise == "3":
                    for ship in SHIPS:
                        print(str(ship)+"\n")
        winner = self.__game.winner
        print(f"{winner.name} is the winner!")
        print(f"{winner.name}\'s board:")
        self.printBoard(self.__game.winner, showShips = True)
        print(f"{self.__game.playerOpponent(winner).name}\'s board:")
        self.printBoard(self.__game.playerOpponent(self.__game.winner), showShips = True)

    def turnMenu(self):
        print("""Options:
        1) Fire
        2) View Ship Placement
        3) View Fleet Details
        
        Or input coordinates to fire at those coordinates""")
        return input()