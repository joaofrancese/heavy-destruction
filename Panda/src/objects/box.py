from pandac.PandaModules import OdeBody, OdeMass, OdeBoxGeom, Vec3, Texture, TextureStage
from gameObject import GameObject
from cement import Cement
from random import random
from pandaUtils import makeVec4Color
from vecUtils import vecFromList, getNeutralDir
#more imports at the end of the file

class Box(GameObject):
	disableGracePeriod = 20
	
	def __init__(self, world, parent, color, pos, dir, size, density, unglueThreshold=None, shatterLimit=None, shatterThreshold=None):
		GameObject.__init__(self, world)

		if unglueThreshold == None: unglueThreshold = 20
		if shatterLimit == None: shatterLimit = 0
		if shatterThreshold == None: shatterThreshold = 30

		self.size = size
		self.density = density
		self.dir = dir
		self.parent = parent
		self.color = color = makeVec4Color(color)
		
		self.node = parent.attachNewNode("")
		self.node.setPos(*pos)
		self.node.setColorScale(color)
		self.node.setScale(*size)
		self.node.lookAt(self.node, *dir)

		self.model = loader.loadModel("models/box.egg")
		self.model.reparentTo(self.node)
		self.model.setScale(2.0)
		self.model.setPos(-1.0, -1.0, -1.0)

		self.applyTexture()

		self.mass = OdeMass()
		self.mass.setBox(density, Vec3(*size) * 2)
		self.body = OdeBody(world.world)
		self.body.setMass(self.mass)
		self.body.setPosition(self.node.getPos())
		self.body.setQuaternion(self.node.getQuat())
		self.body.setData(self)
		self.geom = OdeBoxGeom(world.space, Vec3(*size) * 2.0)
		self.geom.setBody(self.body)
		world.space.setSurfaceType(self.geom, world.surfaces["box"])

		# Adjust collision bitmasks.
		self.geom.setCategoryBits(GameObject.bitmaskBox)
		self.geom.setCollideBits(GameObject.bitmaskAll & ~GameObject.bitmaskTileGlued)

		# Tile, cement and shatter variables.
		self.tiles = []
		self.cements = []
		self.disableCount = 0
		self.unglueThreshold = unglueThreshold
		self.shatterLimit = shatterLimit
		self.shatterThreshold = shatterThreshold

	def applyTexture(self):
		self.texture = loader.loadTexture("media/brick_wall.tga")
		self.texture.setWrapU(Texture.WMRepeat)
		self.texture.setWrapV(Texture.WMRepeat)
		self.model.setTexture(self.texture, 1)
		self.model.setTexScale(TextureStage.getDefault(), max(self.size[0], self.size[1]), self.size[2])

	def addTile(self, tile):
		if tile not in self.tiles:
			self.tiles.append(tile)

	def removeTile(self, tile):
		if tile in self.tiles:
			self.tiles.remove(tile)

	def addCement(self, cement):
		if cement not in self.cements:
			self.cements.append(cement)

	def removeCement(self, cement):
		if cement in self.cements:
			self.cements.remove(cement)

	def destroy(self):
		for tile in self.tiles:
			tile.unglue()
		for cement in self.cements:
			cement.destroy()
		GameObject.destroy(self)

	def makeTiles(self, xNeg=False, xPos=False, yNeg=False, yPos=False, zNeg=False, zPos=False, thickness=0.1, unglueThreshold=None, shatterLimit=None, shatterThreshold=None):
		if xNeg: Tile(self, self.color, (-1,0,0), thickness, self.density, unglueThreshold, shatterLimit, shatterThreshold)
		if xPos: Tile(self, self.color, ( 1,0,0), thickness, self.density, unglueThreshold, shatterLimit, shatterThreshold)
		if yNeg: Tile(self, self.color, (0,-1,0), thickness, self.density, unglueThreshold, shatterLimit, shatterThreshold)
		if yPos: Tile(self, self.color, (0, 1,0), thickness, self.density, unglueThreshold, shatterLimit, shatterThreshold)
		if zNeg: Tile(self, self.color, (0,0,-1), thickness, self.density, unglueThreshold, shatterLimit, shatterThreshold)
		if zPos: Tile(self, self.color, (0,0, 1), thickness, self.density, unglueThreshold, shatterLimit, shatterThreshold)

	def onCollision(self, otherBody, entry):
		if otherBody.isEmpty():
			return
		self.disableCount = 0
		speed = otherBody.getData().body.getLinearVel()
		#if otherBody.getData().__class__ == Bullet: print speed.length(), self.shatterThreshold, self.shatterLimit #######
		if self.active and speed.length() >= self.shatterThreshold and self.shatterLimit > 0:
			adj = otherBody.getData().body.getMass().getMagnitude() / self.body.getMass().getMagnitude()
			speedMag = speed.length() * adj
			speedBase = ((speed * adj) + (self.body.getLinearVel() * 2) / 3)
			self.shatter(speedMag, speedBase)

	def shatter(self, speedMag, speedBase):
		#print 'box shatter' #########
		self.destroy()
		taskMgr.add(self.spawnTask, "box-spawn", extraArgs=[speedMag, speedBase])

		# Graphic (camera shake) and sound effects
		self.world.game.cameraHandler.shake((0,0,2), 0.1)
		sound = base.loader.loadSfx("media/shatter.wav")
		sound.setVolume(1.5)
		sound.play()

	def spawnTask(self, speedMag, speedBase):
		pos = self.node.getPos()
		size = Vec3(self.size) / 2
		w = 1
		for i in [-w, w]:
			for j in [-w, w]:
				for k in [-w, w]:
					box = Box(self.world, self.parent, self.color,
						(pos[0] + (i * size[0]), pos[1] + (j * size[1]), pos[2] + (k * size[2])),
						self.dir, size, self.density, self.unglueThreshold, self.shatterLimit - 1, self.shatterThreshold * 1)
					speed = (speedBase * (1.5 + random())) + (Vec3(i,j,k) * speedMag * (1 + random()))
					speed = speed / 2.0
					box.body.setLinearVel(speed)
					box.body.setAngularVel(speedMag * random(), speedMag * random(), speedMag * random())
					taskMgr.add(box.disableOnStopTask, "box-disableOnStop")

	def disableOnStopTask(self, task):
		if self.body.getLinearVel().length() > 0.1 or self.body.getAngularVel().length() > 0.1:
			self.disableCount = 0
			return task.cont
		elif self.disableCount < Box.disableGracePeriod:
			self.disableCount += 1
			return task.cont
		else:
			self.visibleAfterDestroy = True
			if DEBUG: self.node.setColorScale(1.0, 2.0, 1.0, 0.5)
			self.destroy()
			return task.done

def createWall(world, parent, color, pos, size, density, quantity, shatterLimit=None, tileThickness=None, tileShatterLimit=None):
	boxes = []
	diffBase = vecFromList(size) * 2
	dir = getNeutralDir()
	for i in range(quantity[0]):
		boxes.append([])
		for j in range(quantity[1]):
			boxes[i].append([])
			for k in range(quantity[2]):
				diff = Vec3(diffBase[0]*i, diffBase[1]*j, diffBase[2]*k)
				box = Box(world, parent, color, Vec3(*pos) + diff, dir, size, density, shatterLimit=shatterLimit)
				boxes[i][j].append(box)
				if tileThickness != None:
					box.makeTiles(	xNeg = i == 0, xPos = i == quantity[0] - 1,
									yNeg = j == 0, yPos = j == quantity[1] - 1,
									zNeg = False,  zPos = k == quantity[2] - 1,
									thickness = tileThickness, shatterLimit = tileShatterLimit)
				if i > 0: Cement(boxes[i][j][k], boxes[i-1][j][k])
				if j > 0: Cement(boxes[i][j][k], boxes[i][j-1][k])
				if k > 0: Cement(boxes[i][j][k], boxes[i][j][k-1])
				if k == 0: Cement(boxes[i][k][k], None)
				
	return boxes

from tile import Tile
