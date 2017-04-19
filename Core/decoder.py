# This snippet transforms .wtb files storing Othello match record into human readable formats
# By human readable format, we mean standard Othello encoding, eg. c4e3f6e6f5c5f4g6f7d3f3g5g4e7d6h3

import os
rootdir = "LOCATION OF THE WTHOR FILE"
for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		ext = os.path.splitext(file)[-1].lower()
		if ext == ".wtb":
			inputfilename = os.path.join (rootdir, file)
			outputfilename = "ENTER SUITABLE OUTPUT FILENAME HERE"
			li = []
			with open(inputfilename, "rb") as f:
				with open (outputfilename, "a") as outputFile:
					byte = f.read(16)
					print ("Signature: ", byte)
					byte = f.read (8)
					while byte:
						print ("Match: ", byte)
						order = 0
						string = ""
						while order < 60:
							byte = f.read(1)
							i = int.from_bytes(byte, byteorder='big', signed=False)
							y = i//10 - 1
							x = i%10 - 1
							string = string + chr (x+97)
							string = string + chr (y+49)
							coor = (x, y)
							print (order, ": ", coor)
							li.append (coor)
							order += 1
						print ("===========")
						byte = f.read (8)
						outputFile.write (string)
						outputFile.write ("\n")
						outputFile.write ("\n")

