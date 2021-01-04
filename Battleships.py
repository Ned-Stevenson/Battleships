from Ui import Gui, Terminal
from sys import argv
from database import initialiseDatabase, databasePath
from os.path import exists

def usage():   
    print(f"""
Usage: {argv[0]} - run in Terminal
{argv[0]} g - Run with the GUI""")

if __name__ == "__main__":
    if len(argv) != 2: #Ensures the program was called properly from the terminal with the file name and argument
        ui = Gui()
    elif argv[1] == "g":
        ui = Gui()
    else:
        usage()
        ui = Terminal()
    
    if not exists(databasePath):
        initialiseDatabase()
    ui.run()