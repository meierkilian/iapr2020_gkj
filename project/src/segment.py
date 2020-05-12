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
        
        ax[3].imshow(edge, cmap=plt.cm.gray, alpha=1)
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
            imgResized = resize(cropCenter(labels == l, obj["pos"], r), outputSize, preserve_range = True)
            try:
                thresh = filters.threshold_otsu(imgResized)
            except Exception as e:
                print("Caugth except {}".format(e))

            obj["img"] = imgResized > thresh
        else :
            obj["img"] = cropCenter(labels == l, obj["pos"], int(outputSize[0]/2))

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