#!/usr/bin/python

import sys
from video import *
from segment import *

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

	segment_getObj(imgs[0])



if __name__ == '__main__':
	main()