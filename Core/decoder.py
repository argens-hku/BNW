# The operation => column + (10 * row). Ex: a1 = 11, h1 = 18, a8 = 81,
# H8 = 88.

# inputfilename = input ("What is the filename? ")
# outputfilename = "/Users/Argens/Desktop/OB/GameRecord/_RMD copy"
# li = []
# with open(inputfilename, "rb") as f:
# 	byte = f.read(16)
# 	print ("Signature: ", byte)
# 	byte = f.read (8)
# 	while byte:
# 		print ("Match: ", byte)
# 		order = 0
# 		while order < 60:
# 			byte = f.read(1)
# 			i = int.from_bytes(byte, byteorder='big', signed=False)
# 			y = i//10 - 1
# 			x = i%10 - 1
# 			coor = (x, y)
# 			print (order, ": ", coor)
# 			li.append (coor)
# 			order += 1
# 		print ("===========")
# 		byte = f.read (8)
# 		Do stuff with byte.

import os
rootdir = "/Users/Argens/Desktop/Cassio/Database/WThor"
for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		ext = os.path.splitext(file)[-1].lower()
		if ext == ".wtb":
			inputfilename = os.path.join (rootdir, file)
			outputfilename = "/Users/Argens/Desktop/OB/GameRecord/_RMD copy"
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

