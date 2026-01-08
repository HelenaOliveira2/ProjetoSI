class Position:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def setX(self, x:int):
        self.x = x

    def getY(self):
        return self.y

    def setY(self, y:int):
        self.y = y

    def toString(self):
        return "Position [X=" + str(self.x) + ", Y=" + str(self.y) + "]"