import numpy as np
import cv2
from cv2 import cvtColor
from skimage.filters import threshold_otsu

from video import video_showFrame

def segment_getArrow(video, to_plot):
    
    arrow_pos=np.zeros([42,2])
    i = 0
    for im in video:
        #ranges of y, u, v:
        # Y: 0 - 255
        # U: -128 - 127
        # V: -128 - 127
        img_yuv = cvtColor(im, cv2.COLOR_BGR2YUV);
        img_yuv = img_yuv[:,:,1];
        img_bin = np.zeros([480,720]);
        thresh = threshold_otsu(img_yuv)
        #print(thresh)
        img_bin[np.where(img_yuv>thresh)] = 1
        #video_showFrame(img_bin)
        M = cv2.moments(img_bin);
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        arrow_pos[i,:] = [cX,cY];
        i = i+1

    #print(arrow_pos) 
    if(to_plot ==1):
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
        ax.set_xlim(0,720)
        ax.set_ylim(480,0)
        plt.plot(arrow_pos[:,0], arrow_pos[:,1])
        plt.title("Arrow position")
        plt.show()
        

    return arrow_pos