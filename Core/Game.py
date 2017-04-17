from othello import State

policyNN = "PolicyNetwork/policy_network.h5"
valueNN = "ValueNetwork/value_network13.h5"

# 2 for boders only
# 9 for corner and border

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
        self.end = False
        self.computer = Computer (player = -1)
        self.state.setAbsBoard (self)
        return

    def setDisplayBoard (self, db):
        self.displayBoard = db
        return

    def move (self, x, y):

        s = self.state.move (x, y)
        if s != None:
            self.state = s
            self.computer.updateMove (x, y)
            if self.state.player == 0:
                self.end = True
        else:
            self.displayBoard.highlightGrid (self.state.validMoves)
        self.updateDisplay ()

        while self.player != self.state.player and self.state.player != 0:
            (x, y) = self.computer.move ()
            s = self.state.move (x, y)
            if s != None:
                self.state = s
                self.computer.updateMove (x, y)
                if self.state.player == 0:
                    self.end = True
            else:
                # clearScreen ()
                # self.computer.tree.currentNode.state.print ()
                # print (x, y)
                break
            self.updateDisplay ()

        # self.expand ()

    def updateDisplay (self):
        print ("Trying to update display")
        if self.displayBoard == None:
            return
        self.displayBoard.update()

    def sendStatus (self, str):
        if self.displayBoard == None:
            return

        if self.end == True:
            return

        self.displayBoard.msg2Statusbar.emit (str)
        return

    def isValid (self, x, y):
        (b, _) = self.state.isValid (x, y)
        return b

# ========================================== #

class Computer ():

    tree = None

    def __init__ (self, player):
        self.tree = Tree (player)

        return

    def updateMove (self, x, y):
        print ("151")
        self.tree.updateMove (x, y)
        print ("153")

    def move (self):
        return self.tree.getBestMove ()

from othello import *
from collections import deque
from threading import Thread, Lock
import threading
from evaluator import Evaluator
from time import sleep
class Tree ():

    def __init__ (self, originalPlayer):

        self.originalPlayer = originalPlayer

        self.lock = Lock ()
        self.priority = False
        thread = Thread (target = self.expand, daemon = True)
        thread.start ()
        print ("Thread!!", threading.active_count ())

    def updateMove (self, x, y):

        self.priority = True
        self.lock.acquire ()
        print ("Self.currentNode.depth", self.currentNode.depth)

        # if self.currentNode == None:
        #     state = State ()
        #     state = state.move (x, y)
        #     self.currentNode = Node (state = state)
        #     self.currentNode.originalPlayer = self.originalPlayer
        #     self.currentNode.evaluator = self.evaluator
        #     self.currentNode.evaluate (depth = 2)
        #     self.currentNode.evaluate (depth = 4)
        #     self.depth = 4

        # else:

        # while self.currentNode.depth < 4:
        #     self.nextNode = self.nextNode.expand ()

        counter = 0
        for i in self.currentNode.order:
            (x1, y1, _) = self.currentNode.state.validMoves [i]
            if (x1, y1) == (x, y):
                break
            else:
                counter += 1   

        if (x, y) in self.currentNode.children:
            self.currentNode = self.currentNode.children [(x, y)]
            if counter != self.currentNode.parent.expandedChildNode:
                self.nextNode = self.currentNode.leftMost ()
            self.currentNode.parent = None
            self.currentNode.resetAlphaBeta ()
        else:
            childState = self.currentNode.state.move (x, y)
            childNode = Node (state = childState)
            childNode.evaluator = self.currentNode.evaluator
            childNode.originalPlayer = self.originalPlayer
            
            self.currentNode = childNode
            self.nextNode = self.currentNode

        self.priority = False
        self.lock.release ()

        return

    def initialize (self):
        self.currentNode = Node (state = State ())
        self.currentNode.originalPlayer = self.originalPlayer
        self.currentNode.evaluator = Evaluator (valueNN, border = border_bool, corner = corner_bool, liberty = liberty_bool)
        self.nextNode = self.currentNode

    def getBestMove (self):

        if len (self.currentNode.state.validMoves) == 1:
            (x, y, _) = self.currentNode.state.validMoves [0]
            return (x, y)

        self.priority = True
        self.lock.acquire ()
        
        if self.currentNode == None:
            self.priority = False
            self.lock.release ()
            sleep (0.5)
            self.priority = True
            self.lock.acquire ()

        if self.currentNode.depth < 5:
            targetDepth = 64 - self.currentNode.state.bc - self.currentNode.state.wc - 1
            if targetDepth > 5:
                targetDepth = 5
            while self.currentNode.depth < targetDepth:
                self.nextNode = self.nextNode.expand ()

        # if self.currentNode == None:
        #     state = State ()
        #     self.currentNode = Node (state = state)
        #     self.currentNode.originalPlayer = self.originalPlayer
        #     self.currentNode.evaluator = self.evaluator
        #     self.currentNode.evaluate (depth = 2)
        #     self.currentNode.evaluate (depth = 4)
        #     self.depth = 4
        move = self.currentNode.getBestMove ()
        self.lock.release ()
        self.priority = False
        return move

    def expand (self):
        
        self.currentNode = Node (state = State ())
        self.currentNode.originalPlayer = self.originalPlayer
        self.currentNode.evaluator = Evaluator (valueNN, border = border_bool, corner = corner_bool, liberty = liberty_bool)
        self.nextNode = self.currentNode
        
        while True:
            print ("Hi")
            if self.priority == True:
                sleep (0.3)
            self.lock.acquire ()
            self.nextNode = self.nextNode.expand ()


            # print ("======================")
            # self.nextNode.state.print ()
            # print (self.nextNode.depth)
            # print ("======================")
            self.lock.release ()

            if self.currentNode.depth > (64 - self.currentNode.state.bc - self.currentNode.state.wc):
                break

import operator
class Node ():

    minimum = -100
    maximum = 100
    neutral = 0

    def __init__ (self, state = None, alpha = minimum, beta = maximum, parent = None):
        self.state = state
        self.alpha = alpha
        self.beta = beta
        self.parent = parent

        self.depth = 0
        self.children = {}
        self.value = None
        self.order = []
        self.expandedChildNode = 0

        if self.parent != None:
            self.evaluator = self.parent.evaluator
            self.originalPlayer = self.parent.originalPlayer

        return

    def expand (self):

        self.state.print ()

        if self.state.player == 0:
            self.depth += 1
            print (self.depth)
            return self.nextNode ()

        if len (self.order) == 0:
            ordering = range (len (self.state.validMoves))
        else:
            ordering = self.order

        order = {}

        if self.state.player == self.originalPlayer:

            for i in ordering:
                order [i] = self.minimum

            v = self.minimum
            firstMove = False

            for i in ordering:
                if self.state.firstMove == -1:
                    firstMove = True
                (x, y, _) = self.state.validMoves [i]
                
                if (x, y) in self.children:
                    self.children [(x, y)].updateAlphaBeta (self.alpha, self.beta)
                else:
                    childState = self.state.move (x, y)
                    childNode = Node (state = childState, alpha = self.alpha, beta = self.beta, parent = self)
                    self.children [(x, y)] = childNode

                childValue = self.children [(x, y)].evaluate ()
                order [i] = childValue
                if childValue > v:
                    v = childValue
                if v > self.alpha:
                    self.alpha = v
                if self.beta <= self.alpha:
                    break

                if firstMove:
                    self.state.firstMove = -1

            temp_lst = sorted (order.items (), key = operator.itemgetter (1), reverse = True)
        else:

            for i in ordering:
                order [i] = self.maximum

            v = self.maximum
            firstMove = False

            for i in ordering:
                if self.state.firstMove == -1:
                    firstMove = True
                (x, y, _) = self.state.validMoves [i]
                
                if (x, y) in self.children:
                    self.children [(x, y)].updateAlphaBeta (self.alpha, self.beta)
                else:
                    childState = self.state.move (x, y)
                    childNode = Node (state = childState, alpha = self.alpha, beta = self.beta, parent = self)
                    self.children [(x, y)] = childNode

                childValue = self.children [(x, y)].evaluate ()
                order [i] = childValue
                if childValue < v:
                    v = childValue
                if v < self.beta:
                    self.beta = v
                if self.beta <= self.alpha:
                    break

                if firstMove:
                    self.state.firstMove = -1

            temp_lst = sorted (order.items (), key = operator.itemgetter (1), reverse = False)

        self.order = [pair [0] for pair in temp_lst]
        self.value = v
        self.depth += 1
        if self.parent != None and self.depth == self.parent.depth:
            self.parent.expandedChildNode += 1
            # print (self.parent.expandedChildNode, "/", len(self.parent.state.validMoves))
        return self.nextNode ()

    def nextNode (self):

        parent = self.parent

        if parent == None:
            self.cleanse ()
            return self.leftMost ()

        if parent.depth >= self.depth + 1:
            self.cleanse ()
            self.alpha = parent.alpha
            self.beta = parent.beta
            self.refreshAlphaBeta ()
            return self.leftMost ()

        if parent.expandedChildNode >= len (parent.state.validMoves):
            print ("433")
            return parent

        # parent.state.print ()
        # print (parent.state.validMoves)
        # print (len (parent.state.validMoves))
        # print (parent.order)
        # print (parent.expandedChildNode)
        

        if parent.state.player == parent.originalPlayer:
            if self.value > parent.alpha:
                parent.alpha = self.value
                parent.updateAlphaBeta (parent.alpha, parent.beta)
        else:
            if self.value < parent.beta:
                parent.beta = self.value
                parent.updateAlphaBeta (parent.alpha, parent.beta)
        if parent.beta <= parent.alpha:
            print ("452")
            return parent

        (x, y, _) = parent.state.validMoves [parent.order [parent.expandedChildNode]]

        if not (x, y) in parent.children: 
            childState = parent.state.move (x, y)
            childNode = Node (state = childState, alpha = parent.alpha, beta = parent.beta, parent = parent)
            parent.children [(x, y)] = childNode
        # print (x, y)
        return parent.children [(x, y)].leftMost ()
    
    def cleanse (self):
        self.expandedChildNode = 0
        self.alpha = self.minimum
        self.beta = self.maximum
        for key in self.children:
            self.children [key].cleanse ()

        return

    def leftMost (self):
        if len (self.children) == 0:
            return self

        if len (self.order) == 0:
            order = 0
        else:
            order = self.order [0]

        (x, y, _) = self.state.validMoves [order]
        return self.children [(x, y)].leftMost ()

    def evaluate (self):

        if self.value != None:
            return self.value

        value = self.evaluator.evaluate (self.state, self.originalPlayer)
        self.value = value

        return value

    def updateAlphaBeta (self, alpha, beta):
        for i in range (self.expandedChildNode, len  (self.order)):
            index = self.order [i]
            (x, y, _) = self.state.validMoves [index]
            if (x, y) in self.children:
                self.children [(x, y)].alpha = alpha
                self.children [(x, y)].beta = beta

        return

    def reduceDepth (self):
        self.depth -= 1
        for _, child in self.children.items ():
            child.reduceDepth ()

    def getBestMove (self):
        order = self.order [0]
        (x, y, _) = self.state.validMoves [order]
        return (x, y)

    def resetAlphaBeta (self):
        self.alpha = self.minimum
        self.beta = self.maximum
        for key in self.children:
            self.children[key].resetAlphaBeta ()
        return

    def print (self):
        if self.depth == 0:
            return
        print (self.depth)
        if len (self.order) == 0:
            ordering = range (len (self.state.validMoves))
        else:
            ordering = self.order
            print ("Using self order")

        for i in ordering:
            (x, y, _) = self.state.validMoves [i]
            if (x, y) in self.children:
                print (self.children [(x, y)].depth,"(",x,y,")", end = ',')
        print ("")
        print ("---------------")
        for i in ordering:
            (x, y, _) = self.state.validMoves [i]
            if (x, y) in self.children:
                self.children [(x, y)].print ()

    def refreshAlphaBeta (self):
        if len (self.children) == 0:
            return self.evaluate ()

        if self.state.player == self.originalPlayer:
            v = self.minimum
            for i in self.order:
                (x, y, _) = self.state.validMoves [i]
                key = (x, y)
                if key in self.children:
                    self.children[key].alpha = self.alpha
                    self.children[key].beta = self.beta
                    childValue = self.children [key].refreshAlphaBeta ()

                if childValue > v:
                    v = childValue
                if v > self.alpha:
                    self.alpha = v
            
            self.value = v
            return self.value
        else:
            v = self.maximum
            for i in self.order:
                (x, y, _) = self.state.validMoves [i]
                key = (x, y)
                if key in self.children:
                    self.children[key].alpha = self.alpha
                    self.children[key].beta = self.beta
                    childValue = self.children [key].refreshAlphaBeta ()
                if childValue < v:
                    v = childValue
                if v < self.beta:
                    self.beta = v
                
            self.value = v
            return self.value
        return





# ========================================== #

class Othello(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.board = Board(self)
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

from PyQt5 import QtCore
class Board (QFrame):

    msg2Statusbar = pyqtSignal(str)
    size = 8
    roomPerGrid = 50
    desiredWidth = roomPerGrid * size
    desiredHeight = roomPerGrid * size
    x = 3
    y = 3
    validMoves = []
    alpha = 255
    timer = QtCore.QTimer ()

    def __init__(self, parent):
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

        lightgreen = QColor (0x9be315)
        lightpink = QColor (0xfc8096)

        paintedMove = False

        painter = QPainter (self)
        self.drawGrid (painter, grey)

        if self.absBoard.state.board [self.x][self.y] == 0:
            if self.absBoard.isValid (self.x, self.y):
                self.fillGrid (painter, self.x, self.y, lightgreen)
            else:
                self.fillGrid (painter, self.x, self.y, lightpink)
            if (self.x, self.y) in self.validMoves:
                paintedMove = True
                self.validMoves = []
                self.timer.stop ()

        for j in range (self.size):
            for i in range (self.size):
                if self.absBoard.state.board[i][j] == 0:
                    if not paintedMove:
                        if (i, j) in self.validMoves:
                            self.fillGrid (painter, i, j, QColor (0, 128, 0, self.alpha))
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

    def fillGrid (self, painter, x, y, color):

        painter.setBrush (color)
        painter.drawRect (x * self.roomPerGrid, y * self.roomPerGrid, self.roomPerGrid, self.roomPerGrid)
    
    def highlightGrid (self, validMoves):

        interval = 50
        speed = 15
        self.timer = QtCore.QTimer ()
        self.validMoves = [(move [0], move [1]) for move in validMoves]
        self.alpha = 255
        self.timer.timeout.connect (lambda: self.dropAlpha (speed, validMoves))
        self.jumpCount = 0
        self.timer.start (interval)
        return

    def dropAlpha (self, speed, validMoves):

        self.alpha -= speed

        if self.alpha < 127 and self.jumpCount < 1:
            self.jumpCount += 1
            self.alpha = 255

        if self.alpha < 0:
            self.timer.stop ()
            self.validMoves = []
            return

        self.update ()
        return

    def mouseMoveEvent (self, e):
        (x, y) = self.getCoordinate (e)
        str_x = str (x)
        str_y = str (y)

        # if (x > 6 and y > 7):
        #     self.pieces [5][6].color = Color.white
        #     self.update()

        playerMove = ""

        if self.absBoard.player == 1:
            playerMove = playerMove + "Black"
        else:
            playerMove = playerMove + "White"
        playerMove = playerMove + "'s Move "

        self.absBoard.sendStatus(playerMove + "(" + str_x + ", " + str_y + ")")

        self.x = x
        self.y = y
        self.update ()

    def mousePressEvent (self, e):
        (x, y) = self.getCoordinate (e)
        if x == 0 and y == 0:
            painter = QPainter (self)
            self.drawPiece (painter, 0, 0, QColor (0xb0e0e6))
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