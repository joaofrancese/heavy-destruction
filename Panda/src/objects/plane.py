from pandac.PandaModules import Point2, Vec4, CardMaker, OdePlaneGeom, TextureStage, Texture

def makeVec4FromPointAndNormal(point, normal):
	return Vec4(-normal[0],
				-normal[1],
				-normal[2],
				-normal[0]*point[0] -normal[1]*point[1] -normal[2]*point[2])

class Plane():
	def __init__(self, world, parent, pos, dir, width, height, color, name, textureFilename=None):
		self.node = parent.attachNewNode("")
		self.node.setPos(*pos)
		self.node.lookAt(self.node, *dir)
		self.name = name

		divisions = 1
		for i in range(divisions):
			for j in range(divisions):
				self.makeCard(color, width, height, i, j, divisions)

		if textureFilename == None:
			self.texture = None
		else:
			self.texture = loader.loadTexture(textureFilename)
			self.texture.setWrapU(Texture.WMRepeat)
			self.texture.setWrapV(Texture.WMRepeat)
			self.node.setTexture(self.texture)
			self.node.setTexScale(TextureStage.getDefault(), 0.5, 0.5)

		self.geom = OdePlaneGeom(world.space, makeVec4FromPointAndNormal(pos, dir))
		world.space.setSurfaceType(self.geom, world.surfaces["plane"])

	def makeCard(self, color, width, height, i, j, divisions):
		divisions = float(divisions)
		x = i / divisions
		y = j / divisions
		d = 1 / divisions

		card = CardMaker("wall")
		card.setColor(*color)
		card.setFrame(width*(x*2-1), width*((x+d)*2-1), height*(y*2-1), height*((y+d)*2-1))
		card.setUvRange(Point2(width*x, height*y), Point2(width*(x+d), height*(y+d)))
		card.setHasUvs(True)
		card.setHasNormals(True)
		node = self.node.attachNewNode(card.generate())
		#if  (i + j) % 2 == 0:
		#	card.setFrame(height*(y*2-1), height*((y+d)*2-1), width*(x*2-1), width*((x+d)*2-1))
		#	card.setUvRange(Point2(width*(x+d), height*(y+d)), Point2(width*x, height*y))
		#	node = self.node.attachNewNode(card.generate())
		#	node.setHpr(0, 0, 90)
		#	#node.setPos(width*(1-(i%2)*2)*2/divisions, 0, 0)
