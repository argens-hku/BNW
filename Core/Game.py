from othello import State

policyNN = "PolicyNetwork/policy_network.h5"
valueNN = "ValueNetwork/value_network11.h5"

border_bool = True
corner_bool = True
liberty_bool = True

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
        print ("Trying to update display")
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

# ========================================== #

class Computer ():

    tree = None
    evaluator = None

    def __init__ (self):
        valueNetwork = load_model (valueNN)
        self.evaluator = Evaluator (valueNetwork, border = border_bool, corner = corner_bool, liberty = liberty_bool)
        self.tree = Tree (self.evaluator)

        return

    def updateMove (x. y):
        self.tree.updateMove (x, y)

    def move (self):
        (x, y) = self.tree.getBestMove ()
        return (x, y)

from keras.models import load_model
class Evaluator ():

    def __init__ (self, valueNN, border = "False", corner = "False", liberty = "False"):
        self.valueNN = valueNN
        self.border = border
        self.corner = corner
        self.liberty = liberty
        return

    def evaluate (self, state, player):
        NN = []
        NN.append (self.convertToNN (state.mirrored (), player))
        X = np.asarray (NN)
        value = self.valueNN.predict (X)
        return value [0][0]

    def convertToNN (self, board, player):
        input_NN = []
        white = []
        black = []
        empty = []

        if self.border or self.corner:
            border = []

        if self.liberty:
            moves = []

        for i in range (size):
            row_white = []
            row_black = []
            row_empty = []

            if self.border or self.corner:
                row_border = []

            if self.liberty:
                row_total = []

            for j in range (size):

                if self.border == True:
                    if i == 0 or j == 0 or i == size-1 or j == size-1:
                        row_border.append (1)
                    else:
                        row_border.append (0)
                else:
                    if self.corner == True:
                        row_border.append (0)

                piece = line [i][j] * player
                if piece == 0:
                    row_empty.append (1)
                    row_black.append (0)
                    row_white.append (0)
                    if self.liberty:
                        row_total.append (0)
                else:
                    if piece == 1:
                        row_empty.append (0)
                        row_black.append (1)
                        row_white.append (0)
                        if self.liberty:
                            row_total.append (1)
                    else:
                        row_empty.append (0)
                        row_black.append (0)
                        row_white.append (1)
                        if self.liberty:
                            row_total.append (-1)

            empty.append (row_empty)
            white.append (row_white)
            black.append (row_black)

            if self.border or self.corner:
                border.append (row_border)
            if self.liberty:
                moves.append (row_total)

        if self.corner:
            border [0][0] = border [0][size - 1] = border [size - 1][0] = border [size - 1][size - 1] = 4
            border [0][1] = border [1][0] =  border [1][1] = -1
            border [0][size - 2] = border [1][size - 1] =  border [1][size - 2] = -1
            border [size - 2][0] = border [size - 1][1] =  border [size - 2][1] = -1
            border [size - 2][size - 1] = border [size - 1][size - 2] = border [size - 1][size - 1] =  -1

        e = np.asarray (empty)
        w = np.asarray (white)
        bl = np.asarray (black)

        input_NN.append (e)
        input_NN.append (w)
        input_NN.append (bl)

        if self.border or self.corner:
            bd = np.asarray (border)
            input_NN.append (bd)
        
        if self.liberty:
            state = State (board = moves)
            for i in range (size):
                for j in range (size):
                    moves [i][j] = 0

            for (x, y, _) in state.validMoves:
                moves [x][y] = 1

            mv = np.asarray (moves)
            input_NN.append (mv)

        # print ("e", e.shape)
        # print ("w", w.shape)
        # print ("bl", bl.shape)

        # b = np.asarray (board)
        # print ("b.shape", b.shape)
        return input_NN

from othello import *
from collections import deque

class Tree ():

    currentNode = None
    originalPlayer = 0
    leaf = deque ([])
    depth = 0

    def __init__ (self, evaluator):
        self.evaluator = evaluator

    def updateMove (self, x, y):

        if self.currentNode = None:
            state = State ()
            state = state.move (x, y)
            self.currentNode = Node (state = state)
            self.currentNode.evaluator = self.evaluator
            return

        temp = self.currentNode
        self.currentNode.reduceDepth ()
        self.depth -= 1
        self.currentNode = self.currentNode.children ((x, y))
        del temp

        return

    def getBestMove (self):

        if originalPlayer == 0:
            self.originalPlayer = self.currentState.player
            self.currentNode.originalPlayer = self.originalPlayer

        if self.depth < 5:
            currentNode.evaluate (depth = 2)
            currentNode.evaluate (depth = 5)

        self.depth -= 1
        return currentNode.getBestMove ()

    def expand (self):

        self.depth += 1
        self.currentNode.evaluate (depth = self.depth)
        return


class Node ():

    minimum = -100
    maximium = 100
    neutral = 0

    def __init__ (self, state = None, depth = 0, alpha = self.minimum, beta = self.maximium, parent = None):
        self.state = State
        self.depth = depth
        self.alpha = alpha
        self.beta = beta
        self.parent = parent

        self.player = self.state.player
        self.children = {}
        self.value = None
        self.order = []

        if self.parent != None:
            self.evaluator = self.parent.evaluator
            self.originalPlayer = self.parent.originalPlayer

        return

    def evaluate (self, depth = 0):
        if depth == 0 or len (self.state.validMoves) == 0:
            if self.value != None:
                return self.value
            self.value = self.evaluator.evaluate (self.state, self.originalPlayer)
            return self.value
        
        if self.depth >= depth:
            if self.value != None:
                return self.value

        if self.state.player == 0:
            score = self.originalPlayer * (self.state.bc - self.state.wc)
            if score > 0:
                return self.maximium
            if score == 0:
                return self.neutral
            if score < 0:
                return self.minimum

        if len (self.order) == 0:
            ordering = range (len (self.state.validMoves))
        else:
            ordering = self.order
        newOrder = {}

        if self.state.player == self.originalPlayer:
            
            for i in ordering:
                newOrder [i] = self.minimum

            v = self.minimum
            for i in ordering:
                
                (x, y, _) = self.state.validMoves [i]
                
                if (x, y) in self.children:
                    self.children.updateAlphaBeta (alpha = self.alpha, beta = self.beta)

                else:
                    childState = self.state.move (x, y)
                    childNode = Node (state = childState, alpha = self.alpha, beta = self.beta, parent = self)
                    self.children [(x, y)] = childNode

                childvalue = self.children [(x, y)].evaluate (depth - 1)
                newOrder [(x, y)] = childvalue
                if childvalue > v:
                    v = childvalue
                if v > self.alpha:
                    self.alpha = v
                if self.beta <= self.alpha
                    break

            self.order = sorted (newOrder.items(), key = operator.itemgetter (0), reverse = True)
            return v

        else:

            for i in ordering:
                newOrder [i] == self.maximium

            v = self.maximium

            for i in ordering:

                (x, y, _) = self.state.validMoves [i]

                if (x, y) in self.children:
                    self.children.updateAlphaBeta (alpha = self.alpha, beta = self.beta)

                else:
                    childState = self.state.move (x, y)
                    childNode = Node (state = childState, alpha = self.alpha, beta = self.beta, parent = self)
                    self.children [(x, y)] = childNode

                childvalue = self.children [(x, y)].evaluate (depth -1)
                newOrder [(x, y)] = childNode
                if childvalue  < v:
                    v = childvalue
                if v < self.beta:
                    self.beta = v
                if self.beta <= self.alpha:
                    break

            self.order = sorted (newOrder.items(), key = operator.itemgetter (0))
            return v

    def updateAlphaBeta (self, alpha, beta):
        self.alpha = alpha
        self.beta = beta
        return



        


    def expand (self, depth = 0):
        if depth = 0:
            end_expansion = 0
            for i in range (len (self.state.validMoves)):
                (x, y, _) = self.state.validMoves [i]
                childState = self.state.move (x, y)
                childNode = Node (state = childState, depth = self.depth + 1, alpha = self.alpha, beta = self.beta, parent = self)
                self.children ((x, y): childNode)
        return

    def reduceDepth (self):
        self.depth -= 1
        for _, child in self.children.items ():
            child.reduceDepth ()

    def getBestMove (self):
        self.reduceDepth ()
        maxValue = -100
        bestMove = (-1, -1)
        for move, child in self.children.items ():
            if child.value > maxValue:
                maxValue = child.value
                bestMove = move

        return move


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