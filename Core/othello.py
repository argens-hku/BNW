class State ():

    def __init__ (self, size = 8, board = None, player = 1, firstMove = -1, absBoard = None):
        self.player = player
        self.size = size
        self.board = []
        self.validMoves = []
        self.firstMove = firstMove
        self.absBoard = absBoard

        if board != None:
            for i in range (size):
                column = []
                for j in range (size):
                    column.append (board[i][j])
                self.board.append (column)
        else:
            for i in range (size):
                column = []
                for j in range (size):
                    if i == size / 2 - 1:
                        if j == size / 2:
                            column.append (1)
                            continue
                        if j == size / 2 - 1:
                            column.append (-1)
                            continue
                    
                    if i == size / 2:
                        if j == size / 2 - 1:
                            column.append (1)
                            continue
                        if j == size / 2:
                            column.append (-1)
                            continue

                    column.append (0)
                self.board.append (column)

        self.bc = 0
        self.wc = 0

        for i in range (size):
            for j in range (size):
                if self.board [i][j] == 1:
                    self.bc += 1
                    continue
                if self.board [i][j] == -1:
                    self.wc += 1

        self.count = (self.bc, self.wc)
        self.checkMoves ()

    def move (self, x, y):
        if self.firstMove == -1:
            self.firstMove = x

        print ((x, y, self.player))
        found = False
        for i in range (len(self.validMoves)):
            (le_x, le_y, changes) = self.validMoves [i]
            if x == le_x and y == le_y:
                found = True
                break
#        (valid, changes) = self.isValid (x, y)
        if not found:
            self.sendStatus ("Invalid Move!!!")
            return None

        temp = []
        for i in range (self.size):
            column = []
            for j in range (self.size):
                column.append (self.board [i][j])
            temp.append (column)

        temp [x][y] = self.player
        print (x, y)
        for (x, y) in changes:
            print (x, y)
            temp [x][y] = self.player

        if self.player == 1:
            newPlayer = -1
        else:
            newPlayer = 1

        state = State (board = temp, player = newPlayer, firstMove = self.firstMove, absBoard = self.absBoard)
        return state    

    def isValid (self, x, y):

        if x < 0 or y < 0 or x >= self.size or y >= self.size or self.board [x][y] != 0:
            return (False, [])

        directions = []
        for i in range (3):
            for j in range (3):
                directions.append ((i-1, j-1))

        directions.remove ((0, 0))

        converts = []
        for direction in directions:
            (x_change, y_change) = direction
            (valid, convert) = self.oneDirection (x, y, x_change, y_change)
            if not valid:
                continue
            for c in convert:
                converts.append (c)

        if (len (converts) == 0):
            return (False, converts)
        else:
            return (True, converts)

    def print (self):

        for j in range (self.size):
            s = ""
            for i in range (self.size):
                if self.board [i][j] == 0:
                    s = s + "."
                else:
                    if self.board [i][j] == -1:
                        s = s + "w"
                    else:
                        s = s + "b"
            print (s)

        s = ""
        for i in range (self.size):
            s = s + "-"

        print (s)
        return

    def printToFile (self, filename, move = (-1, -1)):

        outputFile = open (filename, 'a')
        outputFile.write ("Player:  ")
        if self.player == 1:
            outputFile.write ("Black (X)")
        else:
            outputFile.write ("White (O)")

        outputFile.write ("\n")

        for j in range (self.size):
            s = ""
            for i in range (self.size):
                if i == move [0] and j == move [1]:
                    if i == 0:
                        s = s + "?"
                    else:
                        s = s + " ?"
                    continue

                if self.board [i][j] == 0:
                    if i == 0:
                        s = s + "."
                    else:
                        s = s + " ."
                else:
                    if self.board [i][j] == -1:
                        if i == 0:
                            s = s + "O"
                        else:
                            s = s + " O"
                    else:
                        if i == 0:
                            s = s + "X"
                        else:
                            s = s + " X"
            s = s + "\n"
            outputFile.write (s)

        outputFile.close ()

        return

    def mirrored (self):
        temp = []
        for i in range (self.size):
            column = []
            for j in range (self.size):
                column.append (self.board[i][j])
            temp.append (column)

        if self.firstMove == 3 or self.firstMove == 5:
            for i in range (self.size):
                for j in range (i):
                    tempN = temp [i][j]
                    temp[i][j] = temp [j][i]
                    temp [j][i] = tempN

        if self.firstMove == 4 or self.firstMove == 5:
            for i in range (self.size):
                for j in range (self.size - 1 - i):
                    tempN = temp [i][j]
                    temp [i][j] = temp[self.size - 1 - j][self.size - 1 - i]
                    temp[self.size - 1 - j][self.size - 1 - i] = tempN

        return temp

    def asByte (self):

        temp = self.mirrored ()

        ## For testing of reflectivity
        # for j in range (self.size):
        #     s = ""
        #     for i in range (self.size):
        #         if temp [i][j] == 0:
        #             s = s + "."
        #         else:
        #             if temp [i][j] == -1:
        #                 s = s + "w"
        #             else:
        #                 s = s + "b"
        #     print (s)

        # return None

        ba = ""
        for j in range (self.size) :
            for i in range (self.size):
                if temp [i][j] == 0:
                    ba = ba + "0"
                else:
                    if temp [i][j] == self.player:
                        ba = ba + "1"
                    else:
                        ba = ba + "2"

        return (ba, self.player)

    @staticmethod
    def readFromFile (filename):

        inputFile = open (filename, 'r')
        line = inputFile.readline ()
        (size, player) = map (int, line.split (" "))
        board = []

        for _ in range (size):
            line = inputFile.readline ()
            indices = line.split (",")
            int_indices = list (map (int, indices))
            board.append (int_indices)

        for i in range (size):
            for j in range (i):
                t = board [i][j]
                board [i][j] = board [j][i]
                board [j][i] = t

        inputFile.close ()

        state = State (board = board, player = player, size = size)
        return state

    def getFeatures (self, option = 0):

        # size = str (self.size) + " "
        # player = str (self.player) + " "
        
        # board = ""

        if option > 3:
            print ("Option Overflow!!")

        if option == 0:
            temp = []

            for j in range (self.size):
                for i in range (self.size):
                    temp.append (self.player * self.board [i][j])
            return temp

        if option == 1:

            score = 0
            for j in range (self.size):
                for i in range (self.size):
                    if i >= self.size // 2:
                        x = self.size - 1 - i
                    else:
                        x = i

                    if j >= self.size // 2:
                        y = self.size - 1 - j
                    else:
                        y = j

                    if x < y:
                        t = x
                        x = y
                        y = t

                    if x == 0 and y == 0:
                        score += self.board[i][j] * 99
                        continue

                    if x == 1 and y == 1:
                        score -= self.board[i][j] * 24
                        continue

                    if x == 2 and y == 2:
                        score += self.board[i][j] * 7
                        continue

                    if x == 3 and y == 3:
                        continue

                    if x == 1 and y == 0:
                        score -= self.board[i][j] * 8
                        continue

                    if x == 2 and y == 0:
                        score += self.board[i][j] * 8
                        continue

                    if x == 3 and y == 0:
                        score += self.board[i][j] * 6
                        continue

                    if x == 2 and y == 1:
                        score -= self.board[i][j] * 4
                        continue

                    if x == 3 and y == 1:
                        score -= self.board[i][j] * 3
                        continue

                    if x == 3 and y == 2:
                        score += self.board[i][j] * 4
                        continue
            return score

        if option == 2:
            temp = []
            for i in range (self.size):
                column = []
                for j in range (self.size):
                    column.append (self.player * self.board[i][j])

            temp.append (column)
            return temp

        if option == 3:
            temp = []
            plane1 = [] #player
            plane2 = [] #opponent
            plane3 = [] #blank

            for i in range (self.size):
                column1 = []
                column2 = []
                column3 = []
                for j in range (self.size):
                    id = self.player * self.board [i][j]
                    if id == 1:
                        column1.append (1)
                        column2.append (0)
                        column3.append (0)
                        continue
                    if id == -1:
                        column1.append (0)
                        column2.append (1)
                        column3.append (0)
                        continue
                    if id == 0:
                        column1.append (0)
                        column2.append (0)
                        column3.append (1)
                        continue

                plane1.append (column1)
                plane2.append (column2)
                plane3.append (column3)

            temp.append (plane1)
            temp.append (plane2)
            temp.append (plane3)
            return temp

    def checkMoves (self):
        self.findValidMoves ()
        if len (self.validMoves) == 0:
            if self.player == 1:
                self.sendStatus ("No valid moves for black! It is now white's turn")
                self.player = -1
            else:
                self.sendStatus ("No valid moves for white! It is now black's turn")
                self.player = 1

            self.findValidMoves ()
            if len (self.validMoves) == 0:
                self.player = 0
                msg = "The game has ended!!! "

                if (self.bc > self.wc):
                    msg += "Black has won by: "
                else:
                    if (self.wc > self.bc):
                        msg += "White has won by: "
                    else:
                        msg += "It is a tie of: "

                msg += self.count.__str__()
                self.sendStatus (msg)

    #------------------------------------

    def oneDirection (self, x, y, x_change, y_change):
        defaultReturn = (False, [])
        new_x = x + x_change
        new_y = y + y_change

        if new_x < 0 or new_x >= self.size:
            return defaultReturn

        if new_y < 0 or new_y >= self.size:
            return defaultReturn

        if self.player == 1:
            opponent = -1
        else:
            opponent = 1

        if self.board[new_x][new_y] != opponent:
            return defaultReturn

        convert = []
        convert.append ((new_x, new_y))

        new_x += x_change
        new_y += y_change
        while (new_x > -1 and new_y > -1 and new_x < self.size and new_y < self.size):
            if self.board[new_x][new_y] == self.player:
                return (True, convert)
            else:
                if self.board[new_x][new_y] == 0:
                    return (False, [])
            convert.append ((new_x, new_y))
            new_x += x_change
            new_y += y_change

        return (False, [])

    def findValidMoves (self):
        for j in range (self.size):
            for i in range (self.size):
                (valid, converts) = self.isValid (i, j)
                if valid:
                    v = (i, j, converts)
                    self.validMoves.append (v)

    def setAbsBoard (self, absBoard):
        self.absBoard = absBoard
        return

    def sendStatus (self, str):
        if self.absBoard == None:
            print (str)
        else:
            self.absBoard.sendStatus (str)