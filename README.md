Python Robotic Simulator
________________________

Important notice:
The program is provided as is. No warranty or support will be provided. However, you may try at puheim@gmail.com

Description:
Train AI controller of mobile robot on 2D race track using custom semi-interactive evolutionary algorithm.

Depedencies:
Python 3.6 and later
pygame 1.9.3 and later

Setup:
install Python 3
from command line run:
  pip install pygame

Interactive evolution of fuzzy cognitive map controller:
run interactiveEvolution.py

Program controls:
- right mouse click to decrease fitness to 2/3 of former value (lower fitness means better individual)
- left mouse click to increase fitness to 3/2 of former value 
- left and right arrow keys to view whole generation

Results of evolution are stored in folder:
/results/

Configuration:
edit interactiveEvolution.py

Other useful scripts:
runSimulation.py
viewTrajectory.py
tracks/_track_designer.zip

________________________________
Created by M. Puheim in 2015.
Credits to J. Vraštiak, M. Širochman and T. Sabol. 2011-2017.
