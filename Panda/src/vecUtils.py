from pandac.PandaModules import Vec3, Vec4

def getNeutralDir():
	return (0, 1, 0)

def vecToList(vec):
	list = []
	for i in vec:
		list.append(i)
	return list

def vecFromList(list):
	if len(list) == 3:
		return Vec3(*list)
	else:
		return Vec4(*list)

def vecBasic(vec):
	list = []
	for i in vec:
		list.append(0 if i == 0 else 1)
	return vecFromList(list)

def vecInvert(vec):
	list = []
	for i in vec:
		list.append(1 if i == 0 else 0)
	return vecFromList(list)

def average(vec):
	sum = 0
	for item in vec:
		sum += item
	return float(sum) / len(vec)

def entrywiseMult(vec1, vec2):
	list = []
	for i in range(len(vec1)):
		list.append(vec1[i] * vec2[i])
	return vecFromList(list)
