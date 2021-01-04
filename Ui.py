from game import Game, SHIPS, vertical, horizontal ,Array2d
from exceptions import ShotError
from tkinter import Tk, Frame, Button, Grid, Label, Entry, Text, Scrollbar, Canvas, Checkbutton, StringVar, IntVar, N, S, E, W, X, Y, BOTH, TOP, BOTTOM, RIGHT, LEFT, DISABLED, NORMAL, SOLID, END, VERTICAL
from itertools import product
from enum import auto
from database import loginUserAccount, createUserAccount, listSaves, saveGame, loadGame
from sqlite3 import IntegrityError

class Ui:
    def __init__(self):
        self._ship = "#"
        self._sea = " "
        self._hit = "X"
        self._miss = "/"
        self._icons = {Game.empty: self._sea, Game.ship: self._ship,
        Game.hit: self._hit, Game.miss: self._miss}

class Gui(Ui): #To Do

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
        frame = Frame(root, bg = self._background)
        frame.pack(fill = BOTH, expand = True)
        # These buttons will be displayed on the main menu
        Button(frame, text = "Play Game", command = self.__playGameMenu, **self._defaultLayout).grid(row = 0, column = 0, sticky = N + S + E + W, padx = 30, pady = 20)
        Button(frame, text = "Settings", command = self.__settings, **self._defaultLayout).grid(row = 1, column = 0, sticky = N + S + E + W, padx = 30, pady = 20)
        Button(frame, text = "User stats", command = self.__userStats, **self._defaultLayout).grid(row = 2, column = 0, sticky = N + S + E + W, padx = 30, pady = 20)
        Button(frame, text = "Log in", command = self.__loginScreen, **self._defaultLayout).grid(row = 3, column = 0, sticky = N + S + E + W, padx = 30, pady = 20)
        Button(frame, text = "Exit", command = root.quit, **self._defaultLayout).grid(row = 4, column = 0, sticky = N + S + E + W, padx = 30, pady = 20)

        # Weighting the rows and columns to make all of the buttons on the screen of equal size
        frame.grid_columnconfigure(0, weight = 1)
        for i in range(5):
            frame.grid_rowconfigure(i, weight = 1)

        self._root = root
        self._mainMenu = frame
        self._currentFrame = frame

        self.__userID = None
    
    def run(self):
        self._root.mainloop()
    
    def __playGameMenu(self):
        # Unrender the previous frame and replace it with the game menu frame
        frame = Frame(self._root, bg = self._background)
        self.__transitionToScreen(frame)

        # Adding widgets to the frame using the grid placement
        player1Box = Entry(frame, font = self._defaultText)
        player1Box.insert(0, "Player 1")
        player1AIVar = IntVar()
        player1AI = Checkbutton(frame, text = "AI", variable = player1AIVar, **self._defaultLayout)
        player1AI.grid(row = 0, column = 1, sticky = N+S+E+W, padx = 50, pady = 50)
        player1Box.grid(row = 0, column = 0)

        player2Box = Entry(frame, font = self._defaultText)
        player2Box.insert(0, "Player 2")
        player2AIVar = IntVar()
        player2AI = Checkbutton(frame, text = "AI", variable = player2AIVar)
        player2AI.grid(row = 1, column = 1, sticky = N+S+E+W, padx = 50, pady = 50)
        player2Box.grid(row = 1, column = 0)
        # This lambda, when called, will simply apply the player names to the game GUI constructor
        startGame = lambda: self.__startGame(player1Box.get(), player2Box.get(), player1AIVar, player2AIVar)
        Button(frame, text = "Start game", command = startGame, **self._defaultLayout).grid(row = 0, column = 2, sticky = N+S+E+W)
        Button(frame, text = "Load game", command = self.__loadGameMenu, **self._defaultLayout).grid(row = 1, column = 2, sticky = N+S+E+W)
        Button(frame, text = "Return to main menu", command = self.__returnToMainMenu, **self._defaultLayout).grid(row = 2, column = 0, columnspan = 3, sticky = N+S+E+W)

        for i in range(3):
            frame.grid_rowconfigure(i, weight = 1)
        frame.grid_columnconfigure(0, weight = 3)
        frame.grid_columnconfigure(1, weight = 1)
        frame.grid_columnconfigure(1, weight = 2)

    def __startGame(self, player1Name, player2Name, player1AI, player2AI):
        game = Game(player1Name, player2Name, bool(player1AI), bool(player2AI))
        self.__game = game
        # Creating a frame for the whole window and placing a board frame within the larger frame
        frame = Frame(self._root, bg = self._background)
        frame.bind_all("r", self.__toggleOrientation)
        self.__mainGameFrame = frame

        self.__player1ID = None
        self.__player2ID = None
        self.__fleet1ID = None
        self.__fleet2ID = None

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
        self.__boardMode = Game.ShipBoard
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

        confirmShipPlacementButton = Button(shipIcons, command = self.__confirmShipPlacement, text = "Confirm ship placement", **self._defaultLayout)
        confirmShipPlacementButton.grid(row = len(SHIPS), column = 0, sticky = N+S+E+W)
        self.__bothPlayersPlacedShips = False

        self.__transitionToScreen(frame)

        Button(frame, **self._defaultLayout, text = "Return to main menu", command = self.__returnToMainMenu).grid(row = 1, column = 1, sticky = N+S+E+W, columnspan = 2)
        Button(frame, **self._defaultLayout, text = "Save Game", command = self.__saveGameCallback).grid(row = 2, column = 1, sticky = N+S+E+W, columnspan = 2)

    def __confirmShipPlacement(self):
        for shipIndex in range(len(SHIPS)):
            button = self.__shipIconsFrame.grid_slaves(row = shipIndex, column = 0)[0]
            if button.cget("state") != DISABLED:
                # self.__console.write("You need to place all your ships before continuing")
                return False
        if self.__bothPlayersPlacedShips == False:
            self.__bothPlayersPlacedShips = True
        else:
            self.__boardMode = Game.ShotBoard
            self.__gameFireColumn = self.__gameFireRow = None
            confirmShipPlacementButton = self.__shipIconsFrame.grid_slaves(row = len(SHIPS), column = 0)[0]
            cmd = lambda : self.__gameFireOnButtonSelect(self.__gameFireRow, self.__gameFireColumn)
            confirmShipPlacementButton.config(text = "Confirm shot placement", command = cmd)
        self.__game.changeTurn()
        self.__showHoldingScreen(self.__game.currentPlayerTurn)

    def __showHoldingScreen(self, newPlayer):
        holdingScreen = Frame(self._root, bg = self._background)
        nextPlayerMessage = Label(holdingScreen, **self._defaultLayout, text = f"{newPlayer.name}, it's your turn")
        cmd = lambda : self.__transitionToScreen(self.__mainGameFrame)
        continueButton = Button(holdingScreen, **self._defaultLayout, text = "Continue", command = cmd)
        nextPlayerMessage.grid(row = 0, column = 0, sticky = N+S+E+W)
        continueButton.grid(row = 1, column = 0, sticky = N+S+E+W, padx = 400, pady = 100)

        holdingScreen.grid_rowconfigure(0, weight = 5)
        holdingScreen.grid_rowconfigure(1, weight = 1)
        holdingScreen.grid_columnconfigure(0, weight = 1)

        # Reconfigure main game screen
        for row, col in product(range(Game.dim), range(Game.dim)):
            self.__buttons[row][col].set(self._icons[self.__game.board[newPlayer][self.__boardMode][row][col]])
        if self.__boardMode == Game.ShipBoard:
            for shipIndex in range(len(SHIPS)):
                shipButton = self.__shipIconsFrame.grid_slaves(row = shipIndex, column = 0)[0]
                shipButton.config(state = NORMAL, bg = "SystemButtonFace")
        
        self.__transitionToScreen(holdingScreen)

    def __transitionToScreen(self, newFrame):
        self._currentFrame.pack_forget()
        newFrame.pack(fill = BOTH, expand = True)
        self._currentFrame = newFrame

    def __boardButtonPress(self, row, col):
        if self.__boardMode == Game.ShipBoard:
            self.__placeShip(row, col)
        else:
            if self.__gameFireRow != None:
                previouslySelectedButton = self.__boardFrame.grid_slaves(row = self.__gameFireRow + 1, column = self.__gameFireColumn + 1)[0]
                previouslySelectedButton.config(fg = self._text)
                self.__buttons[self.__gameFireRow][self.__gameFireColumn].set(self._icons[self.__game.board[self.__game.currentPlayerTurn][Game.ShotBoard][row][col]])
            self.__buttons[row][col].set("O")
            selectedButton = self.__boardFrame.grid_slaves(row = row + 1, column = col + 1)[0]
            selectedButton.config(fg = "black")
            self.__gameFireRow = row
            self.__gameFireColumn = col

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
        # message = Label(self.__consoleFrame, bg = "white", fg = "green", text = m, anchor = W)
        # message.grid(column = 0, row = self.__consoleLabelCount, sticky = E+W)
        # self.__consoleLabelCount += 1

        self.__game.fire(col, row)
        self.__game.changeTurn()
        self.__showHoldingScreen(self.__game.currentPlayerTurn)

    def __settings(self): #To Do Change text colour and button colour
        message = "Sorry, settings are not yet available"
        frame = Frame(self._root)
        Label(frame, text = message, **self._defaultLayout).grid(row = 0, column = 0, sticky = N+S+E+W)
        Button(frame, text = "Return to main menu", command = self.__returnToMainMenu, **self._defaultLayout).grid(row = 1, column = 0, sticky = N+S+E+W)
        # This means that the row of the grid containing the text will always be 3 times larger than the row for the button
        frame.grid_rowconfigure(0, weight = 3)
        frame.grid_rowconfigure(1, weight = 1)
        frame.grid_columnconfigure(0, weight = 1)
        self.__transitionToScreen(frame)

    def __userStats(self): #To Do Change text colour and button colour
        message = "Sorry, user stats are not yet available"
        frame = Frame(self._root)
        Label(frame, text = message, **self._defaultLayout).grid(row = 0, column = 0, sticky = N+S+E+W)
        Button(frame, text = "Return to main menu", command = self.__returnToMainMenu, **self._defaultLayout).grid(row = 1, column = 0, sticky = N+S+E+W)
        # This means that the row of the grid containing the text will always be 3 times larger than the row for the button
        frame.grid_rowconfigure(0, weight = 3)
        frame.grid_rowconfigure(1, weight = 1)
        frame.grid_columnconfigure(0, weight = 1)
        self.__transitionToScreen(frame)

    def __loginScreen(self):
        frame = Frame(self._root, bg = self._background)
        usernameFrame = Frame(frame, bg = self._background)
        passwordFrame = Frame(frame, bg = self._background)
        username = Entry(usernameFrame, font = self._defaultText)
        password = Entry(passwordFrame, font = self._defaultText, show = "*")
        login = lambda : self.__loginCallback(username.get(), password.get())
        createAccount = lambda : self.__createAccountCallback(username.get(), password.get())
        loginButton = Button(frame, command = login, text = "Login", **self._defaultLayout)
        createAccountButton = Button(frame, text = "Create Account", command = createAccount, **self._defaultLayout)
        returnToMain = Button(frame, command = self.__returnToMainMenu, text = "Return to main menu", **self._defaultLayout)


        Label(usernameFrame, text = "Username", **self._defaultLayout, anchor = S+W).grid(row = 0, column = 0, sticky = N+S+E+W, padx = 50)
        username.grid(row = 1, column = 0, sticky = N+S+E+W, padx = 50)
        usernameFrame.grid_rowconfigure(0, weight = 1)
        usernameFrame.grid_rowconfigure(1, weight = 3)
        usernameFrame.grid_columnconfigure(0, weight = 1)

        Label(passwordFrame, text = "Password", **self._defaultLayout, anchor = W).grid(row = 0, column = 0, sticky = N+S+E+W, padx = 50)
        password.grid(row = 1, column = 0, sticky = N+S+E+W, padx = 50)
        passwordFrame.grid_rowconfigure(0, weight = 1)
        passwordFrame.grid_rowconfigure(1, weight = 3)
        passwordFrame.grid_columnconfigure(0, weight = 1)

        frame.columnconfigure(0, weight = 1)
        frame.columnconfigure(1, weight = 1)
        usernameFrame.grid(row = 1, column = 0, sticky = N+S+E+W, pady = 80, columnspan = 2)
        passwordFrame.grid(row = 2, column = 0, sticky = N+S+E+W, pady = 80, columnspan = 2)
        loginButton.grid(row = 3, column = 0, sticky = N+S+E+W, padx = 50, pady = 10)
        createAccountButton.grid(row = 3, column = 1, sticky = N+S+E+W, padx = 50, pady = 10)
        returnToMain.grid(row = 4, column = 0, sticky = N+S+E+W, padx = 50, pady = 10, columnspan = 2)

        for i in range(5):
            frame.grid_rowconfigure(i, weight = 1)
        self.__transitionToScreen(frame)

    def __loginCallback(self, username, password):
        if username and password:
            userID = loginUserAccount(username, password)
            frame = self._currentFrame
            if userID != None:
                self.__userID = userID
                feedbackMessage = f"Log in as {username} successful"
            else:
                feedbackMessage = f"Log in as {username} unsuccessful"
            Label(frame, text = feedbackMessage, **self._defaultLayout).grid(row = 0, column = 0, ipady = 10)

    def __createAccountCallback(self, username, password):
        """Attempts to create an account in the database"""
        if username and password:
            frame = self._currentFrame
            try:
                createUserAccount(username, password)
            except IntegrityError:
                feedbackMessage = f"Account creation for {username} failed. Account already exists"
            else:
                feedbackMessage = f"Account creation for {username} successful"
            Label(frame, text = feedbackMessage, **self._defaultLayout).grid(row = 0, column = 0, ipady = 10)

    def __loadGameMenu(self):
        frame = Frame(self._root, bg = self._background)
        saves = listSaves(self.__userID)
        commandTextList = []
        for saveID in saves:
            cmd = lambda : self.__loadGameCallback(saveID)
            commandTextList.append((cmd, f"Save ID: {saveID}"))
        scrollBox = VerticalScrolledFrame(frame, bg = "blue")
        for command, message in commandTextList:
            b = Button(scrollBox.interior, text = message, command = command, **self._defaultLayout)
            b.pack(anchor = N, fill = X, expand = True, pady = 5, padx = 10)
        scrollBox.grid(row = 0, column = 0, sticky = N+S+E+W, padx = 20, pady = 20)
        Button(frame, text = "Return to game menu", command = self.__playGameMenu, **self._defaultLayout).grid(row = 1, column = 0, padx = 50, pady = 30, sticky = N+S+E+W)

        frame.grid_columnconfigure(0, weight = 1)
        frame.grid_rowconfigure(0, weight = 4)
        frame.grid_rowconfigure(1, weight = 1)

        self.__transitionToScreen(frame)
    
    def __loadGameCallback(self, SaveID):
        player1, player2, fleet1, fleet2, turnNumber, gameBoard, gameDimentions = loadGame(SaveID)

    def __saveGameCallback(self):
        """Must collect data Player1, Player2, Fleet1, Fleet2, DateSaved, TurnNumber, GameBoard, BoardSize"""
        player1 = self.__player1ID
        player2 = self.__player2ID
        fleet1 = self.__fleet1ID
        fleet2 = self.__fleet2ID
        turnNumber = self.__game.turnNumber
        gameBoard = self.__game.board
        boardSize = Game.dim
        saveGame(player1, player2, fleet1, fleet2, turnNumber, gameBoard, boardSize)

        # Add to statistics

    def __returnToMainMenu(self):
        self.__transitionToScreen(self._mainMenu)


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

class Console(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(master, *args, **kwargs)
        kwargs["state"] = DISABLED
        kwargs["anchor"] = S
        self.__text = Text(master, *args, **kwargs)
        self.__text.pack(fill = BOTH, expand = True)

    def write(self, text:str):
        self.__text.config(state = NORMAL)
        self.__text.insert(END, text+"\n")
        self.__text.config(state = DISABLED)

# Taken from https://stackoverflow.com/questions/31762698/dynamic-button-with-scrollbar-in-tkinter-python
# to be used for a list of interactable options of unknown length, such as all available saved games
class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=False)
        canvas = Canvas(self, bd=0, highlightthickness=0, relief = SOLID,
                        yscrollcommand=vscrollbar.set, **kw)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        vscrollbar.config(command=canvas.yview)

        # reset the view to watch the whole canvas
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=N+W)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)