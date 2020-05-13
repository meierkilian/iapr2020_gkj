
def classify_getDigit(img, label):
	return label


def classify_getSymbol( pic, path_classifier='symbol_classifier_V1.pk' ):
	"""
	Given a picture which represents a symbol, return its symbol.
	
	=> Input :    °)  pic :  - a 2D numpy binary picture of shape (28 x 28)
	                         - True = an element of the symbol
							 - False = background
				  °)  path_classifier :  - the path where the classifier file is stored
				                         - Note : the path must also include the name of the classifier file
	
	=> Output :   °)  return a string caracter, either '+', '-', '*', '=', ':'
	"""
  lda_model = pickle.load(open(path_classifier,'rb'))
  features = np.zeros((1,3))
  bend_the_knee_to_the_chosen_fourier_descriptor_feature = 5 #Heretics will burn.
  features[0,0:2] = compute_nb_objects(pic)
  features[0,2],_,_ = compute_feat_with_fourier_descriptor(pic, feat_n = bend_the_knee_to_the_chosen_fourier_descriptor_feature)
  features[0,2]*=300 #lazy wait to not normalize the data
  pred = lda_model.predict(features[:,1:3])

  if features[0,0] == 3:   # 3 points in object => Divide symbol
    return ':'
  elif features[0,0] ==2:  # 2 points in object => '=' symbol
    return '='
  elif pred[0] == 1:       # 1 point in object => use lda classifier to decide between + , - ,* symbols
    return '*'
  elif pred[0] == 2:
    return '+'
  elif pred[0] == 3:
    return '-'
  else:
    return 'STH WENT WRONG'
