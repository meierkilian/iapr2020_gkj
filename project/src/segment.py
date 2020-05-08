import matplotlib.pyplot as plt

from skimage import morphology
from skimage.segmentation import watershed
from skimage.draw import rectangle
from skimage.draw import circle
from skimage.measure import label
from skimage import color 
from skimage import filters
from skimage.util import img_as_ubyte
from skimage import feature

import numpy as np


# im_gray = color.rgb2yuv(img)[:,:,2] NOTE red arrow is super nicely visible in this color space


def getObjCenter(img, label):
    x = []
    y = []
    for i in range(img.shape[0]) :
        for j in range(img.shape[1]) :
            if img[i,j] == label :
                x.append(i)
                y.append(j)

    meanX = np.round(np.average(x))
    meanY = np.round(np.average(y))
    return (meanX, meanY)


def segment_getObj(img) :

    # convert to grayscale
    im_gray = color.rgb2gray(img)

    
    # First marker label approximation 
    thresh = filters.threshold_otsu(im_gray)
    markers = im_bin = im_gray < thresh
    markers = morphology.opening(im_bin*255, selem=morphology.disk(1)) # removes some false positives, in particular table edge
    markers = label(markers)

    
    # Merge labels which are close to each other 
    maxDist = 60 ### PARAM HERE !!!
    objMeanPos = {}
    for i in range(1,np.max(markers)+1) :
        objMeanPos[i] = getObjCenter(markers, i)

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


    # Removes ojects that are to big 
    maxSize = 300 ### PARAM HERE !!!
    objSize = {}
    for i in range(1,np.max(markers)+1) :
        objSize[i] = np.sum(markers==i)
        if objSize[i] > maxSize :
            markers[markers == i] = 0


    # Adds label for background 
    markers = markers*2 # makes sure that label 1 is available for background marker
    rr, cc = rectangle((0,0), extent=(20,20), shape=markers.shape) ### PARAM HERE !
    markers[rr,cc] = 1    
    

    # Perform the watershed
    #edge = feature.canny(im_gray, sigma=.5)
    edge = filters.sobel(im_gray)
    labels = watershed(edge, markers)    
    

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
    
    ax[3].imshow(edge, cmap=plt.cm.gray, alpha=1)
    ax[3].set_title("Other")
    

    for a in ax:
        a.axis('off')

    fig.tight_layout()
    plt.show()