import time

from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import AntialiasAttrib

from pandaUtils import centerWindow, toggleFullscreen, setWindowTitle, preSetWindowIcon
from world import World
from character import Character
from cameraHandler import CameraHandler
from shooter import Shooter
import scene

class Game:
	def __init__(self, fullscreen, sceneName=None):
		# Start Panda
		preSetWindowIcon("media/heavy_destruction.ico")
		ShowBase()
		
		# Some non-gameplay setup.
		self.name = "Heavy Destruction"
		self.version = 1.0
		base.setBackgroundColor(0, 0, 0)
		centerWindow()
		render.setAntialias(AntialiasAttrib.MAuto)
		if fullscreen: toggleFullscreen()
		self.setupKeys()
		self.setupFps()
		self.setupTitle()

		# Setup game objects.
		self.world = World(self)
		self.character = Character(self.world)
		self.cameraHandler = CameraHandler(self.character)
		self.shooter = Shooter(self.character)

		# Select a scene.
		if sceneName == "balls":
			self.scene = scene.FallingBalls(self.world, render, self.cameraHandler, self.character)
		else:
			self.scene = scene.BasicWall(self.world, render, self.cameraHandler, self.character)

	def run(self):
		Game.current = self
		run()

	def setupKeys(self):
		base.accept("alt-enter", toggleFullscreen, [])
		base.accept("backspace", base.toggleWireframe, [])

	def setupFps(self):
		self.fps = 0
		self.fpsCounter = 0
		self.fpsPrevTimestamp = time.clock()
		base.taskMgr.add(self.updateFpsTask, "update-fps")

	def setupTitle(self):
		self.title = self.name + " " + str(self.version) + " - %d physical object(s) - %d FPS"
		base.taskMgr.add(self.updateTitleTask, "update-title")

	def updateFpsTask(self, task):
		self.fpsCounter += 1
		timestamp = time.clock()
		if timestamp - self.fpsPrevTimestamp > 1:
			self.fps = self.fpsCounter
			self.fpsCounter = 0
			self.fpsPrevTimestamp = timestamp
		return task.cont

	def updateTitleTask(self, task):
		setWindowTitle(self.title % (len(self.world.objects), self.fps))
		return task.cont



