from pandac.PandaModules import OdeFixedJoint, Texture, TextureStage, Vec3
from box import Box
from gameObject import GameObject
from vecUtils import entrywiseMult, vecFromList, vecBasic, vecInvert, getNeutralDir

class Tile(Box):

	def __init__(self, brick, color, tileDir, thickness, density, unglueThreshold=None, shatterLimit=None, shatterThreshold=None, noSetup=False):
		if noSetup: return
		
		depth = thickness / 2
		world = brick.world
		parent = brick.parent
		size = entrywiseMult(vecInvert(tileDir), brick.size) + (vecBasic(tileDir) * depth)
		pos = brick.node.getPos() + entrywiseMult(tileDir, brick.size) + (vecFromList(tileDir) * depth)
		self.tileDir = tileDir
		if unglueThreshold == None: unglueThreshold = 5
		if shatterThreshold == None: shatterThreshold = 10
		dir = getNeutralDir()

		Box.__init__(self, world, parent, color, pos, dir, size, density, unglueThreshold, shatterLimit, shatterThreshold)

		self.thickness = thickness
		self.brick = brick
		self.brick.addTile(self)

		# Glue to brick.
		self.glue = OdeFixedJoint(self.world.world)
		self.glue.attachBodies(self.body, brick.body)
		self.glue.set()

		# Adjust collision bitmasks.
		self.geom.setCategoryBits(GameObject.bitmaskTileGlued)
		self.geom.setCollideBits(GameObject.bitmaskAll & ~GameObject.bitmaskBox & ~GameObject.bitmaskTileGlued & ~GameObject.bitmaskTile)

	def make2(self, tile, color, tileDir, pos, size, density, shatterLimit=None, shatterThreshold=None):
		self = Tile(0, 0, 0, 0, 0, noSetup = True)
		world = tile.world
		parent = tile.parent
		self.tileDir = tileDir
		if shatterThreshold == None: shatterThreshold = 10
		dir = getNeutralDir()

		Box.__init__(self, world, parent, color, pos, dir, size, density, shatterLimit, shatterThreshold)

		self.thickness = tile.thickness
		self.brick = tile.brick
		self.glue = None

		# Adjust collision bitmasks.
		self.geom.setCategoryBits(GameObject.bitmaskTile)
		self.geom.setCollideBits(GameObject.bitmaskAll & ~GameObject.bitmaskTileGlued & ~GameObject.bitmaskTile)

		return self

	def applyTexture(self):
		self.texture = loader.loadTexture("media/gray_stone_tile.png")
		self.texture.setWrapU(Texture.WMRepeat)
		self.texture.setWrapV(Texture.WMRepeat)
		self.model.setTexture(self.texture, 1)

		# Calculate and apply texture scale factors.
		sizes = entrywiseMult(vecInvert(self.tileDir), self.size)
		scales = []
		for i in sizes:
			scales.append(i) if i != 0 else None
		self.model.setTexScale(TextureStage.getDefault(), scales[0], scales[1])

	def unglue(self):
		if self.glue != None:
			self.glue.destroy()
			self.glue = None
			self.brick.removeTile(self)
			if DEBUG: self.node.setColorScale(1.0, 1.0, 2.0, 0.5)

		# Adjust collision bitmasks.
		self.geom.setCategoryBits(GameObject.bitmaskDefault)
		self.geom.setCollideBits(GameObject.bitmaskAll)
	
	def destroy(self):
		self.unglue()
		Box.destroy(self)

	def shatter(self, speedMag, speedBase):
		self.destroy()
		taskMgr.add(self.spawnTask, "box-spawn", extraArgs=[speedMag, speedBase])
		return

	def spawnTask(self, speedMag, speedBase):
		w = 1
		size = entrywiseMult(vecInvert(self.tileDir), self.size / (w*2)) + entrywiseMult(vecBasic(self.tileDir), self.size)
		basDir = vecBasic(self.tileDir)
		posBase = self.node.getPos()
		for i in [-w, w]:
			for j in [-w, w]:
				if basDir == Vec3(1,0,0): pos = (posBase[0], posBase[1] + (i * size[1]), posBase[2] + (j * size[2]))
				if basDir == Vec3(0,1,0): pos = (posBase[0] + (i * size[0]), posBase[1], posBase[2] + (j * size[2]))
				if basDir == Vec3(0,0,1): pos = (posBase[0] + (i * size[0]), posBase[1] + (i * size[1]), posBase[2])

				tile = self.make2(self, self.color, self.tileDir, pos, size, self.density, self.shatterLimit - 1, self.shatterThreshold)
				tile.node.setHpr(self.node.getHpr())
				if DEBUG: tile.node.setColorScale(1.0, 1.0, 2.0, 0.5)
				#speed = (speedBase * (1.5 + random())) + (Vec3(i,j,k) * speedMag * (1 + random()))
				#speed = speed / 8.0
				#tile.body.setLinearVel(speed)
				#tile.body.setAngularVel(speedMag * random(), speedMag * random(), speedMag * random())
				taskMgr.add(tile.disableOnStopTask, "tile-disableOnStop")

