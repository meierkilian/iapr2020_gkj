import matplotlib.pyplot as plt

from skimage import morphology
from skimage.segmentation import watershed
from skimage.draw import rectangle
from skimage.draw import circle
from skimage.measure import label
from skimage import color 
from skimage import filters
from skimage import feature
from skimage.util import crop
from skimage.transform import resize

import numpy as np
import cv2
from cv2 import cvtColor

# TODO
# im_gray = color.rgb2yuv(img)[:,:,1] NOTE red arrow is super nicely visible in this color space
# increase border maybe ?
# resize only using filling and no interpolation

# PARAMATER LIST
# 
# Max distance objects can be appart to be considered as belonging to the same symbol
maxDist = 40
# 
# Max/Min size an object is allowed to be to be considered as a symbol
maxSize = 300
minSize = 40
#
# Black border to add around a symbol, if object has size r then extracted image has size int(r*border)
border = 1.2
#
# Shape of desired output images in pixels
outputSize = (28,28)
#
# If True all the symbols are rescaled to match outputSize, if False the images are cropped directly to outputSize,
# this may result in different scale or symbol beeing outside of the image.
adjustSize = False
# 
# Background marker offset and extent notes the position and size of the marker disignating the brackground
bgmOffset = (0, 0)
bgmExtent = (20, 20)
#
# If True intermediate images are displayed
verbose = False
#
# Radius or red arrow (TODO estimate this param)
arrowRad = 70

def getObjCenter(img) :
    x = []
    y = []
    for i in range(img.shape[0]) :
        for j in range(img.shape[1]) :
            if img[i,j] :
                x.append(i)
                y.append(j)

    meanX = np.round(np.average(x))
    meanY = np.round(np.average(y))
    return (meanX, meanY)


def getObjRadius(img, center) :
    dmax = 0
    for i in range(0,img.shape[0]) :
        for j in range(0, img.shape[1]) :
            if img[i,j] :
                d = np.linalg.norm(np.subtract((i,j), center))
                if d > dmax :
                    dmax = d
    return dmax


def cropCenter(img, center, radius) :
    cropLim = (np.clip((center[0] - radius, img.shape[0] - center[0] - radius), 0, img.shape[0]), \
                np.clip((center[1] - radius, img.shape[1] - center[1] - radius), 0, img.shape[1]))
    return crop(img, cropLim, copy = True)


def segment_getObj(img) :

    # convert to grayscale
    im_gray = color.rgb2gray(img)

    
    # First marker label approximation 
    thresh = filters.threshold_otsu(im_gray)
    markers = im_bin = im_gray < thresh
    markers = morphology.opening(im_bin*255, selem=morphology.disk(1)) # removes some false positives, in particular table edge
    markers = label(markers)

    
    # Merge labels which are close to each other 
    objMeanPos = {}
    for i in range(1,np.max(markers)+1) :
        objMeanPos[i] = getObjCenter(markers == i)

    prevMarkers = np.array(markers)

    for i in range(1, np.max(np.max(markers))+1) :
        for j in range(i, np.max(np.max(markers))+1) :
            if np.linalg.norm(np.subtract(objMeanPos[i], objMeanPos[j])) < maxDist :
                markers[markers == j] = i

    while (prevMarkers != markers).any() :
        prevMarkers = np.array(markers)
        for i in range(1, np.max(np.max(markers))+1) :
            for j in range(i, np.max(np.max(markers))+1) :
                if np.linalg.norm(np.subtract(objMeanPos[i], objMeanPos[j])) < maxDist :
                    markers[markers == j] = i        


    # Removes ojects that are to big or to small
    objSize = {}
    for i in range(1,np.max(markers)+1) :
        objSize[i] = np.sum(markers==i)
        if objSize[i] > maxSize or objSize[i] < minSize:
            markers[markers == i] = 0

    # Removes arrow related objects
    arrowPos = segment_getArrow([img])[0].astype(int)
    for i in range(-arrowRad, arrowRad) :
        for j in range(-arrowRad, arrowRad) :
            x = np.clip(arrowPos[0] + i, 0, img.shape[0]-1)
            y = np.clip(arrowPos[1] + j, 0, img.shape[1]-1)
            markers[x,y] = 0


    # Adds label for background 
    markers = markers*2 # makes sure that label 1 is available for background marker
    rr, cc = rectangle(bgmOffset, extent=bgmExtent, shape=markers.shape)
    markers[rr,cc] = 1    
    

    # Perform the watershed
    #edge = feature.canny(im_gray, sigma=.5)
    edge = filters.sobel(im_gray)
    labels = watershed(edge, markers)    
    
    if verbose :
        # display results
        fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(16, 8),
                                 sharex=True, sharey=True)
        ax = axes.ravel()

        ax[0].imshow(img)
        ax[0].set_title("Original")

        ax[1].imshow(markers, cmap=plt.cm.nipy_spectral, alpha=1)
        ax[1].set_title("Markers")

        ax[2].imshow(labels, cmap=plt.cm.nipy_spectral, alpha=1)
        ax[2].set_title("Segmented")
        
        ax[3].imshow(im_gray, cmap=plt.cm.gray, alpha=1)
        ax[3].set_title("Other")
        

        for a in axes:
            a.axis('off')

        fig.tight_layout()
        plt.show()

    # Extract symbol list from original image
    listObj = []
    for l in np.unique(labels) :
        if l == 1 :
            continue ## Ignoring background

        obj = {}
        obj["pos"] = getObjCenter(labels == l)
        if adjustSize :
            r = int(np.round(getObjRadius(labels == l, obj["pos"]))*border)
            imgResized = resize(cropCenter(np.multiply(labels == l, 1 - im_gray), obj["pos"], r), outputSize, preserve_range = True)
            try:
                thresh = filters.threshold_otsu(imgResized)
            except Exception as e:
                print("Caugth except {}".format(e))

            obj["img"] = imgResized > thresh
            # obj["img"] = imgResized
        else :
            imgResized = cropCenter(np.multiply(labels == l, 1 - im_gray), obj["pos"], int(outputSize[0]/2))
            try:
                thresh = filters.threshold_otsu(imgResized)
            except Exception as e:
                print("Caugth except {}".format(e))

            obj["img"] = imgResized > thresh

        listObj.append(obj)

    

    if verbose :
        fig, axes = plt.subplots(nrows=3, ncols=int(np.ceil(len(listObj)/3)), figsize=outputSize, \
        sharex=True, sharey=True)

        axes = axes.ravel()
        
        for obj, ax in zip(listObj, axes) :
            ax.imshow(obj["img"], cmap=plt.cm.gray)
            ax.set_title("Center\n {}".format(obj["pos"]))

        for a in axes:
            a.axis('off')

        plt.show()

    return listObj


def segment_getArrow(video):
    
    arrow_pos=np.zeros((len(video),2))
    i = 0
    thr_min_2 = 0;
    thr_min_1 = 0;
    for im in video:
        #ranges of y, u, v:
        # Y: 0 - 255
        # U: -128 - 127
        # V: -128 - 127
        img_yuv = cvtColor(im, cv2.COLOR_BGR2YUV);
        img_yuv = img_yuv[:,:,1];
        img_bin = np.zeros(video[0][:,:,0].shape);
        
        #selection of threshold with redundancy
        if i==0:
            thr_min_2 = thr_min_1 = thresh = threshold_otsu(img_yuv);
        else:
            thr_min_2 = thr_min_1;
            thr_min_1 = thresh;
            thr_mean = np.mean([thr_min_2, thr_min_1]);
            thresh = threshold_otsu(img_yuv);
            if abs(thresh-thr_mean)>5: #5 = empirically chosen threshold
                thresh = thr_mean;
        
        #print(thresh)
        img_bin[np.where(img_yuv>thresh)] = 1

        M = cv2.moments(img_bin);
        cY = int(M["m10"] / M["m00"])
        cX = int(M["m01"] / M["m00"])
        arrow_pos[i,:] = [cX,cY];
        i = i+1

        # fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(16, 8),
        #                          sharex=True, sharey=True)
        # ax = axes.ravel()

        # ax[0].imshow(im)
        # ax[0].set_title("Original")

        # ax[1].imshow(img_yuv, cmap=plt.cm.gray, alpha=1)
        # ax[1].set_title("YUV")

        # ax[2].imshow(img_bin, cmap=plt.cm.gray, alpha=1)
        # ax[2].set_title("Bin t = {}".format(thresh))
        
        # ax[3].imshow(im, alpha=1)
        # ax[3].set_title("Other")
        

        # for a in axes:
        #     a.axis('off')

        # fig.tight_layout()
        # plt.show()


    #print(arrow_pos) 
    if verbose :
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
        ax.set_xlim(0,720)
        ax.set_ylim(480,0)
        plt.imshow(video[0])
        plt.scatter(arrow_pos[:,1], arrow_pos[:,0])
        plt.title("Arrow position")
        plt.show()
        

    return arrow_pos

