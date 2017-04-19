# Author: Argens Ng
# Description: This program trains neural network and save it for future use

import os.path
from pathlib import Path

#  --------------- Non-program Specific ----------------  #

# Description: Clears the standard output screen

def clearScreen ():
	print ("\033c")

# Description: Helps unclash a filename so as to prevent overwriting files
# Input:
#	[STR] name: filename
#	[STR] extension: extension
# Output:
#	[STR] suitable filename that is not used

def unclash (name, extension):
	counter = 1

	filename = Path (name + str (counter) + extension)
	while filename.is_file():
		counter += 1
		filename = Path (name + str (counter) + extension)

	return (name + str(counter) + extension)

#  --------------- Program Specific ----------------  #

# Description: Outputs a grid for policy network training
# Input:
#	[INT] x: x index of the move
#	[INT] y: y index of the move
# Output:
#	[(8,8) INT] a 8-by-8 list of list with 1 where the move is played and 0s elsewhere

size = 8
def createOutputGrid (x, y):
	grid = []
	for j in range (size):
		row = []
		for i in range (size):
			if i == x and y == j:
				row.append (1)
			else:
				row.append (0)
		grid.append (row)
	return grid

from othello import State

# Description: Converts a condensed state (Byte/Train_) format into inputs for neural network using feature "Border, Corner and Freemove"
# Input:
#	[STR] line: a line in any of the training sets
# Output:
#	[(5,8,8) INT] a 5-8-8 integer matrix which stores features namely raw board position, padding layer and freemove matrix

def convertToNN (line):
	board = []
	white = []
	black = []
	empty = []
	border = []
	moves = []
	for i in range (size):
		row_white = []
		row_black = []
		row_empty = []
		row_border = []
		row_total = []
		for j in range (size):
			if i == 0 or j == 0 or i == size-1 or j == size-1:
				row_border.append (1)
			else:
				row_border.append (0)
			piece = int (line [i*8+j])
			if piece == 0:
				row_empty.append (1)
				row_black.append (0)
				row_white.append (0)
				row_total.append (0)
			else:
				if piece == 1:
					row_empty.append (0)
					row_black.append (1)
					row_white.append (0)
					row_total.append (1)
				else:
					row_empty.append (0)
					row_black.append (0)
					row_white.append (1)
					row_total.append (-1)

		empty.append (row_empty)
		white.append (row_white)
		black.append (row_black)
		border.append (row_border)
		moves.append (row_total)

	border [0][0] = border [0][size - 1] = border [size - 1][0] = border [size - 1][size - 1] = 4
	border [0][1] = border [1][0] =  border [1][1] = -1
	border [0][size - 2] = border [1][size - 1] =  border [1][size - 2] = -1
	border [size - 2][0] = border [size - 1][1] =  border [size - 2][1] = -1
	border [size - 2][size - 1] = border [size - 1][size - 2] = border [size - 1][size - 1] =  -1
	
	state = State (board = moves)
	for i in range (size):
		for j in range (size):
			moves [i][j] = 0

	for (x, y, _) in state.validMoves:
		moves [x][y] = 1

	e = np.asarray (empty)
	w = np.asarray (white)
	bl = np.asarray (black)
	bd = np.asarray (border)
	mv = np.asarray (moves)

	board.append (e)
	board.append (w)
	board.append (bl)
	board.append (bd)
	board.append (mv)

	# print ("e", e.shape)
	# print ("w", w.shape)
	# print ("bl", bl.shape)

	# b = np.asarray (board)
	# print ("b.shape", b.shape)
	return board
#  --------------- Setting Constants ----------------  #

size = 8
# currentDirectory = os.path.dirname(os.path.abspath(__file__))
import os

currentDirectory = os.getcwd ()
parentDirectory = currentDirectory + "/.."
trainingDirectory = parentDirectory + "/Byte"
trainingFilename = trainingDirectory + "/Train_"

#  --------------- Getting Data ----------------  #

list_X = []
list_move = []
list_winner = []

gameCounter = 0
gameEnd = 1000000000000000000

import numpy as np

# When i = 0, /../Byte/Train_1 is used
i = 0
index = i + 1
filename = trainingFilename + str (index)

f = open (filename, "r")
for line in f:
	if gameCounter > gameEnd:
		break
	gameCounter += 1
	board = convertToNN (line)

	x = int (line [65])
	y = int (line [68])
	if len (line) == 73:
		winner = int (line [70:72])
	else:
		winner = int (line [70])

	list_winner.append (winner)
	list_move.append (createOutputGrid (x, y))
	list_X.append (board)


#  --------------- Visualize ----------------  #

# print (list_X)

# for i in range (len (list_X)):
# 	for a in range (3):
# 		for j in range (size):
# 			print (list_X [i][a][j])
# 		print ("")

# 	for j in range (size):
# 		print (list_move [i][j])

# 	print (list_winner [i])
# 	print ("")

#  --------------- Pre-Processing ----------------  #

import numpy as np

X = np.asarray (list_X)
Y = np.asarray (list_winner)

# Uncomment to train with dense layers
# X = X.reshape (X.shape [0], X.shape [1] * X.shape [2] * X.shape [3])

# Uncomment to train policy network
# Y = np.asarray (list_move)

print ("X_shape", X.shape)
print ("Y_shape", Y.shape)

# Uncomment to train policy network
# Y = Y.reshape (Y.shape[0], Y.shape[1] * Y.shape[2])
# print ("Y_shape", Y.shape)


from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

# print ("X_train", X_train.shape)
# print ("X_test", X_test.shape)
# print ("Y_train", Y_train.shape)
# print ("Y_test", Y_test.shape)

# ----- setting random seed ----- #
seed = 6
np.random.seed (seed)

# ----- hyperparameter ----- #
epoch_ = 500
lr_ = 0.001
momentum_ = 0.9
decay_ = lr_/epoch_
batch_size_ = 5

# ----- Training ----- #

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
from sklearn.metrics import mean_squared_error
from keras.constraints import maxnorm

model = Sequential()
model.add (Convolution2D (32, 3, 3, input_shape = (5, 8, 8), border_mode = "same", activation = "relu", W_constraint = maxnorm(3), dim_ordering = "th"))
model.add (Dropout(0.3))
model.add (Convolution2D (32, 3, 3, border_mode = "same", activation = "relu", W_constraint = maxnorm(3)))
model.add (Dropout(0.3))
model.add (Convolution2D (32, 3, 3, border_mode = "same", activation = "relu", W_constraint = maxnorm(3)))
model.add (Flatten ())
# model.add (Dense (512, input_shape = (256, ), activation = 'relu', W_constraint = maxnorm(2)))
# model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
# model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dropout(0.3))
model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dropout(0.3))
model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dropout(0.3))
model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dropout(0.3))
model.add (Dense (64))
model.add (Dense (1))
sgd = SGD(lr=lr_, momentum=momentum_, decay=decay_, nesterov=False)
# model.compile(loss='categorical_crossentropy', optimizer=sgd)
model.compile(loss='mse', optimizer=sgd)

from keras.callbacks import EarlyStopping

early_stopping = EarlyStopping (monitor = "val_loss", patience = 5, min_delta = 0)
model.fit(X, Y, nb_epoch= epoch_, batch_size=batch_size_, verbose = True, validation_split = 0.1, callbacks = [early_stopping])

filename = unclash ("ValueNetwork/final_network", ".h5")
print (filename)
model.save (filename)

# ===================================================================
# Y_test_pred = model.predict(X_test, verbose=True)

# print (Y_test_pred[0])
