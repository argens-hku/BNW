policyNN = "PolicyNetwork/policy_network.h5"
valueNN = "ValueNetwork/value_network2.h5"
size = 8

#  --------------- Non-program Specific ----------------  #

def clearScreen ():
	print ("\033c")

def query (question = "", choices = []):

	if len (choices) == 0:
		clearScreen ()
		question = question +"\n\n"
		answer = input (question)
		
	else:
		for i in range (len (choices)):
			question = question + "\n"
			question = question + str(i) + ") "
			question = question + choices [i]
		question = question + "\n\n"

		answer = len (choices)

		while answer >= len (choices):
			clearScreen ()
			try:
				answer = int (input (question))
			except ValueError:
				answer = len (choices)

	return answer

#  --------------- Program Specific ----------------  #

from pathlib import Path
import numpy as np

def getNetworks ():

    global policyNN
    global valueNN

    q = "Which policy network would you like to use?"
    file = Path (policyNN)
    while not file.is_file():
        policyNN = "PolicyNetwork/" + query (question = q)
        file = Path (policyNN)

    q = "Which value network would you like to use?"
    file = Path (valueNN)
    while not file.is_file():
        valueNN = "ValueNetwork/" + query (question = q)
        file = Path (valueNN)

    return (policyNN, valueNN)

def convertToNN (line):
    board = []
    white = []
    black = []
    empty = []
    border = []
    for i in range (size):
        row_white = []
        row_black = []
        row_empty = []
        row_border = []
        for j in range (size):
            if i == 0 or j == 0 or i == size-1 or j == size-1:
                row_border.append (1)
            else:
                row_border.append (0)
            piece = line [i][j]
            if piece == -1:
                row_empty.append (1)
                row_black.append (0)
                row_white.append (0)
            else:
                if piece == 1:
                    row_empty.append (0)
                    row_black.append (1)
                    row_white.append (0)
                else:
                    row_empty.append (0)
                    row_black.append (0)
                    row_white.append (1)

        empty.append (row_empty)
        white.append (row_white)
        black.append (row_black)
        border.append (row_border)

    e = np.asarray (empty)
    w = np.asarray (white)
    bl = np.asarray (black)
    bd = np.asarray (border)

    board.append (e)
    board.append (w)
    board.append (bl)
    board.append (bd)

    # print ("e", e.shape)
    # print ("w", w.shape)
    # print ("bl", bl.shape)

    # b = np.asarray (board)
    # print ("b.shape", b.shape)
    return board
#  --------------- Definition -----------------  #

from enum import Enum

class Piece:

    def __init__(self, c):
        self.color = c

class Color (Enum):

    black = 0
    white = 1
    neither = 2

    def swap (self):
        if self.value == 0:
            return Color.white
        if self.value == 1:
            return Color.black
        return self

#  --------------- Borrowed Segment -----------------  #

import sys
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QFrame, QApplication
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPainter, QColor 

class AbstractBoard ():

    pieces = []
    possibleMoves = []
    nextStates = []
    score = 0
    displayBoard = None

    # @classmethod
    # def placeHolder (self):
    #     pieces = []

    def __init__ (self, size, c):
        for j in range (size):
            row = []
            for i in range (size):

                if i == size / 2 - 1:
                    if j == size / 2 - 1:
                        row.append (Piece(Color.white))
                        continue
                    if j == size / 2:
                        row.append (Piece(Color.black))
                        continue
                
                if i == size / 2:
                    if j == size / 2 - 1:
                        row.append (Piece(Color.black))
                        continue
                    if j == size / 2:
                        row.append (Piece(Color.white))
                        continue

                row.append (Piece(Color.neither))
            self.pieces.append (row)
        self.size = size
        self.player = c
        self.computer = Computer ()
        self.findPositions ()

    def setDisplayBoard (self, db):
        self.displayBoard = db

#    def __init__ (self, displayBoard, prevBoard, move);

    def tryMove (self, x, y):

        (hasMove, converts) = self.checkValidMove (x, y, self.player)
        #print (converts)

        if hasMove:
            self.makeMove (x, y, converts)
        else:
            self.sendStatus ("Invalid Move!")

    def checkValidMove (self, x, y, color):
        
        valid = []
        if x < 0 or y < 0 or x >= self.size or y >= self.size or self.pieces [x][y].color != Color.neither:
            return (False, [])
        
        if color != Color.neither:

            # In the clockwise direction, starting from direct left
            valid.append (self.checkOneDirection (x, y, color, -1, 0))
            valid.append (self.checkOneDirection (x, y, color, -1, -1))
            valid.append (self.checkOneDirection (x, y, color, 0, -1))
            valid.append (self.checkOneDirection (x, y, color, 1, -1))
            valid.append (self.checkOneDirection (x, y, color, 1, 0))
            valid.append (self.checkOneDirection (x, y, color, 1, 1))
            valid.append (self.checkOneDirection (x, y, color, 0, 1))
            valid.append (self.checkOneDirection (x, y, color, -1, 1))

        converts = []
        hasMove = False
        for (v, x, y, i, j) in valid:
            if v == True:
                converts.append ((x, y, i, j))
                hasMove = True

        return (hasMove, converts)

    def checkOneDirection (self, x, y, color, x_change, y_change):

        new_x = x + x_change
        new_y = y + y_change
        di = -1
        dj = -1
        dx = 0
        dy = 0

        if new_x < 0 or new_x >= self.size:
            return (False, dx, dy, di, dj)

        if new_y < 0 or new_y >= self.size:
            return (False, dx, dy, di, dj)

        adjColor = self.pieces[new_x][new_y].color
        if adjColor == color or adjColor == Color.neither:
            return (False, dx, dy, di, dj)

        i = x + 2 * x_change
        j = y + 2 * y_change
        valid = (False, dx, dy, di, dj)
        while (i != -1 and j != -1 and i != self.size and j != self.size):
            if self.pieces [i][j].color == color:
                valid = (True, x_change, y_change, i, j)
                break
            i += x_change
            j += y_change

        return valid

    def findPositions (self):

        pos = []
        for j in range (self.size):
            for i in range (self.size):
                if self.pieces [i][j].color == self.player.swap():
                    pos.append ((i-1, j))
                    pos.append ((i-1, j-1))
                    pos.append ((i, j-1))
                    pos.append ((i+1, j-1))
                    pos.append ((i+1, j))
                    pos.append ((i+1, j+1))
                    pos.append ((i, j+1))
                    pos.append ((i-1, j+1))
        # print (pos)

        posMoves = []
        pm = []
        for x, y in pos:
            (hasMove, converts) = self.checkValidMove (x, y, self.player)
            if hasMove and posMoves.count ((x,y)) == 0:
                posMoves.append ((x, y, converts))
                pm.append ((x, y))

        self.possibleMoves = posMoves
        print (pm)
        # print (self.possibleMoves)

    def makeMove (self, x, y, converts):

        self.pieces [x][y].color = self.player
        for (x_change, y_change, end_x, end_y) in converts:
            if x_change != 0 and y_change != 0:
                for i, j in zip (range (x, end_x, x_change), range (y, end_y, y_change)):
                    self.pieces [i][j].color = self.player
                break

            if x_change != 0:
                for i in range (x, end_x, x_change):
                    self.pieces [i][y].color = self.player

            if y_change != 0:
                for j in range (y, end_y, y_change):
                        self.pieces [x][j].color = self.player

        self.updateDisplay ()
        self.player = self.player.swap()
        self.findPositions ()
        if len (self.possibleMoves) == 0:
            self.player = self.player.swap ()
            self.findPositions ()
            if len (self.possibleMoves) == 0:
                self.end ()
        else:
            (x, y) = self.computer.move (self.pieces, self.player)
            self.computerMove (x, y)
        # self.expand ()

    def computerMove (self, x, y):
        (hasMove, converts) = self.checkValidMove (x, y, self.player)
        #print (converts)

        if hasMove:
            self.pieces [x][y].color = self.player
            for (x_change, y_change, end_x, end_y) in converts:
                if x_change != 0 and y_change != 0:
                    for i, j in zip (range (x, end_x, x_change), range (y, end_y, y_change)):
                        self.pieces [i][j].color = self.player
                    break

                if x_change != 0:
                    for i in range (x, end_x, x_change):
                        self.pieces [i][y].color = self.player

                if y_change != 0:
                    for j in range (y, end_y, y_change):
                            self.pieces [x][j].color = self.player

            self.updateDisplay ()
            self.player = self.player.swap()
            self.findPositions ()
            if len (self.possibleMoves) == 0:
                self.player = self.player.swap ()
                self.findPositions ()
                if len (self.possibleMoves) == 0:
                    self.end ()
        else:
            self.sendStatus ("Invalid Move!")

    def updateDisplay (self):
        if self.displayBoard == None:
            return
        self.displayBoard.update()

    def sendStatus (self, str):
        if self.displayBoard == None:
            return

        self.displayBoard.msg2Statusbar.emit (str)
        return

    def expand (self):
        for (x, y, converts) in self.possibleMoves:
            temp = AbstractBoard (self.size, self.player)
            temp.makeMove (x, y, converts)
            self.nextStates.append (temp)

        print (self.nextStates)

    def evaluate (self, color):
        if self.ended ():
            (b, w) = self.count ()
            if color == Color.black:
                if b > w:
                    return 1
                if w > b:
                    return -1
            if color == Color.white:
                if b > w:
                    return -1
                if w > b:
                    return 1

        return 0

    def count (self):
        b = 0
        w = 0
        for j in range (self.size):
            for i in range (self.size):
                if self.pieces[i][j].color == Color.black:
                    b += 1
                if self.pieces[i][j].color == Color.white:
                    w += 1
        return (b, w)

    def end (self):
        return

from othello import *
from keras.models import load_model
import operator

class Computer ():

    original = None
    size = 8
    valueNetwork = None
    policyNetwork = None
    v = []

    def __init__ (self):
        self.valueNetwork = load_model (valueNN)
        self.policyNetowrk = load_model (policyNN)
        return
 
    # Convert board so that it is now black's move    
    def setOriginal (self, pieces, player):
        board = []
        for j in range (self.size):
            row = []
            for i in range (self.size):
                row.append (0)
            board.append (row)

        for j in range (self.size):
            for i in range (self.size):
                if pieces[i][j].color == player:
                    board [i][j] = 1
                    print ("409")
                else:
                    if pieces [i][j].color == player.swap ():
                        board [i][j] = -1
                        print ("413")
                    else:
                        board [i][j] = 0
                        print (pieces[i][j].color)

        self.original = State (board = board)

    # def move (self, pieces, player):
    #     self.setOriginal (pieces, player)
    #     print (len (self.original.validMoves))
    #     NNs = []
    #     for i in range (len (self.original.validMoves)):
    #         (x, y, _) = self.original.validMoves [i]
    #         temp = self.original.move (x, y)
    #         smallNN = convertToNN (temp.board)
    #         NNs.append (smallNN)


    #     X = np.asarray(NNs)
    #     print ("Shape!!!: ", X.shape)
    #     value = self.valueNetwork.predict (X)

    #     index, value = max(enumerate(value), key=operator.itemgetter(1))
    #     (x, y, _) = self.original.validMoves [index]
    #     return (x, y)

    def move (self, pieces, player):
        self.setOriginal (pieces, player)
        print (len (self.original.validMoves))

        v2 = []
        for i in range (len (self.original.validMoves)):
            (x, y, _) = self.original.validMoves [i]
            temp = self.original.move (x, y)
            v = []

            for j in range (len(temp.validMoves)):
                (x, y, _) = temp.validMoves [j]
                temp2 = temp.move (x, y)
                
                NNs = []

                for k in range (len(temp2.validMoves)):
                    (x, y, _) = temp2.validMoves [k]
                    temp3 = temp2.move (x, y)
                    smallNN = convertToNN (temp3.board)
                    NNs.append (smallNN)


                X = np.asarray(NNs)
                print ("Shape!!!: ", X.shape)
                value = self.valueNetwork.predict (X)

                maxValue = max (value)
                v.append (maxValue)

            maxV = max (v)
            v2.append (maxV)

        index, _ = max(enumerate(v2), key=operator.itemgetter(1))
        (x, y, _) = self.original.validMoves [index]
        return (x, y)

# ========================================== #

class Othello(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.board = Board(self, Color.black)
        self.initUI()

    def initUI(self):    

        self.setCentralWidget(self.board)

        self.statusbar = self.statusBar()        
        self.board.msg2Statusbar[str].connect(self.statusbar.showMessage)
        
       # self.board.start()
        
        self.resize(self.board.desiredWidth, self.board.desiredHeight + self.statusbar.sizeHint().height())
        self.center()
        self.setWindowTitle('Othello')        
        self.show()

    def center(self):
        
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

# ========================================== #

class Board (QFrame):

    msg2Statusbar = pyqtSignal(str)
    size = 8
    roomPerGrid = 50
    desiredWidth = roomPerGrid * size
    desiredHeight = roomPerGrid * size

    def __init__(self, parent, c):
        super().__init__(parent)
        self.initGame ()
        self.initSensor ()

    def initSensor (self):
        self.setMouseTracking (True)

    def initGame (self):
        self.absBoard = AbstractBoard (self.size, Color.black)
        self.absBoard.setDisplayBoard (self)

    def paintEvent (self, event):

        black = QColor (0x000000)
        grey = QColor (0xC0C0C0)
        white = QColor (0xFFFFFF)

        painter = QPainter (self)
        self.drawGrid (painter, grey)

        for j in range (self.size):
            for i in range (self.size):
                if self.absBoard.pieces[i][j].color == Color.neither:
                    continue
                if self.absBoard.pieces[i][j].color == Color.white:
                    self.drawPiece (painter, i, j, white)
                    continue
                if self.absBoard.pieces[i][j].color == Color.black:
                    self.drawPiece (painter, i, j, black)
                    continue


    def drawGrid (self, painter, color):

        painter.setPen (color)

        for i in range (self.size):
            painter.drawLine (self.roomPerGrid * i, 0, self.roomPerGrid * i, self.desiredHeight)
        
        for i in range (self.size):
            painter.drawLine (0, self.roomPerGrid * i, self.desiredWidth, self.roomPerGrid * i)

    def drawPiece (self, painter, i, j, color):

        center_x = i * self.roomPerGrid + 1
        center_y = j * self.roomPerGrid + 1
        radius = self.roomPerGrid - 2
        painter.setBrush (color)
        painter.drawEllipse (center_x, center_y, radius, radius)

    def mouseMoveEvent (self, e):
        (x, y) = self.getCoordinate (e)
        str_x = str (x)
        str_y = str (y)

        # if (x > 6 and y > 7):
        #     self.pieces [5][6].color = Color.white
        #     self.update()

        playerMove = ""

        if self.absBoard.player == Color.black:
            playerMove = playerMove + "Black"
        else:
            playerMove = playerMove + "White"
        playerMove = playerMove + "'s move "

        self.msg2Statusbar.emit(playerMove + "(" + str_x + ", " + str_y + ")")

        # if self.checkValidMove (x, y, Color.white):
        #     msg = "OK"
        # else:
        #     msg = "Nay"

        # self.msg2Statusbar.emit (msg)

    def mousePressEvent (self, e):
        (x, y) = self.getCoordinate (e)
        if x == 0 and y == 0:
            print(self.absBoard.count())
        self.absBoard.tryMove (x, y)

    def getCoordinate (self, e):
        x = int(e.x() / self.roomPerGrid)
        y = int(e.y() / self.roomPerGrid)

        return (x, y)

# -------------------- Main ----------------------- #

if __name__ == "__main__":

    (policyNN, valueNN) = getNetworks ()

    app = QApplication (sys.argv)
    othello = Othello ()
    sys.exit(app.exec_())