#!/usr/bin/python

import sys
from video import *

inPath = ''
outPath = ''


def parsInput():
	global inPath
	global outPath

	if len(sys.argv) != 3:
		raise ValueError("Bad input syntax, use : python3 main.py inPath outPath")
	inPath = sys.argv[1]
	outPath = sys.argv[2]


def main():
	parsInput()

	imgs = video_load(inPath)

	video_showFrame(imgs[20])



if __name__ == '__main__':
	main()