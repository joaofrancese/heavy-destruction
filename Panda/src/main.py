import __builtin__
import sys
from game import Game

full = False
sceneName = None
__builtin__.DEBUG = False

for arg in sys.argv:
	if arg.lower() == "full": full = True
	if arg.lower() == "balls": sceneName = "balls"
	if arg.lower() == "debug": __builtin__.DEBUG = True

Game(full, sceneName).run()