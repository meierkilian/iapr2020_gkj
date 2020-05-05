# conda install av -c conda-forge

import av
import numpy as np
import matplotlib.pyplot as plt

def video_load(path):
	v = av.open(path)

	imgs = []

	for packet in v.demux():
		for frame in packet.decode():
			#if frame.type == 'video':
			img = frame.to_image()  # PIL/Pillow image
			arr = np.asarray(img)  # numpy array
			imgs.append(arr)

	return imgs

def video_showFrame(img):
	plt.imshow(img)
	plt.axis('off')
	plt.show()