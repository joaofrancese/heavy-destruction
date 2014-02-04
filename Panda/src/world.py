from pandac.PandaModules import OdeJointGroup, OdeWorld, OdeHashSpace

class World:
	def __init__(self, game):
		self.game = game
		self.world = OdeWorld()
		self.world.setGravity(0, 0, -9.81 * 3)
		self.group = OdeJointGroup()
		self.space = OdeHashSpace()
		self.space.setAutoCollideWorld(self.world)
		self.space.setAutoCollideJointGroup(self.group)
		self.setSurfaceTables()
		self.objects = []
		self.objectsToRemove = []
		self.postStepTasks = []

		self.engineRunning = True
		self.dtAccumulator = 0.0
		self.physicsFps = 90
		self.physicsMinFps = 10
		base.taskMgr.doMethodLater(0.1, self.processPhysics, "Physics")
		base.accept("escape", self.togglePhysics)

		self.space.setCollisionEvent("odeCollision")
		base.accept("odeCollision", self.onCollision)
		
	def setSurfaceTables(self):
		self.surfaces = {}
		self.surfaces["plane"] = 0
		self.surfaces["box"] = 1
		self.surfaces["sphere"] = 2
		self.surfaces["bullet"] = 3
		n = len(self.surfaces)

		self.world.initSurfaceTable(n)
		for i in range(n):
			for j in range(n):
				# id1, id2, mu (0 to inf), bounce (1 = bouncy), min_bounce_vel, erp (1 = hard), cfm (0 = hard), slip, dampen
				# sample:   150,             0.0,                    9.1,       0.9,          0.00001,          0.0,  0.002
				self.world.setSurfaceEntry(i, j, 10.0, 1.0, 0.0, 0.9, 0.0, 0.5, 0.001) # Default value for unspecified pairs.
		self.world.setSurfaceEntry(self.surfaces["box"], self.surfaces["box"],
			200.0, 0.2, 0.3, 1.0, 0.0, 0.0, 0.01)
		self.world.setSurfaceEntry(self.surfaces["plane"], self.surfaces["box"],
			200.0, 0.2, 0.3, 1.0, 0.0, 0.0, 0.01)
		self.world.setSurfaceEntry(self.surfaces["box"], self.surfaces["bullet"],
			10.0, 0.1, 0.5, 1.0, 0.0, 0.0, 0.01)
		self.world.setSurfaceEntry(self.surfaces["plane"], self.surfaces["bullet"],
			100.0, 0.01, 0.1, 1.0, 0.0, 0.0, 1.0)

	def addObject(self, obj):
		self.objects.append(obj)

	def removeObject(self, obj):
		if obj not in self.objectsToRemove:
			self.objectsToRemove.append(obj)

	def removeDestroyedObjects(self):
		while len(self.objectsToRemove) > 0:
			obj = self.objectsToRemove.pop()
			if obj in self.objects:
				self.objects.remove(obj)
				obj.doDestroy()

	def togglePhysics(self):
		self.engineRunning = not self.engineRunning
		self.dtAccumulator = 0.0

	def processPhysics(self, task):
		stepSize = 1.0 / self.physicsFps
		maxDt = 1.0 / self.physicsMinFps
		if self.engineRunning:
			self.dtAccumulator += globalClock.getDt()
			self.dtAccumulator = min(self.dtAccumulator, maxDt)
			while self.dtAccumulator >= stepSize:
				self.space.autoCollide()
				self.world.quickStep(stepSize)
				for obj in self.objects:
					obj.updatePosFromPhysics()
				self.group.empty()
				self.performPostStepTasks()
				self.removeDestroyedObjects()
				self.dtAccumulator -= stepSize
		return task.cont

	def onCollision(self, entry):
		body1 = entry.getBody1()
		body2 = entry.getBody2()
		if not body1.isEmpty():
			body1.getData().onCollision(body2, entry)
		if not body2.isEmpty():
			body2.getData().onCollision(body1, entry)

	def performAfterStep(self, method, params):
		self.postStepTasks.append([method, params])

	def performPostStepTasks(self):
		for task in self.postStepTasks:
			method = task[0]
			params = task[1]
			method(*params)
		self.postStepTasks = []
