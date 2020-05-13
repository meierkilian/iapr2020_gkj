# conda install av -c conda-forge

import av
import numpy as np
import cv2
from cv2 import cvtColor
import matplotlib.pyplot as plt
from PIL import Image

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
    
    
'''
    function name: video_export
    description: this function outputs a video from a numpy array
    
    input:
    - video_name [string]: name of the exported video
    - imgs [np.array]: array of the modified images
    - png_path [string]: ../relative/path_to/exported/png_files
    - video_path [string]: ../relative/path_to/exported/final_video
    
    output:
    - png pictures of each frame to given png_path
    - final exported video to given video_path
'''
def video_export(video_name, imgs, png_path, video_path):

    #Boucle pour sauver les png.
    i = 0;
    for im in imgs:
        new_im = Image.fromarray(im)
        new_im.save(png_path+"/"+"frame%d.png" % i)
        i = i+1
        
    #Boucle pour sauver la vidéo
    video_name = video_path+"/"+video_name+".avi"
    freq = 2

    images = [img for img in os.listdir(png_path) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(png_path, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, freq, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(png_path, image)))

    cv2.destroyAllWindows()
    video.release()