from pandac.PandaModules import OdeBody, OdeMass, OdeBoxGeom, Vec3, Point3

from objects.gameObject import GameObject
from pandaUtils import SoundWrapper, sign


class Character(GameObject):	
	def __init__(self, world):
		GameObject.__init__(self, world)

		# Set the speed parameters
		self.vel = Vec3(0, 0, 0)
		self.strafespeed = 20.0
		self.forwardspeed = 32.0
		self.backspeed = 24.0
		self.jumpspeed = 20
		self.wasJumping = False

		# Set character dimensions
		self.size = (4.0, 3.0, 10.0)
		self.eyeHeight = 9.0
		self.offset = Point3(0, 0, self.eyeHeight - (self.size[2]/2))

		# Create character node
		self.node = base.render.attachNewNode("character")
		self.node.setPos(0, 0, self.eyeHeight)
		self.node.lookAt(0, 1, self.eyeHeight)

		# Create physics representation
		self.mass = OdeMass()
		self.mass.setBox(50, *self.size)
		self.body = OdeBody(world.world)
		self.body.setMass(self.mass)
		self.updatePhysicsFromPos()
		self.body.setData(self)
		self.geom = OdeBoxGeom(world.space, Vec3(*self.size))
		self.geom.setBody(self.body)
		world.space.setSurfaceType(self.geom, world.surfaces["box"])

		# Adjust collision bitmasks.
		self.geom.setCategoryBits(GameObject.bitmaskCharacter)
		self.geom.setCollideBits(GameObject.bitmaskAll & ~GameObject.bitmaskBullet)

		# Setup event handling
		self.keys = [0, 0, 0, 0, 0]
		self.setupKeys()
		base.taskMgr.add(self.moveTask, "character-move")

		# Create footsteps sound
		self.footstepsSound = base.loader.loadSfx("media/footsteps.wav")
		self.footstepsSound.setLoop(1)
		self.footsteps = SoundWrapper(self.footstepsSound)

		# Create other sounds.
		self.jumpSound = base.loader.loadSfx("media/jump_start.wav")
		self.landSound = base.loader.loadSfx("media/jump_fall.wav")

	def updatePosFromPhysics(self):
		self.node.setPos(render, self.body.getPosition() + self.offset)
		self.body.setAngularVel(0, 0, 0)

	def updatePhysicsFromPos(self):
		self.body.setPosition(self.node.getPos() - self.offset)
		self.body.setQuaternion(self.node.getQuat())

	def getDir(self):
		return base.render.getRelativeVector(self.node, (0, 1, 0))

	def moveTo(self, pos):
		self.node.setPos(pos)
		self.updatePhysicsFromPos()

	def recoil(self, mag):
		vel = self.body.getLinearVel()
		diff = self.getDir() * mag
		
		# Limit recoil
		if sign(vel[0]) != sign(diff[0]) and abs(vel[0]) > 15: diff[0] = 0
		if sign(vel[1]) != sign(diff[1]) and abs(vel[1]) > 15: diff[1] = 0
		diff[2] = 0

		self.body.setLinearVel(vel - diff)

	def jump(self):
		vel = self.body.getLinearVel()
		self.body.setLinearVel(vel[0], vel[1], vel[2] + self.jumpspeed)
		self.jumpSound.play()

	def isJumping(self):
		return abs(self.body.getLinearVel()[2]) > 0.05

	def setKey(self, button, value):
		self.keys[button] = value

	def setupKeys(self):
		base.accept("w", self.setKey, [0, 1]) #forward
		base.accept("s", self.setKey, [1, 1]) #back
		base.accept("a", self.setKey, [2, 1]) #strafe left
		base.accept("d", self.setKey, [3, 1]) #strafe right
		base.accept("space", self.setKey, [4, 1]) #jump
		base.accept("w-up", self.setKey, [0, 0])
		base.accept("s-up", self.setKey, [1, 0])
		base.accept("a-up", self.setKey, [2, 0])
		base.accept("d-up", self.setKey, [3, 0])
		base.accept("space-up", self.setKey, [4, 0])

	def moveTask(self, task):
		# Initialize variables
		elapsed = globalClock.getDt()
		x = 0.0
		y = 0.0
		jumping = self.isJumping()

		# Calculate movement vector.
		if self.keys[0] != 0:
			y = self.forwardspeed
		if self.keys[1] != 0:
			y = -self.backspeed
		if self.keys[2] != 0:
			x = -self.strafespeed
		if self.keys[3] != 0:
			x = self.strafespeed
		self.vel = Vec3(x, y, 0)
		self.vel *= elapsed

		# Move the character along the ground.
		hpr = self.node.getHpr()
		self.node.setP(0)
		self.node.setR(0)
		self.node.setPos(self.node, self.vel)
		self.updatePhysicsFromPos()
		self.node.setHpr(hpr)

		# Play landing sound (if applicable).
		if self.wasJumping and not jumping:
			pass #Landing detection not working.
			#self.landSound.play()

		# Jump (if applicable).
		if self.keys[4] and not jumping:
			self.jump()
		self.wasJumping = jumping

		# Play footsteps if walking.
		if not jumping and (self.keys[0] != 0 or self.keys[1] != 0 or self.keys[2] != 0 or self.keys[3] != 0):
			self.footsteps.resume()
		else:
			self.footsteps.pause()

		return task.cont
