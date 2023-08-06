# Simple ABCD matrix propagator.

Main file in this directory is tracer.py.  

# Installation

You can install using `pip` at https://pypi.org/project/beamtrace/ 
```
pip install beamtrace
```
then in a python scipy or ipython terminal, import the BeamTrace class by running
```python
import beamtrace
from beamtrace.tracer import BeamTrace
```

or if you have LIGO credentials you can git clone the directory at https://git.ligo.org/craig-cahillane/beamtrace
and run
```python
import sys
sys.path.addpath('path/to/this/directory')
from beamtrace.tracer import BeamTrace
```

# Docstring

From beamtrace/tracer.py, the main class BeamTrace docstring;

```python
Class BeamTrace
For very simple beam waist and gouy phase calculations in python.
No fancy optimization like alamode, no nice GUI like jammt.
Just mirrors, lenses, and lengths added in sequence.

### Better options:
MATLAB alamode: https://github.com/nicolassmith/alm
JAMMT: http://www.sr.bham.ac.uk/dokuwiki/doku.php?id=geosim:jammt
Finesse + pykat: https://git.ligo.org/finesse/pykat


### Process:
User adds in mirrors, lenses, and spaces *in sequential order*.
User computes the cavity ABCD matrix from the components added using calculate_cavity_ABCD().
If cavity is stable, find the fundamental eigenmode for the beam (q-parameter)
Set this q-parameter as q_input beam.
Scan the cavity beam parmater using scan_cavity().

### Examples:
# Simple resonator
import numpy as np

my_cav = BeamTrace()        # initializes ABCD class
my_cav.add_mirror(1.0) # adds mirror with 1.0 meter radius of curvature at z=0.0 meters
my_cav.add_space(0.5)  # adds 0.5 meters of space to cavity
my_cav.add_mirror(1.0) # adds mirror with 1.0 meter radius of curvature at z=0.5 meters
my_cav.calculate_cavity_ABCD() # Finds the cavity round-trip ABCD matrix, tells you if it's stable.  If it is stable, populates the my_cav.q_input parameter
zz, ww, gouy, qq = my_cav.scan_cavity(round_trip=True) # Returns propagation distance, beam radius, accumulated gouy phase, and beam q-parameter for the entire cavity, plus the round-trip

import matplotlib.pyplot as plt
fig = my_cav.plot_cavity_scan(round_trip=True, label='Simple Cavity')
plt.show()

# LIGO arm cavity
R1 = 1934. # m
R2 = 2245. # m
L = 3994.469 # m
arm_cav = BeamTrace()

arm_cav.add_mirror(R1, name='ITMY')
arm_cav.add_space(L)
arm_cav.add_mirror(R2, name='ETMY')

fig = arm_cav.plot_cavity_scan(round_trip=True)
plt.show()
```

# Simple ABCD matrix calculations

Space matrix, $`L`$ is the length of the space

$`S(L) = \begin{bmatrix}
1 & L \\
0 & 1
\end{bmatrix}
`$

Lens, $`f`$ is the focal length

$`L(f) = \begin{bmatrix}
1 & 0 \\
-\frac{1}{f} & 1
\end{bmatrix}
`$

Mirror, $`R`$ is the radius of curvature with index of refraction $`n`$, same as lens with $`f = RoC/2`$

$`M(R) = \begin{bmatrix}
1 & 0 \\
-\frac{2 n}{R} & 1
\end{bmatrix}
`$

Refraction through a surface with radius of curvature $`R`$, initial index of refraction $`n1`$, and final index of refraction $`n2`$:

$`F(R, n1, n2) = \begin{bmatrix}
1 & 0 \\
\frac{n2 - n1}{n2 R} & \frac{n1}{n2}
\end{bmatrix}
`$

# Other Options:
[Finesse + pykat](https://git.ligo.org/finesse/pykat)

[MATLAB alamode](https://github.com/nicolassmith/alm)

[JAMMT](http://www.sr.bham.ac.uk/dokuwiki/doku.php?id=geosim:jammt)

# References:

[Kogelnik and Li](https://www.osapublishing.org/ao/abstract.cfm?URI=ao-5-10-1550)

[Koji Arai on beam prop](https://dcc.ligo.org/public/0102/T1300189/001/T1300189_v1_cavity_gouy_phase.pdf)

[Wikipedia with ABCD matrices](https://en.wikipedia.org/wiki/Ray_transfer_matrix_analysis)

[Stefan SRC gouy phase meas](https://alog.ligo-wa.caltech.edu/aLOG/index.php?callRep=52504)
