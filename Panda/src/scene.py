from pandac.PandaModules import Point3, Vec3, VBase4, PointLight, AmbientLight, Fog
from objects.plane import Plane
from objects.sphere import Sphere
from objects.spinner import Spinner
from objects.box import createWall

class Scene:
	def __init__(self, world, parent, cameraHandler, character):
		self.world = world
		self.parent = parent
		self.objects = []
		self.boundaries = []
		self.cameraHandler = cameraHandler
		self.character = character

		self.bgm = base.loader.loadSfx("media/ambient.ogg")
		self.bgm.setVolume(2.0)
		self.bgm.setLoop(True)
		self.bgm.play()

	def createBoundaries(self, sizeVector, centerPos):
		x, y, z = centerPos
		sx, sy, sz = sizeVector
		b = []
		b.append(Plane(self.world, self.parent, (x, y, z - sz), (0, 0,-1), sx, sy, (0.7, 0.7, 0.8, 0.0), "floor", "media/floor_quake.png"))
		b.append(Plane(self.world, self.parent, (x, y, z + sz), (0, 0, 1), sx, sy, (0.4, 0.4, 0.4, 0.0), "ceiling", "media/floor_metal_plate.tga"))
		b.append(Plane(self.world, self.parent, (x - sx, y, z), (-1, 0,0), sy, sz, (0.38, 0.40, 0.35, 0.0), "left", "media/brick_wall.tga"))
		b.append(Plane(self.world, self.parent, (x + sx, y, z), ( 1, 0,0), sy, sz, (0.38, 0.38, 0.38, 0.0), "right", "media/brick_wall.tga"))
		b.append(Plane(self.world, self.parent, (x, y - sy, z), (0,-1, 0), sx, sz, (0.35, 0.40, 0.35, 0.0), "front", "media/brick_wall.tga"))
		b.append(Plane(self.world, self.parent, (x, y + sy, z), (0, 1, 0), sx, sz, (0.35, 0.40, 0.40, 0.0), "back", "media/brick_wall.tga"))
		return b

	def setupLighting(self, sizeVector, centerPos):
		x, y, z = centerPos
		sx, sy, sz = (Vec3(sizeVector) * 0.8)

		# Point lights, one in each ceiling corner.
		for i in (x-sx, x+sx):
			for j in (y-sy, y+sy):
				for k in (z+sz,):
					self.addPointLight((i, j, k))

		# Ambient light.
		c = 0.4
		lightA = AmbientLight("light-ambient")
		lightA.setColor(VBase4(c, c, c, 1))
		lightANode = render.attachNewNode(lightA)
		render.setLight(lightANode)

		# Fog.
		fog = Fog("fog")
		fog.setColor(1, 1, 1)
		fog.setExpDensity(0.002)
		render.setFog(fog)

	def addPointLight(self,	 pos):
		k = 12
		light = PointLight("light-point")
		light.setColor(VBase4(k, k, k, 1))
		light.setAttenuation(Point3(0.2, 0.1, 0.01))
		node = render.attachNewNode(light)
		node.setPos(*pos)
		render.setLight(node)


class FallingBalls(Scene):
	def __init__(self, world, parent, cameraHandler, character):
		Scene.__init__(self, world, parent, cameraHandler, character)
		self.sphere1 = Sphere(world, parent, (0.7, 0.4, 0.4), (-5, 0,  7), ( 1, 0, 0), 0.9, 30)
		self.sphere1.body.setLinearVel(-1.0, 0.0, 0.0)
		self.sphere2 = Sphere(world, parent, (0.4, 0.7, 0.4), ( 0, 0, 12), ( 0, 1, 0), 1.2, 30)
		self.sphere2.body.setLinearVel(0.0, 0.0, -15.0)
		self.sphere3 = Sphere(world, parent, (0.4, 0.4, 0.7), ( 5, 0,  4), (-1, 0, 0), 1.0, 30)
		self.sphere3.body.setLinearVel(5.0, 0.0, 15.0)

		self.spinner1 = Spinner(world, parent, (0.25, 0.19, 0.13), (-4, 0, 1), (0, 0, -1), (0, -1, 0), (2.0, 1.0, 4.0), 50)
		self.spinner2 = Spinner(world, parent, (0.25, 0.19, 0.13), ( 4, 0, 1), (0, 0, -1), (0, -1, 0), (2.0, 1.0, 4.0), 50)

		self.createBoundaries((30, 20, 20), (0, 0, 5))
		self.setupLighting((30, 20, 20), (0, 0, 5))

class BasicWall(Scene):
	def __init__(self, world, parent, cameraHandler, character):
		Scene.__init__(self, world, parent, cameraHandler, character)

		# Setup the containing area.
		volume = (60, 60, 18)
		center = (0, 0, 18)
		self.createBoundaries(volume, center)
		self.setupLighting(volume, center)
		character.moveTo((0, 0, 15))

		# Create the wall itself.
		color = (0.8, 0.8, 0.8)
		size = (3, 1, 2)
		pos = (-20, 30, size[2])
		density = 10
		quantity = (4, 2, 3)
		shatterLimit = 2
		tileThickness = 0.05
		tileShatterLimit = 1
		createWall(world, parent, color, pos, size, density, quantity, shatterLimit, tileThickness, tileShatterLimit)

