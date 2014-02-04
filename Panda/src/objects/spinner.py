from pandac.PandaModules import OdeHingeJoint
from box import Box

class Spinner(Box):
	def __init__(self, world, parent, color, pos, dir, axis, size, density):
		Box.__init__(self, world, parent, color, pos, dir, size, density)
		self.body.setGravityMode(False)
		self.joint = OdeHingeJoint(world.world)
		self.joint.attach(self.body, None)
		self.joint.setAnchor(self.node.getPos())
		self.joint.setAxis(*axis)
		self.joint.setParamBounce(0.0)
