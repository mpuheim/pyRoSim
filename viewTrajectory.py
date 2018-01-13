#!/usr/bin/python
# This Python file uses the following encoding: utf-8

import time, datetime
import sys
from modules import simulation, gui
from modules.utils import struct, makedir
from modules.config import res,simstep

# set save folder
folder = 'results'
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
navdist = 20
stopdist = 100
navigator = simulation.Navigator(track, car, start, navdist, stopdist)
# init controller
controller = simulation.SimpleController()
# init timer
timer = simulation.Timer()
# init statistics
statistics = []
# init simulator
simulator = simulation.Simulator(track, car, navigator, controller, timer)
# run control loop
run = 1
while (run):
    # run simulation step
    simulator.runSimulationStep(fast=True)
    # save stats
    simulator.saveStats(statistics)
    # stop conditions
    if (simulator.navigator.finished > 0 or simulator.navigator.lost == True):
        run = 0
    if (simulator.timer.getRealTime() > 2):
        simulator.navigator.lost = True
        run = 0
# average statistics
results = simulator.aggregateStats(statistics)
# draw trajectory
screen.zoom_mode = 0
gui.DrawTrajectory(screen, simulator, statistics, results)
# show trajectory
while (gui.Refresh(screen)): pass
# save stats
makedir(folder)
now = datetime.datetime.now()
folder += '/runtime-date-'+str(now.strftime("%Y-%m-%d-time-%H-%M"))
makedir(folder)
# save runtime stats
runtime_file = folder + "/stats.txt"
with open(runtime_file, 'w') as f:
    line = 'Time;Distance;Speed;Acceleration;Direction;Turn;GoalAngle;X;Y'
    f.write(line+'\n')
    for stat in statistics:
        line = str(stat.time)
        line+=';'+str(stat.distance)
        line+=';'+str(stat.speed)
        line+=';'+str(stat.acceleration)
        line+=';'+str(stat.direction)
        line+=';'+str(stat.turn)
        line+=';'+str(stat.goalangle)
        line+=';'+str(stat.x)
        line+=';'+str(stat.y)
        f.write(line+'\n')
# save averages
averages_file = folder + "/averages.txt"
with open(averages_file, 'w') as f:
    line = 'TimeAVG;DistanceAVG;SpeedAVG;AccelerationAVG;Turn;GoalAngle;Lost;Finished'
    f.write(line+'\n')
    line=str(results.time)
    line+=';'+str(results.distance)
    line+=';'+str(results.avg_speed)
    line+=';'+str(results.avg_acc)
    line+=';'+str(results.avg_turn)
    line+=';'+str(results.avg_goalangle)
    line+=';'+str(results.lost)
    line+=';'+str(results.finished)
    f.write(line+'\n')
# save trajectory
trajectory_file = folder + "/trajectory.png"
printscreen = gui.InitSubscreen(0,(0,0),(800,800))
printscreen.zoom_mode = 0
gui.DrawTrajectory(printscreen, simulator, statistics, results)
gui.ShowInfo(printscreen,'Controller Runtime',(10,10),15)
gui.saveScreen(printscreen,trajectory_file)
