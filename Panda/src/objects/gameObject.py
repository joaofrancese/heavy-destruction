from pandac.PandaModules import Quat, BitMask32
import threading

class GameObject:
	bitmaskAll = BitMask32.allOn()
	bitmaskDefault = BitMask32.bit(0)
	bitmaskBullet = BitMask32.bit(1)
	bitmaskCharacter = BitMask32.bit(2)
	bitmaskBox = BitMask32.bit(3)
	bitmaskTileGlued = BitMask32.bit(4)
	bitmaskTile = BitMask32.bit(5)
	
	def __init__(self, world):
		world.addObject(self)
		self.world = world
		self.body = None
		self.geom = None
		self.node = None

		self.active = True
		self.visibleAfterDestroy = False
		self.dissipateCountdown = 0

	def updatePosFromPhysics(self):
		if self.body != None:
			self.node.setPosQuat(render, self.body.getPosition(), Quat(self.body.getQuaternion()))

	def getMomentum(self):
		mass = self.body.getMass().getMagnitude()
		speed = self.body.getLinearVel().length()
		return mass * speed

	def dissipate(self, factor, interval=5):
		if self.body == None or self.dissipateCountdown > 0:
			return
		self.body.setLinearVel(self.body.getLinearVel() * factor)
		self.body.setAngularVel(self.body.getAngularVel() * factor)
		self.dissipateCountdown = interval + 1
		self.dissipateRecover()

	def dissipateRecover(self):
		self.dissipateCountdown -= 1
		if self.dissipateCountdown > 0:
			self.world.performAfterStep(self.dissipateRecover, [])
	
	def onCollision(self, otherBody, entry):
		pass

	def destroy(self):
		self.active = False
		self.world.removeObject(self)

	def doDestroy(self):
		if self.node != None and not self.visibleAfterDestroy:
			self.node.detachNode()
		if self.geom != None:
			self.geom.disable()
		if self.body != None:
			self.body.disable()
		return

		# This is the code that actually removes the elements instead of just disabling them.
		# But it doesn't work.
		obj = self
		print obj #DEBUG
		print threading.current_thread() #DEBUG
		print "0", #DEBUG
		if obj.node != None:
			obj.node.detachNode()
			obj.node = None
		print "1", #DEBUG
		if obj.geom != None:
			self.world.space.remove(obj.geom) #Probably unnecessary
		print "2", #DEBUG
		if obj.geom != None:
			obj.geom.destroy()
			obj.geom = None
		print "3", #DEBUG
		if obj.body != None:
			obj.body.destroy()
			obj.body = None
		print "4" #DEBUG
