from pandac.PandaModules import Point3, TransparencyAttrib, CardMaker
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpColorInterval
from direct.gui.OnscreenImage import OnscreenImage

from pandaUtils import hideMouse

# Adapted from: http://www.panda3d.org/forums/viewtopic.php?t=9143

class CameraHandler():
	def __init__(self, character):
		self.character = character
		
		# Setup mouse
		base.disableMouse()
		hideMouse(True)
		self.mouseSensitivity = 0.1
		base.taskMgr.doMethodLater(0.1, self.prepareCameraTask,  "prepare-camera")

		# Setup camera
		base.camera.reparentTo(self.character.node)
		base.camera.setPos(0, 0, 0)
		base.camera.lookAt(0, 1, 0)

		# Create target
		self.target = OnscreenImage(image = "media/target.png", pos = (0, 0, 0))
		self.target.setTransparency(TransparencyAttrib.MAlpha)
		self.target.setScale(0.1)
		self.target.setSa(0.5)

		# Create overlay
		self.overlayCard = CardMaker("overlayCard")
		self.overlayCard.setFrameFullscreenQuad()
		self.overlay = base.render2d.attachNewNode(self.overlayCard.generate())
		self.overlay.setTransparency(TransparencyAttrib.MAlpha)
		self.overlay.setColor(0,0,0,0)

		# Setup interval sequences
		self.shakeSequence = None
		self.flashSequence = None

	def shake(self, amplitude = (1,0,0), duration = 1.0, swings = 1):
		if self.shakeSequence != None:
			self.shakeSequence.finish()
		self.shakeSequence = Sequence()

		swings = int(swings)
		duration = float(duration)
		dt = duration / (swings * 4)
		ds = Point3(amplitude)

		for i in range(swings):
			self.shakeSequence.append(LerpPosInterval(base.camera, dt, ds*-1))
			self.shakeSequence.append(LerpPosInterval(base.camera, dt*2, ds))
			self.shakeSequence.append(LerpPosInterval(base.camera, dt, Point3(0, 0, 0)))
		self.shakeSequence.start()

	def flash(self, color = (1,1,1,1), duration = 1.0, fadeIn = 0.2):
		if self.flashSequence != None:
			self.flashSequence.finish()
		self.flashSequence = Sequence()

		dtIn = float(duration) * fadeIn
		dtOut = duration - dtIn

		if dtIn > 0:
			self.flashSequence.append(LerpColorInterval(self.overlay, dtIn, color))
		if dtOut > 0:
			self.flashSequence.append(LerpColorInterval(self.overlay, dtOut, (0,0,0,0), color))
		self.flashSequence.start()

	def prepareCameraTask(self, task):
		base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2)
		base.taskMgr.add(self.controlCameraTask, "camera-control")
		return task.done

	def controlCameraTask(self, task):
		char = self.character.node
		
		# Get current mouse location.
		md = base.win.getPointer(0)
		x = md.getX()
		y = md.getY()

		# Rotate character based on mouse coordinates.
		if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
			char.setP((char.getP() - (y - base.win.getYSize()/2)*self.mouseSensitivity) % 360)
			char.setH((char.getH() - (x - base.win.getXSize()/2)*self.mouseSensitivity) % 360)

		# Don't let the camera loop over. Allowed range is 0-90 (up) and 360-270 (down).
		if char.getP() > 90 and char.getP() < 180:
			char.setP(90)
		elif char.getP() < 270 and char.getP() >= 180:
			char.setP(270)

		return task.cont
