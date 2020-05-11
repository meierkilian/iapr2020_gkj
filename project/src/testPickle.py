import pickle

# Can be loaded using pickle and the following lines
with open('../data/extractedImg.data', 'rb') as dataFile:
	listObj = pickle.load(dataFile)

print(listObj) 