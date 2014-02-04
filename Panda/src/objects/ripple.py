from pandac.PandaModules import TransparencyAttrib

class Ripple():
	lifetime = 100

	def __init__(self, parent, color, pos, dir, scale):
		self.node = parent.attachNewNode("")
		self.node.reparentTo(parent)
		self.node.setPos(*pos)
		self.node.setColor(*color)
		self.node.setTransparency(TransparencyAttrib.MAlpha)
		self.node.setScale(scale, scale, scale)
		self.node.lookAt(self.node, *dir)

		self.life = Ripple.lifetime

		self.model = loader.loadModel("models/ripple.egg")
		self.model.reparentTo(self.node)
		
		taskMgr.add(self.fadeTask, "ripple-fade")

	def fadeTask(self, task):
		if self.life > 0:
			self.life -= 1
			self.node.setAlphaScale(1.5 * self.life / Ripple.lifetime)
			return task.cont
		else:
			self.node.detachNode()
			return task.done
