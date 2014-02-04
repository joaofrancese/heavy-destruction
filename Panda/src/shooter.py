from random import random

from pandac.PandaModules import CardMaker, Point3
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval

from objects.bullet import Bullet

class Shooter(FSM):
	def __init__(self, character):
		FSM.__init__(self, "ShooterFSM")
		
		self.character = character
		self.world = self.character.world

		# Set firing control handlers.
		base.accept("mouse1", self.request, ["Shooting"])
		base.accept("mouse1-up", self.request, ["Waiting"])

		# Create power meter.
		self.meter = base.render2d.attachNewNode("powerMeter")
		self.meter.setPos(-0.2, 0.0, 0.0)
		self.meter.hide()

		self.meterBGCard = CardMaker("powerMeterBG")
		self.meterBGCard.setFrame(0.0, 0.4, -0.9, -0.95)
		self.meterBGCard.setColor(0.5, 0.0, 0.0, 1.0)
		self.meterBG = self.meter.attachNewNode(self.meterBGCard.generate())

		self.meterFGCard = CardMaker("powerMeterFG")
		self.meterFGCard.setFrame(0.0, 0.4, -0.9, -0.95)
		self.meterFGCard.setColor(1.0, 0.0, 0.0, 1.0)
		self.meterFG = self.meter.attachNewNode(self.meterFGCard.generate())

		# Create gun.
		self.gun = loader.loadModel("models/ak47.egg")
		self.gun.reparentTo(base.camera)
		self.gun.setHpr(60, 104, 232)
		self.gun.setPos(4.0, 14.0, -3.5)
		self.gun.setScale(1.75)
		self.gunRecoil = None

		# Make gun get drawn on top.
		self.gun.setBin("fixed", 40)
		self.gun.setDepthTest(False)
		self.gun.setDepthWrite(False)

		# Load gunshot sound
		self.gunSfx = base.loader.loadSfx("media/gun.wav")
		self.gunSfx.setVolume(0.6)

	def exitShooting(self):
		angSpeed = 20.0 + (40.0 * self.powerLevel)
		linSpeed = 80.0 + (320.0 * self.powerLevel)
		color = (0.7 + 0.1*random(), 0.7 + 0.1*random(), 0.7 + 0.1*random())

		dir = self.character.getDir()
		bullet = Bullet(self.world, base.render, color, (0.0, 0.0, 0.0), dir, 0.3, 80, self.character.node)
		bullet.body.setLinearVel(dir * linSpeed)
		bullet.body.setAngularVel(dir * angSpeed)

		self.gunSfx.play()
		self.meter.hide()
		base.taskMgr.remove("powerMeterGauge")

		# Recoil and camera flash
		self.recoil()
		self.character.recoil(12)
		self.world.game.cameraHandler.flash((1,1,1,0.5), 0.2)

	def enterShooting(self):
		self.powerLevel = 0.5
		self.powerDir = 1
		self.meter.show()
		self.refreshMeter()
		base.taskMgr.add(self.gaugeTask, "powerMeterGauge")

	def gaugeTask(self, task):
		self.powerLevel += globalClock.getDt() * self.powerDir
		if self.powerLevel > 1:
			self.powerLevel = 1
			self.powerDir = -1
		elif self.powerLevel < 0:
			self.powerLevel = 0
			self.powerDir = 1
		self.refreshMeter()
		return task.cont

	def refreshMeter(self):
		self.meterFG.setSx(self.powerLevel)

	def recoil(self):
		if self.gunRecoil != None:
			self.gunRecoil.finish()
		self.gunRecoil = Sequence(LerpPosInterval(self.gun, 0.1, Point3(4.0, 12.0, -3.5)),
			LerpPosInterval(self.gun, 0.6, Point3(4.0, 14.0, -3.5), Point3(4.0, 12.0, -3.5)))
		self.gunRecoil.start()
