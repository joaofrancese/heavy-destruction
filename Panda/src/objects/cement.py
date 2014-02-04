from pandac.PandaModules import OdeFixedJoint

class Cement:
	def __init__(self, one, two):
		b1 = None
		b2 = None

		self.one = one
		if one != None:
			one.addCement(self)
			b1 = one.body

		self.two = two
		if two != None:
			two.addCement(self)
			b2 = two.body

		self.joint = OdeFixedJoint(one.world.world)
		self.joint.attach(b1, b2)
		self.joint.set()
		self.active = True

	def destroy(self):
		if not self.active:
			return

		self.joint.destroy()
		if self.one != None:
			self.one.removeCement(self)
		if self.two != None:
			self.two.removeCement(self)
		self.active = False