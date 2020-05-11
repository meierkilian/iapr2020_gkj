#!/usr/bin/python

import sys
from video import *
from segment import *
import pickle

inPath = ''
outPath = ''


def parsInput():
	global inPath
	global outPath

	if len(sys.argv) == 3 :
		inPath = sys.argv[1]
		outPath = sys.argv[2]
	elif len(sys.argv) == 1 :
		inPath = "../data/robot_parcours_1.avi"
		outPath = "../data/robot_parcours_1_out.avi"
	else :
		raise ValueError("Bad input syntax, use : python3 main.py OR python3 main.py inPath outPath")


def main():
	parsInput()

	imgs = video_load(inPath)

	listObj = segment_getObj(imgs[0])
	listObj[0]["label"] = '2'
	listObj[1]["label"] = '3'
	listObj[2]["label"] = '*'
	listObj[3]["label"] = '='
	listObj[4]["label"] = '7'
	listObj[5]["label"] = '7'
	listObj[6]["label"] = '/'
	listObj[7]["label"] = '2'
	listObj[8]["label"] = '3'
	listObj[9]["label"] = '+'
	
	with open('../data/extractedImg.data', 'wb') as dataFile:
		pickle.dump(listObj, dataFile)
	# Can be loaded using pickle and the following lines
	# with open('../data/extractedImg.data', 'rb') as dataFile:
	# 	listObj = pickle.load(dataFile)
 

if __name__ == '__main__':
	main()