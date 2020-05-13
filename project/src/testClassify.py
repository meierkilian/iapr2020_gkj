import pickle
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
from skimage.draw import line

import numpy as np

# Can be loaded using pickle and the following lines
with open('../data/extractedImg.data', 'rb') as dataFile:
	listObj = pickle.load(dataFile)

mask = {}
mask["Times"] = np.zeros((28,28))
mask["Times"][0:28, 13] = -1
mask["Times"][13,0:28] = 1
rr, cc = line(0,0,27,27)
mask["Times"][rr,cc] = 1
rr, cc = line(0,27,27,0)
mask["Times"][rr,cc] = 1

mask["Plus"] = np.array(-mask["Times"])
mask["Plus"][13,0:28] = 1
mask["Plus"][0:28, 13] = 1

mask["Minus"] = np.array(-mask["Times"])
mask["Minus"][0:28, 13] = -1
mask["Minus"][13,0:28] = 1



img = listObj[2]["img"]

r = {}
for m in mask :
	r[m] = np.sum(np.multiply(mask[m], img))#/np.sum(mask[m])

print(r)

print(np.sum(mask["Minus"] != 0))
print(np.sum(mask["Plus"] != 0))
print(np.sum(mask["Times"] != 0))


fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(28,28), \
sharex=True, sharey=True)

axes = axes.ravel()

axes[0].imshow(img, cmap=plt.cm.gray)
axes[1].imshow(img, cmap=plt.cm.gray)
axes[2].imshow(img, cmap=plt.cm.gray)

axes[3].imshow(mask["Minus"], cmap=plt.cm.gray)
axes[4].imshow(mask["Plus"], cmap=plt.cm.gray)
axes[5].imshow(mask["Times"], cmap=plt.cm.gray)

axes[3].set_title("Mask : Minus")
axes[4].set_title("Mask : Plus")
axes[5].set_title("Mask : Times")

axes[6].imshow(np.multiply(mask["Minus"], img), cmap=plt.cm.gray)
axes[7].imshow(np.multiply(mask["Plus"], img), cmap=plt.cm.gray)
axes[8].imshow(np.multiply(mask["Times"], img), cmap=plt.cm.gray)

axes[6].set_title("Score : {}".format(r["Minus"]))
axes[7].set_title("Score : {}".format(r["Plus"]))
axes[8].set_title("Score : {}".format(r["Times"]))

	
for a in axes:
	a.axis('off')

plt.show()