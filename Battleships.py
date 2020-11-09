from Ui import Gui, Terminal
from sys import argv

def usage():   
    print(f"""
Usage: {argv[0]} - run in Terminal
{argv[0]} g - Run with the GUI""")

if __name__ == "__main__":
    if len(argv) != 2: #Ensures the program was called properly from the terminal with the file name and argument
        ui = Terminal()
    elif argv[1] == "g":
        ui = Gui()
    else:
        usage()
        ui = Terminal()
    
    ui.run()