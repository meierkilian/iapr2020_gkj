from Equation import *
import numpy as np

listObj = []

obj = {}
obj["pos"] = (0,0)
obj["img"] = np.zeros((28,28))

listObj.append(obj)
listObj.append(obj)


eq = Equation(listObj)

print(eq.newRobPos((20,20)))

print(eq.newRobPos((200,200)))
print(eq.newRobPos((20,20)))
