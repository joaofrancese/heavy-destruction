from pandac.PandaModules import OdeBody, OdeMass, OdeSphereGeom
from gameObject import GameObject
from objects.ripple import Ripple

class Sphere(GameObject):
	def __init__(self, world, parent, color, pos, dir, radius, density, posParent=None):
		GameObject.__init__(self, world)

		self.node = parent.attachNewNode("")
		if posParent == None:
			self.node.setPos(*pos)
		else:
			self.node.setPos(posParent, *pos)
		self.node.setColor(*color)
		self.node.setScale(radius)
		self.node.lookAt(self.node, *dir)
		self.parent = parent

		self.color = color
		self.scale = radius

		self.model = loader.loadModel("models/smiley.egg")
		self.model.reparentTo(self.node)

		self.mass = OdeMass()
		self.mass.setSphere(density, radius)
		self.body = OdeBody(world.world)
		self.body.setMass(self.mass)
		self.body.setPosition(self.node.getPos())
		self.body.setQuaternion(self.node.getQuat())
		self.body.setData(self)
		self.geom = OdeSphereGeom(world.space, radius)
		self.geom.setBody(self.body)
		world.space.setSurfaceType(self.geom, world.surfaces["sphere"])

	def onCollision(self, otherBody, entry):
		if otherBody.isEmpty(): # Collision on a wall
			geom = entry.getContactGeom(0)
			Ripple(self.parent, self.color, geom.getPos(), geom.getNormal() * -1, self.scale * 2.5)
