import os.path
from pathlib import Path

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

def unclash (name, extension):
	counter = 1

	filename = Path (name + str (counter) + extension)
	while filename.is_file():
		counter += 1
		filename = Path (name + str (counter) + extension)

	return (name + str(counter) + extension)

#  --------------- Program Specific ----------------  #

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
			piece = int (line [i*8+j])
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
#  --------------- Setting Constants ----------------  #

size = 8
# currentDirectory = os.path.dirname(os.path.abspath(__file__))
import os

currentDirectory = os.getcwd ()
parentDirectory = currentDirectory + "/.."
trainingDirectory = parentDirectory + "/Byte"
trainingFilename = trainingDirectory + "/Train_"

#  --------------- Getting Filename ----------------  #
q = "Which training set to use? (Default is 1.)"
while True:
	try:
		ans = query (question = q)
		if len (ans) == 0:
			order = 1
			break
		order = int (ans)
	except ValueError:
		continue
	else:
		break
filename = trainingFilename + str (order)
print (filename)

#  --------------- Getting Data ----------------  #

list_X = []
list_move = []
list_winner = []

gameCounter = 0
gameEnd = 1000000000000000000

import numpy as np

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
# X = X.reshape (X.shape [0], X.shape [1] * X.shape [2] * X.shape [3])
# Y = np.asarray (list_move)

print ("X_shape", X.shape)
# print ("Y_shape", Y.shape)

# Y = Y.reshape (Y.shape[0], Y.shape[1] * Y.shape[2])
print ("Y_shape", Y.shape)


from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

print ("X_train", X_train.shape)
print ("X_test", X_test.shape)
print ("Y_train", Y_train.shape)
print ("Y_test", Y_test.shape)

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
model.add (Convolution2D (32, 3, 3, input_shape = (4, 8, 8), border_mode = "same", activation = "relu", W_constraint = maxnorm(3), dim_ordering = "th"))
model.add (Dropout(0.3))
model.add (Convolution2D (32, 3, 3, border_mode = "same", activation = "relu", W_constraint = maxnorm(3)))
model.add (Dropout(0.3))
model.add (Convolution2D (32, 3, 3, border_mode = "same", activation = "relu", W_constraint = maxnorm(3)))
model.add (Flatten ())
# model.add (Dense (512, input_shape = (256, ), activation = 'relu', W_constraint = maxnorm(2)))
# model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
# model.add (Dense (512, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dense (1024, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dropout(0.3))
model.add (Dense (1024, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dropout(0.3))
model.add (Dense (1024, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dropout(0.3))
model.add (Dense (1024, activation = 'relu', W_constraint = maxnorm(2)))
model.add (Dropout(0.3))
model.add (Dense (64))
model.add (Dense (1))
sgd = SGD(lr=lr_, momentum=momentum_, decay=decay_, nesterov=False)
# model.compile(loss='categorical_crossentropy', optimizer=sgd)
model.compile(loss='mse', optimizer=sgd)

from keras.callbacks import EarlyStopping

early_stopping = EarlyStopping (monitor = "val_loss", patience = 5, min_delta = 0)
model.fit(X_train, Y_train, nb_epoch= epoch_, batch_size=batch_size_, verbose = True, validation_split = 0.1, callbacks = [early_stopping])

filename = unclash ("ValueNetwork/value_network", ".h5")
print (filename)
model.save (filename)

Y_test_pred = model.predict(X_test, verbose=True)

print (Y_test_pred[0])
