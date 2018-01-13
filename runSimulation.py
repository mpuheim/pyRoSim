#!/usr/bin/python
# This Python file uses the following encoding: utf-8

import time
import sys
from modules import simulation, gui
from modules.utils import struct
from modules.config import res,simstep

# init gui screen
screen = gui.Init(res)
# init track
track = simulation.Track("default_track.nft")
# set initial car position
start = 45
x = track.point[start].x
y = track.point[start].y
angle = track.gate[start].angle+90
# init car
car = simulation.Car(x_pos=x, y_pos=y, direction=angle)
# init navigator
navdist = 40
stopdist = 100
navigator = simulation.Navigator(track, car, start, navdist, stopdist)
# init controller
controller = simulation.SimpleController()
# init timer
timer = simulation.Timer()
# init simulator
simulator = simulation.Simulator(track, car, navigator, controller, timer)
# run control loop
run = 1
while (run):
    # run simulation step
    simulator.runSimulationStep()
    # refresh gui screen
    run = gui.ShowSimulation(screen, simulator)
    
