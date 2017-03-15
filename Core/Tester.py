size = 8
result = []
# currentDirectory = os.path.dirname(os.path.abspath(__file__))
import os

currentDirectory = os.getcwd ()
parentDirectory = currentDirectory + "/.."
trainingDirectory = parentDirectory + "/Byte"
trainingFilename = trainingDirectory + "/Train_"


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

#  --------------- Getting Filename ----------------  #
# q = "Which training set to use? (Default is 1.)"
# while True:
# 	try:
# 		ans = query (question = q)
# 		if len (ans) == 0:
# 			order = 1
# 			break
# 		order = int (ans)
# 	except ValueError:
# 		continue
# 	else:
# 		break


# Y = Y.reshape (Y.shape[0], Y.shape[1] * Y.shape[2])
# print ("Y_shape", Y.shape)

from keras.objectives import mean_squared_error
from keras.models import load_model
import tensorflow as tf

#-------------------------------------------

def mse (Y_pred, Y):

	Y_pred = Y_pred.reshape (Y_pred.shape [0],)

	s = 0
	c = 0

	for (y, y_pred) in zip (Y_pred, Y):
		c += 1
		t = y - y_pred
		s += t * t

	return s/c

def doTests (X, Y):
	global result

	valueNN = "ValueNetwork/CNN.h5"
	model = load_model (valueNN)
	Y_pred = model.predict(X, verbose=True)
	result.append (("CNN: ", mse (Y_pred, Y)))

	#-------------------------------------------

	valueNN = "ValueNetwork/CNN_deeper.h5"
	model = load_model (valueNN)
	Y_pred = model.predict(X, verbose=True)
	result.append (("CNNDeeper: ", mse (Y_pred, Y)))

	#-------------------------------------------

	valueNN = "ValueNetwork/DropoutCNN.h5"
	model = load_model (valueNN)
	Y_pred = model.predict(X, verbose=True)
	result.append (("DropoutCNN: ", mse (Y_pred, Y)))

	#-------------------------------------------

	X = X.reshape (X.shape [0], X.shape [1] * X.shape [2] * X.shape [3])

	valueNN = "ValueNetwork/deep_simple.h5"
	model = load_model (valueNN)
	Y_pred = model.predict(X, verbose=True)
	result.append (("Deep Simple: ", mse (Y_pred, Y)))

	#-------------------------------------------

	valueNN = "ValueNetwork/deeper.h5"
	model = load_model (valueNN)
	Y_pred = model.predict(X, verbose=True)
	result.append (("Deeper: ", mse (Y_pred, Y)))

for order in range (3):

	filename = trainingFilename + str (order + 1)
	print (filename)

	list_X = []
	list_move = []
	list_winner = []

	gameCounter = 0
	gameEnd = 100000000

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
		# list_move.append (createOutputGrid (x, y))
		list_X.append (board)

	import numpy as np

	X = np.asarray (list_X)
	Y = np.asarray (list_winner)
	# Y = np.asarray (list_move)

	print ("X_shape", X.shape)
	print ("Y_shape", Y.shape)

	result.append ((order+1, "-------------------------------------"))
	doTests (X, Y)

clearScreen ()

for x in result:
	print (x)