a = 1

def init(glob_a):
	global a 
	a = glob_a

def func():
	print("in func a = {}".format(a))