from othello import State

policyNN = "PolicyNetwork/policy_network.h5"
valueNN = "ValueNetwork/value_network9.h5"
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

    # q = "Which policy network would you like to use?"
    # file = Path (policyNN)
    # while not file.is_file():
    #     policyNN = "PolicyNetwork/" + query (question = q)
    #     file = Path (policyNN)

    q = "Which value network would you like to use?"
    file = Path (valueNN)
    while not file.is_file():
        valueNN = "ValueNetwork/" + query (question = q)
        file = Path (valueNN)

    return (policyNN, valueNN)

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

    possibleMoves = []
    nextStates = []
    score = 0
    displayBoard = None
    state = State ()
    player = 1

    # @classmethod
    # def placeHolder (self):
    #     pieces = []

    def __init__ (self, size):

        self.size = size
        self.computer = Computer ()
        self.state.setAbsBoard (self)
        return

    def setDisplayBoard (self, db):
        self.displayBoard = db
        return
#    def __init__ (self, displayBoard, prevBoard, move);

    def move (self, x, y):

        s = self.state.move (x, y)
        if s != None:
            self.state = s
        self.updateDisplay ()

        if self.state.player == 0:
            self.end ()

        if self.player != self.state.player:
            print ("Self.player", self.player)
            print ("Self.state.player", self.state.player)
            (x, y) = self.computer.move (self.state)
            self.move (x, y)
        # self.expand ()

    def updateDisplay (self):
        if self.displayBoard == None:
            return
        self.displayBoard.update()

    def sendStatus (self, str):
        if self.displayBoard == None:
            return

        self.displayBoard.msg2Statusbar.emit (str)
        return

    def end (self):
        while 1:
            x = 1
        return

from othello import *
from keras.models import load_model
import operator

class Computer ():

    original = None
    valueNetwork = None
    maximum = 100
    neutral = 0
    minimum = -100
    # policyNetwork = None
    v = []

    def __init__ (self):
        self.valueNetwork = load_model (valueNN)
        # self.policyNetowrk = load_model (policyNN)
        return
 
    def convertToNN (self, line, player):
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
                piece = line [i][j] * player
                if piece == 0:
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

        border [0][0] = border [0][size - 1] = border [size - 1][0] = border [size - 1][size - 1] = 4
        border [0][1] = border [1][0] =  border [1][1] = -1
        border [0][size - 2] = border [1][size - 1] =  border [1][size - 2] = -1
        border [size - 2][0] = border [size - 1][1] =  border [size - 2][1] = -1
        border [size - 2][size - 1] = border [size - 1][size - 2] = border [size - 1][size - 1] =  -1

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

    def nnValue (self, state, player):

        NN = []
        NN.append (self.convertToNN (state.mirrored (), player))
        X = np.asarray (NN)
        value = self.valueNetwork.predict (X)
        return value [0][0]

    def alphabeta (self, state, depth, alpha, beta, originalPlayer):
        
        a = alpha
        b = beta

        if state.player == 0:
            score = originalPlayer * (state.bc - state.wc)
            if score > 0:
                return self.maximum
            if score == 0:
                return self.neutral
            return self.minimum

        if depth == 0:
            return self.nnValue (state, originalPlayer)

        if state.player == originalPlayer:
            v = self.minimum
            for i in range (len(state.validMoves)):
                (x, y, _) = state.validMoves [i]
                childState = state.move (x, y)
                childState.absBoard = None
                childStateValue = self.alphabeta (childState, depth -1, alpha, beta, originalPlayer)
                if childStateValue > v:
                    v = childStateValue
                if v > a:
                    a = v
                if b <= a:
                    break
            return v
        else:
            v = self.maximum
            for i in range (len(state.validMoves)):
                (x, y, _) = state.validMoves [i]
                childState = state.move (x, y)
                childState.absBoard = None
                childStateValue = self.alphabeta (childState, depth -1, alpha, beta, originalPlayer)
                if childStateValue < v:
                    v = childStateValue
                if v < b:
                    b = v
                if b <= a:
                    break
            return v           

    def move (self, state):

        if len (state.validMoves) == 0:
            return None

        if len (state.validMoves) == 1:
            (x, y, _) = state.validMoves [0]
            return (x, y)

        depth = 3
        maxValue = self.minimum
        maxIndex = 0
        originalPlayer = state.player
        for i in range (len (state.validMoves)):
            (x, y, _) = state.validMoves [i]
            value = self.alphabeta (state.move (x, y), depth, self.minimum, self.maximum, originalPlayer)
            if value > maxValue:
                maxIndex = i
                maxValue = value
        
        (x, y, _) =  state.validMoves [maxIndex]
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
        self.absBoard = AbstractBoard (self.size)
        self.absBoard.setDisplayBoard (self)

    def paintEvent (self, event):

        black = QColor (0x000000)
        grey = QColor (0xC0C0C0)
        white = QColor (0xFFFFFF)

        painter = QPainter (self)
        self.drawGrid (painter, grey)

        for j in range (self.size):
            for i in range (self.size):
                if self.absBoard.state.board[i][j] == 0:
                    continue
                if self.absBoard.state.board[i][j] == -1:
                    self.drawPiece (painter, i, j, white)
                    continue
                if self.absBoard.state.board[i][j] == 1:
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
        playerMove = playerMove + "'s Move "

        self.msg2Statusbar.emit(playerMove + "(" + str_x + ", " + str_y + ")")

        # if self.checkValidMove (x, y, Color.white):
        #     msg = "OK"
        # else:
        #     msg = "Nay"

        # self.msg2Statusbar.emit (msg)

    def mousePressEvent (self, e):
        (x, y) = self.getCoordinate (e)
        if x == 0 and y == 0:
            print(self.absBoard.state.count)
        self.absBoard.move (x, y)

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