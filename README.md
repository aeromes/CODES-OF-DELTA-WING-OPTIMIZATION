# CODES-OF-DELTA-WING-OPTIMIZATION
Delta-Wing Shape Optimisation Toolkit
Generate a wing ➜ create a mesh ➜ run a CFD test ➜ pick the best design — all from one simple window.

1. What is this?
A small Python toolbox that automates every step of delta-wing design:

Draw the wing in FreeCAD (using a ready-made macro).

Build a 3-D mesh around it with Gmsh.

Run a CFD simulation in SU2 to see how well the wing flies.

Compare many designs and show which one has the best lift-to-drag ratio.

Do it all with a GUI so you don’t have to touch the command line if you don’t want to.

2. What you need before you start
Software	Why you need it			Where to get it
Python 3.9+	Runs the scripts and GUI	python.org
FreeCAD 0.21	Draws the wing shape		freecad.org
Gmsh 4.12+	Creates the mesh		gmsh.info
SU2 8.x “Gorky”	Runs the CFD analysis		su2code.github.io
Windows 10/11 (tested)	The toolkit is written with Windows paths in mind. Linux/macOS should also work, but we haven’t tested them yet.	

Tip: Install all four big programs and make a note of their installation paths.
Tip: Make sure each one can be opened from a normal terminal first.
3. Using the GUI step by step
Define your range – enter minimum and maximum values for sweep, span, chord, etc.

Pick sample size – how many random designs do you want to try?

Generate Geometry – the macro creates one .STEP file per design.

Generate Mesh – a .su2 mesh is built for each .STEP file.

Analyse – SU2 runs, and the program stores lift and drag numbers.

Optimise – the script ranks every design and highlights the winner.

Shortcut: Click Continuous to let it run all six steps in one go while you grab a coffee.
4. Where the files go
output_folder/
├─ samples.csv            <-- list of all design points
├─ sample_001/
│  ├─ wing_001.step
│  ├─ mesh_001.su2
│  ├─ results_M0.80/
│  │  └─ history.csv
│  └─ ...
├─ sample_002/
└─ best_design.txt        <-- summary of the top performer
6. Troubleshooting
Problem	Quick fix
FreeCAD can’t find the macro	Make sure macro.FCMacro is in the same folder as gui.py.
Gmsh import fails		pip install gmsh-sdk in the active environment.
SU2 crashes with Error 1	Check that the path to SU2_CFD.exe is correct and you have write permission in the output folder.
7. Planned improvements
Multi-objective optimisation (e.g. lift-to-drag and pitching moment)

Docker image for one-command setup

Export results directly to Excel or Paraview

8. Contributing
New ideas, bug fixes, or documentation tweaks are welcome!

Open an issue describing your change.

Fork & make a pull request.

We review together.

9. Licence
MIT – free to use, modify, and share. See LICENSE.

Happy designing, meshing, and flying!

