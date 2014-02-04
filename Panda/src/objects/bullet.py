from pandac.PandaModules import OdeBody, OdeMass, OdeCylinderGeom, TransparencyAttrib, Vec3
from gameObject import GameObject
from pandaUtils import makeVec4Color

class Bullet(GameObject):
	lifetime = 120.0

	def __init__(self, world, parent, color, pos, dir, radius, density, posParent=None):
		GameObject.__init__(self, world)

		self.color = makeVec4Color(color)
		self.scale = radius
		self.collisionCount = 0

		diameter = 2 * radius
		length = 1.815 * diameter

		self.node = parent.attachNewNode("")
		if posParent == None:
			self.node.setPos(*pos)
		else:
			self.node.setPos(posParent, *pos)
		self.node.setColorScale(self.color)
		self.node.setTransparency(TransparencyAttrib.MAlpha)
		self.node.setScale(radius)
		self.node.lookAt(self.node, *dir)
		self.node.setHpr(self.node.getHpr() + Vec3(0, 270, 0))

		self.model = loader.loadModel("models/bullet.egg")
		self.model.reparentTo(self.node)
		self.model.setPos(-0.1, -0.1, 0.15)
		self.model.setScale(0.4)

		self.mass = OdeMass()
		self.mass.setCylinder(density, 3, radius, length)
		self.body = OdeBody(world.world)
		self.body.setMass(self.mass)
		self.body.setPosition(self.node.getPos())
		self.body.setQuaternion(self.node.getQuat())
		self.body.setData(self)
		self.body.setGravityMode(False)
		self.geom = OdeCylinderGeom(world.space, radius, length)
		self.geom.setBody(self.body)
		world.space.setSurfaceType(self.geom, world.surfaces["bullet"])

		# Adjust collision bitmasks.
		self.geom.setCategoryBits(GameObject.bitmaskBullet)
		self.geom.setCollideBits(GameObject.bitmaskAll & ~GameObject.bitmaskCharacter)

		# Keep the bullet hidden for a split second so it doesn't appear too close to the camera.
		self.node.hide()
		taskMgr.doMethodLater(0.1, self.showTask, 'show-bullet')

	def onCollision(self, otherBody, entry):
		self.body.setGravityMode(True)

		# Dissipate energy based on collision impact.
		factor = 1.0 - (min(entry.getContactGeom(0).getDepth(), 0.8) * 0.7)
		factor = min(factor, 0.98)
		base.taskMgr.doMethodLater(0.05, self.dissipateTask, "bullet-dissipate", extraArgs=[factor])
		
		# Reduce the lifespan.
		self.collisionCount += 1
		if self.collisionCount == 25:
			self.life = Bullet.lifetime
			taskMgr.add(self.fadeTask, "bullet-fade")
				
	def dissipateTask(self, factor):
		self.dissipate(factor)

	def fadeTask(self, task):
		if self.life > 0:
			self.life -= 1
			self.node.setAlphaScale(4.0 * self.life / Bullet.lifetime)
			return task.cont
		else:
			self.destroy()
			return task.done

	def showTask(self, task):
		if self.node != None:
			self.node.show()
