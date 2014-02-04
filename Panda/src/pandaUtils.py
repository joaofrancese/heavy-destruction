from pandac.PandaModules import AudioSound, WindowProperties, Vec4, loadPrcFileData

def setWindowTitle(title):
	wp = WindowProperties()
	wp.setTitle(title)
	base.win.requestProperties(wp)

def preSetWindowIcon(filename):
	# Must be called before ShowBase().
	loadPrcFileData("", "icon-filename " + filename)

def centerWindow():
	curProps = base.win.getProperties()
	wp = WindowProperties()
	wp.setOrigin((base.pipe.getDisplayWidth() - curProps.getXSize()) / 2,
		(base.pipe.getDisplayHeight() - curProps.getYSize()) / 2)
	base.win.requestProperties(wp)

def hideMouse(hidden):
	wp = WindowProperties()
	wp.setCursorHidden(hidden)
	base.win.requestProperties(wp)

def toggleFullscreen():
	wp = WindowProperties()
	wp.setFullscreen(not base.win.isFullscreen())
	base.win.requestProperties(wp)

def makeVec4Color(color):
	return Vec4(color[0], color[1], color[2], color[3] if len(color) == 4 else 1.0)

def sign(num):
	return cmp(num, 0)


class SoundWrapper():
	def __init__(self, sound):
		self.sound = sound
		self.pos = 0

	def play(self):
		self.sound.play()

	def stop(self):
		self.sound.stop()

	def pause(self):
		if self.sound.status() == AudioSound.PLAYING:
			self.pos = self.sound.getTime()
			self.sound.stop()

	def resume(self):
		if self.sound.status() == AudioSound.READY:
			self.sound.setTime(self.pos)
			self.sound.play()
