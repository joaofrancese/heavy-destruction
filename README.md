# Heavy Destruction

Heavy Destruction is an interactive demo first-person shooter (FPS) game made with Python, Panda3D and ODE which focuses on showcasing an implementation of destructible environments, namely walls.

The demo was made as part of the author's undergraduation thesis in Universidade Federal do Rio de Janeiro (UFRJ), Brazil. The full paper (in Portuguese), named ["Experimentation in Interactive Physics Simulations for Games"](Downloads/Monografia%20-%20Joao%20Pedro%20Schara%20Francese.pdf), and its associated [presentation slides](Downloads/Apresentacao%20-%20Joao%20Pedro%20Schara%20Francese.pdf), are available in the Downloads folder, as well as [30-second video of the demo](Downloads/Demo.mp4).

![ScreenShot](https://raw2.github.com/joaofrancese/heavy-destruction/master/Downloads/Screenshot%20(v1.0).jpg)

## Running the game

The [compiled version](Downloads/heavy-destruction.p3d) can be found in the Downloads folder. To run it, the [Panda3D runtime](http://www.panda3d.org/download.php?runtime) must be installed in your system.

After cloning the repository or downloading it as a ZIP file, you may run the game from source using the script located in Panda/src/main.py. The full [Panda3D SDK](http://www.panda3d.org/download.php?sdk) must be installed in your system.

Commandline arguments are:

- *full* starts the game in fullscreen mode
- *balls* loads the alternative Falling Balls scene
- *debug* enables debug mode

Game controls:

- W, A, S, D move the character
- Space jumps
- Mouse controls camera
- Left button fires; hold down button to control the bullet speed
- Esc pauses the simulation (you can continue to move around
- Backspace toggles wireframe rendering


## External references

- Panda 3D: http://www.panda3d.org/
- LCG/UFRJ (Computer Graphics Lab): http://www.lcg.ufrj.br/
- Open Dynamics Engine (ODE): http://www.ode.org/