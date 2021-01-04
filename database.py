from sqlite3 import connect
from datetime import datetime

databasePath = "database.db"

def initialiseDatabase():
    conn = connect(databasePath)
    c = conn.cursor()
    tableCreateQueries = [
"""CREATE TABLE User (
    UserID INTEGER PRIMARY KEY,
    UserName TEXT UNIQUE,
    UserPassword TEXT
    );""",
"""CREATE TABLE Setting (
        SettingID INTEGER PRIMARY KEY,
        PresetName TEXT,
        UserID INTEGER,
        SoundEffectsVolume REAL,
        BackgroundMusicVolume REAL,
        MasterVolume REAL,
        FOREIGN KEY (UserID)
            REFERENCES User (UserID)
                ON DELETE CASCADE
                ON UPDATE NO ACTION
    );""",
"""CREATE TABLE Stat (
        UserID INTEGER PRIMARY KEY,
        GamesPlayed INTEGER DEFAULT 0,
        GamesWon INTEGER DEFAULT 0,
        ShotsTaken INTEGER DEFAULT 0,
        HitsMade INTEGER DEFAULT 0,
        ShipsSunk INTEGER DEFAULT 0,
        FOREIGN KEY (UserID)
            REFERENCES User (UserID)
                ON DELETE CASCADE
                ON UPDATE NO ACTION
    );""",
"""CREATE TABLE Save (
        SaveID INTEGER PRIMARY KEY,
        Player1 INTEGER,
        Player2 INTEGER,
        FleetPlayer1 INTEGER,
        FleetPlayer2 INTEGER,
        DateSaved DATE,
        TurnNumber INTEGER,
        GameBoard BLOB,
        BoardSize INTEGER,
        FOREIGN KEY (Player1, Player2)
            REFERENCES User (UserID, UserID)
                ON DELETE SET NULL
                ON UPDATE NO ACTION,
        FOREIGN KEY (FleetPlayer1, FleetPlayer2)
            REFERENCES Fleet (FleetID, FleetID)
                ON DELETE SET NULL
                ON UPDATE NO ACTION
    );""",
"""CREATE TABLE PowerUp (
        PowerUpID INTEGER PRIMARY KEY,
        PowerUpName TEXT
    );""",
"""CREATE TABLE PowerUp_Save (
        PowerUpID INTEGER,
        SaveID INTEGER,
        PRIMARY KEY (PowerUpID, SaveID),
        FOREIGN KEY (PowerUpID)
            REFERENCES PowerUp (PowerUpID)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
        FOREIGN KEY (SaveID)
            REFERENCES Save (SaveID)
                ON DELETE CASCADE
                ON UPDATE NO ACTION
    );""",
"""CREATE TABLE Fleet (
        FleetName TEXT,
        FleetID INTEGER PRIMARY KEY
    );""",
"""CREATE TABLE Ship (
        ShipID INTEGER PRIMARY KEY,
        ShipName TEXT,
        ShipShape BLOB
    );""",
"""CREATE TABLE Ship_Fleet (
        ShipID INTEGER,
        FleetID INTEGER,
        PRIMARY KEY (ShipID, FleetID),
        FOREIGN KEY (ShipID)
            REFERENCES Ship (ShipID)
                ON DELETE SET NULL
                ON UPDATE NO ACTION,
        FOREIGN KEY (FleetID)
            REFERENCES Fleet (FleetID)
                ON DELETE SET NULL
                ON UPDATE NO ACTION
    );"""]
    for query in tableCreateQueries:
        print(query)
        c.execute(query)
    conn.commit()
    conn.close()

def saveGame(player1, player2, fleet1, fleet2, turnNumber, GameBoard, boardSize):
    saveGameData = (player1, player2, fleet1, fleet2, datetime.now(), turnNumber, GameBoard, boardSize)
    powerUpIDs = tuple()
    saveID = None
    # To do
    conn = connect(databasePath)
    c = conn.cursor()
    c.execute("""INSERT INTO Save
    (Player1, Player2, FleetPlayer1, FleetPlayer2, DateSaved, TurnNumber, GameBoard, BoardSize)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, saveGameData)
    c.executemany("""INSERT INTO PowerUp-Save 
    (PowerUpID, SaveID)
    VALUES (?, ?);""", [(powerUpID, saveID) for powerUpID in powerUpIDs])
    conn.commit()
    conn.close()

def loadGame(SaveID) -> tuple:
    """Takes in a SaveID as int
    returns: Tuple
    Player1, Player2, FleetPlayer1, FleetPlayer2, TurnNumber, GameBoard, BoardSize"""
    conn = connect(databasePath)
    c = conn.cursor()
    c.execute("""SELECT Player1, Player2, FleetPlayer1, FleetPlayer2, TurnNumber, GameBoard, BoardSize FROM Save
    WHERE SaveID = ?;""", SaveID)
    fields = c.fetchone()
    c.execute("""SELECT PowerUpID, PowerUpName FROM 
    ((PowerUp_Save INNERJOIN Save
    ON Save.SaveID = PowerUp_Save.SaveID
    )INNERJOIN PowerUp
    ON PowerUp_Save.PowerUpID = PowerUp.PowerUpID)
    WHERE Save.SaveID = ?;""", (SaveID,))
    PowerUps = c.fetchall()
    conn.close()
    return fields, PowerUps

def loginUserAccount(userName, password) -> (int, None):
    """Searches for user in users table. Returns UserID if a valid login or None if invalid"""
    conn = connect(databasePath)
    c = conn.cursor()
    vars = (userName, password,)
    c.execute("""SELECT UserID FROM User
    WHERE UserName = ? AND UserPassword = ?""", vars)
    UserID = c.fetchone()
    conn.close()
    return UserID[0] if UserID != None else None

def createUserAccount(userName, password):
    """Creates row in users table with userName and password"""
    # To do add stats record at the same time as the Users record
    conn = connect(databasePath)
    c = conn.cursor()
    c.execute("""INSERT INTO User
    (UserName, UserPassword) 
    VALUES (?, ?);""", (userName, password))
    conn.commit()
    conn.close()

def getShipsInFleet(fleetID):
    conn = connect(databasePath)
    c = conn.cursor()
    c.execute("""SELECT ShipID FROM 
    Fleet INNERJOIN Fleet-Ship ON
    Fleet.FleetID = Fleet-Ship.FleetID
    WHERE FleetID = ?""", (fleetID,))
    shipIDs = c.fetchall()
    conn.close()
    return shipIDs

def getShapeOfShip(shipID):
    conn = connect(databasePath)
    c = conn.cursor()
    c.execute("""SELECT ShipShape FROM Ship
    WHERE ShipID = ?""", (shipID,))
    shipShape = c.fetchone()
    conn.close()
    return shipShape

def updateStats(UserID, GamesPlayed, GamesWon, ShotsTaken, HitsMade, ShipsSunk):
    conn = connect(databasePath)
    c = conn.cursor()
    c.execute("""UPDATE Stat SET
    GamesPlayed = GamesPlayed + ?,
    GamesWon = GamesWon + ?,
    ShotsTaken = ShotsTaken + ?,
    HitsMade = HitsMade + ?,
    ShipsSunk = ShipsSunk + ?
    WHERE UserID = ?""", (GamesPlayed, GamesWon, ShotsTaken, HitsMade, ShipsSunk, UserID))
    conn.commit()
    conn.close()

def listSaves(UserID):
    conn = connect(databasePath)
    c = conn.cursor()
    c.execute("""SELECT SaveID FROM Save
    WHERE Player1 =:userID OR Player2=:userID;""", {"userID": UserID})
    saves = c.fetchall()
    conn.close()
    return saves

def getSaveInfo(SaveID):
    conn = connect(databasePath)
    c = conn.cursor()
    c.execute("""SELECT * FROM Save
    WHERE SaveID = ?;""", (SaveID,))
    row = c.fetchone()
    conn.close()
    return row