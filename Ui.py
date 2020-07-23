from game import Game

class Terminal:
    def __init__(self):
        self.__ship = "#"
        self.__sea = "~"
        self.__hit = "X"
        self.__miss = "/"
        self.__game = Game()
    
    def run(self):
        while not self.__game.winner:
            print(self.__game)
            