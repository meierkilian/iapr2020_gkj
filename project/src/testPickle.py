import pickle

# Can be loaded using pickle and the following lines
with open('../data/extractedImgBIG.data', 'rb') as dataFile:
	listObj = pickle.load(dataFile)

print(len(listObj)) 