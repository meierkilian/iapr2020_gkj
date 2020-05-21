#!/usr/bin/python

from video import video_init, video_load, video_showFrame, video_export
from segment import *
from Equation import *
from overlay import *

import sys
import pickle
import argparse
import os

# Global variable containing programme input parameters
# args.input : input video
# args.output : output video
# args.verbose : bool 
args = None

def parsInput() :
	global args
	parser = argparse.ArgumentParser(description='Deliverable for IAPR 2020 project.')

	defaultInput = os.path.join('..','data','robot_parcours_1.avi')
	defaultOuput = os.path.join('..','data','out','robot_parcours_1_out.avi')
	parser.add_argument('-i','--input', default=defaultInput, help='Input video clip, should be .avi')
	parser.add_argument('-o','--output', default=defaultOuput, help='output video clip (path and name), should be .avi')
	parser.add_argument('-v','--verbose', action='store_true', default=False, help='Makes processing verbose and displays intermediate figures (execution stops when a figure is open)')

	args = parser.parse_args()



def saveData(imgs) :
	listListObj = []
	lbl = {0 : '2', 1 : '3', 1 : '3', 2 : '*', 3 : '=', 4 : '7', 5 : '7', 6 : '/', 7 : '2', 8 : '3', 9 : '+'}

	for i in range(6) :
		print("Iteration {}".format(i))
		listObj = segment_getObj(imgs[i])
		print("Nbr obj {}".format(len(listObj)))
		for i in range(len(listObj)) :
			if i in lbl :
				listObj[i]["label"] = lbl[i]
			else :
				listObj[i]["label"] = "N/A"


		listListObj.append(listObj)

		fig, axes = plt.subplots(nrows=3, ncols=int(np.ceil(len(listObj)/3)), figsize=outputSize, \
		sharex=True, sharey=True)

		axes = axes.ravel()
		
		for obj, ax in zip(listObj, axes) :
			ax.imshow(obj["img"], cmap=plt.cm.gray)
			ax.set_title("Center\n {}\n Lbl : {}".format(obj["pos"], obj["label"]))
			
		for a in axes:
			a.axis('off')

		plt.show()

	
	with open('../data/extractedImgBIG_Gray_withOUTSizeAdjust.data', 'wb') as dataFile:
		pickle.dump(listListObj, dataFile)
	# Can be loaded using pickle and the following lines
	# with open('../data/extractedImg.data', 'rb') as dataFile:
	# 	listObj = pickle.load(dataFile)
	# 	


def main():
	parsInput()

	imgsIn = video_load(args.input)

	# saveData(imgsIn)

	
	listObj = segment_getObj(imgsIn[0])
	lbl = {0 : '2', 1 : '3', 1 : '3', 2 : '*', 3 : '=', 4 : '7', 5 : '7', 6 : '/', 7 : '2', 8 : '3', 9 : '+'}
	for i in range(len(listObj)) :
			if i in lbl :
				listObj[i]["label"] = lbl[i]
			else :
				listObj[i]["label"] = "N/A"


	eq = Equation(listObj)
	listPos = segment_getArrow(imgsIn)

	imgsOut = []

	for i,im in enumerate(imgsIn) :
		eqTemp = eq.newRobPos(listPos[i])
		imgTmp = draw_traj_on_pic(im, listPos[0:i+1])
		imgsOut.append(write_text_on_pic(imgTmp, text = eqTemp, text_size = 100, text_pos = (10,10), text_color = 'red', 
                      background_color = 'white', background_dim = [(0,0), (150,30)]))


	video_export(args.output, imgsOut, False)

if __name__ == '__main__':
	main()