#======================================================================
# IMPORT
#======================================================================

import tarfile
import os
import numpy as np
import matplotlib.pyplot as plt

# NEW ====
import imageio #to load png pictures
import pickle  #to load .data file
import warnings 

# OPEN CV FUNCTIONS
import cv2 # tested using version 4.1.2

# SKIMAGE FUNCTIONS
import skimage.io
from skimage import img_as_ubyte
# from skimage.util import img_as_ubyte
from skimage import filters
from skimage.color import rgb2gray
from skimage.color import rgba2rgb
#from skimage import filters
from skimage.filters import rank
from skimage.filters import median
from skimage.filters import gaussian
from skimage.filters import sobel
from skimage.morphology import disk
from skimage.morphology import erosion
from skimage.morphology import closing
from skimage.morphology import opening
from skimage.morphology import rectangle
from skimage.morphology import area_closing
from skimage.morphology import area_opening
from skimage.draw import rectangle
#from skimage.draw import circle
from skimage.measure import label
from skimage.measure import perimeter
from skimage.segmentation import watershed
from skimage.segmentation import active_contour
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

#if cv2.__version__ != "4.1.2" :
#  warnings.warn("OpenCV currently running version {}, developement version is 4.1.2".format(cv2.__version__))




#======================================================================
# To compute Fourier Descriptor
#======================================================================
ONE_OBJECT_SIGNS = (PLUS, MINUS, TIMES) = 0,2,4  #the index of the + - and * symbols
#not useful anymore



#======================================================================
# To compute Fourier Descriptor
#======================================================================

def get_contour(im, methode = "AC") :
    """
    This function finds a contour in image im using either Active Contour method
    or the OpenCV native findContours function.

    INPUT :
      im : binary image to search the contour in
      methode : specifies methode to be used to search contour, "AC" for active
                contours, "CV2" for OpenCV's findContours(). Default is "AC"
    OUTPUT :
      im : filtered image used for contour search
      snake : order point list of the contour
    """

    # Filtering 
    im = median(im, disk(2))
    im = area_opening(im, 40)

    # Active Contours
    if methode == "AC" :
        # Create a circle used as a seed for active contours
        s = np.linspace(0, 2*np.pi, 300)
        r = 14 + 10*np.sin(s) 
        c = 14 + 10*np.cos(s)
        init = np.array([r, c]).T  #initial snake

        snake = active_contour(im, init, alpha=4, beta=1, gamma=1,
                           w_line = 0, w_edge = 2, coordinates='rc')
        
    # Contour using OpenCV
    elif methode == "CV2" :
        contours, hierarchy = cv2.findContours(im,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        
        c = np.array(contours[0])

        snake = np.array([c[:,0,1],c[:,0,0]]).T
        
    else :
        raise Exception("Unkown methode : {}".format(methode))

    return im, snake
    

def extract_fourier_descriptor(im, methode = "AC"):
    """
    Computes fourier descriptors given a greysclale picture.

    INPUT :
      im : grayscale image to search to contour in
      methode : specifies methode to be used to search contour, see getContour()
                for details
    OUPUT :
      fd : Fourier descriptor coefficients
      snake : order point list of the contour 
      im : filtered image used for contour search
    """
    if type(im[0,0]) == np.bool_: #if picture is binary, convert it to CV_8UC1 type
        im = np.copy(im.astype(np.uint8))
    
    im, snake = get_contour(im, methode)
    
    z = (snake[:,0] + 1j*snake[:,1]) #put the 2D points of the snake in a complex representation
    #off = 0
    #big_z = np.zeros(  off + (z.shape[0] + off)  )
    #big_z[off:z.shape[0]+off] = z
    fd = np.fft.fft(z)

    return fd, snake, im 

def compute_feat_with_fourier_descriptor( pic, feat_n = 1 ):
    """
    Take a CV_8UC1 picture in input and return the n th feature of its Fourier Descriptor which is :
    - Translation invariant (as soon as feat_n is NOT 0)
    - Rotation invariant
    - Sclaled invariant
    """
    descriptor, snake, im= extract_fourier_descriptor(pic, methode = 'CV2')
    module = np.absolute(descriptor) #compute module : rotation invariant
    module/=module[0] #make it sclale invariant
    return module[feat_n],snake, im


#======================================================================
# To compute nb_objects per picture and total area of picture
#======================================================================

def compute_nb_objects(pic):
    """
    It returns the number of objects in the picture pic (background does NOT count as an object)
    It also returns the total area of the objects (i.e. the sum of the area of each object, i.e. the area which is NOT background)
    
    input : The input picture must be a 2D binary numpy array ! 
    """
    if pic.shape[-1] == 4 or pic.shape[-1] == 3:
        print("\n Error : This picture is RGB or RBBA, hence NOT binary. Begone.")
    elif len(pic.shape) ==2: 
        pass
    else:
        print("\n Error : This picture is NOT binary. Begone.")
        
    labels = label(pic)
    return np.amax(labels), np.sum(labels==True)