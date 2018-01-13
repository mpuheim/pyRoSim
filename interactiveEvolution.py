#!/usr/bin/python
# This Python file uses the following encoding: utf-8

import random, time, sys, datetime
from modules import simulation, gui, iec
from modules.ea import Individual
from modules.fcm import FCMcontroller, listToMatrix
from modules.utils import struct, makedir
from modules.config import res,simstep

### CONFIGURATION ###
# population
size = 30
chromosomes = 12
matsize = 8
offsprings = 15
migration = 5
# evolution
mutation = 20
crosspoints = 3
# interaction
interactivity = True
interact = 3 #generations
# stopping conditions
lap_time = 80 #seconds
# track
trackfile = "default_track.nft"
# initial car position
start = 45
# navigation params
navdist = 20
stopdist = 100
max_time = 10
# main save folder
folder = 'results'
### END OF CONFIGURATION ###

# init clocks
evolution_clock = simulation.Clockwatch()
interaction_clock = simulation.Clockwatch()
waiting_clock = simulation.Clockwatch()
program_clock = simulation.Clockwatch()
program_clock.Start()
# init gui screen
screen = gui.InitMultiscreen(res,6)
gui.ShowInfo(screen,"Initialization...")
gui.Refresh(screen)
# init sounds
gui.InitSound()
# set save folder
makedir(folder)
now = datetime.datetime.now()
folder += '/experiment-date-'+str(now.strftime("%Y-%m-%d-time-%H-%M"))
# init track
track = simulation.Track("default_track.nft")

# initial population
evolution_clock.Start()
id = 0
generation = 0
population = []
for i in range(size):
    individual = struct()
    individual.id = id
    individual.genotype = Individual(chromosomes)
    individual.fenotype = FCMcontroller(listToMatrix(individual.genotype.chromosome))
    population.append(individual)
    id += 1
    
# run simulation for each individual
for ind in population:
    # init car
    car = simulation.Car(x_pos=track.point[start].x, y_pos=track.point[start].y, direction=track.gate[start].angle+90)
    # init navigator
    navigator = simulation.Navigator(track, car, start, navdist, stopdist)
    # init controller
    controller = ind.fenotype
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
        if (simulator.timer.getRealTime() > max_time):
            simulator.navigator.lost = True
            run = 0
        # refresh gui
        if gui.Refresh(screen) == 0:
            quit()
    # average statistics
    results = simulator.aggregateStats(statistics)
    # store results for individual
    ind.stats = statistics
    ind.results = results
    ind.simulator = simulator
    # store meta-fittness
    ind.fitness = abs(results.distance-track.length)/track.length + abs(results.remaining)/track.length + 1/results.avg_speed + results.avg_goalangle/45
    # save individual
    iec.saveIndividual(ind,folder)
    # refresh gui
    gui.ClrScr(screen)
    gui.DrawTrajectory(screen, simulator, statistics, results)
    gui.ShowInfo(screen,'Individual ID:' + str(ind.id),(0.6*screen.res[0],0.2*screen.res[1]),12)
    line = 0.2*screen.res[1]+30
    for g in ind.genotype.chromosome:
        gui.ShowInfo(screen,str(g),(0.6*screen.res[0],line),12)
        line+=20
    gui.ShowInfo(screen,"Fitness:",(0.6*screen.res[0],line+40),12)
    gui.ShowInfo(screen,str(ind.fitness),(0.6*screen.res[0],line+60),12)
    gui.Refresh(screen)
    
# Sort individuals according to their meta-fitness
population = sorted(population, key=lambda ind: ind.fitness)
# Save generation
iec.saveGeneration(population,folder,generation)

# Run interactive evolution
gui.ClrScr(screen)
gui.ShowInfo(screen,'Starting interactive evolution.')
time.sleep(5)
user_exit = False
while True:
    # manage clocks
    evolution_clock.Stop()
    waiting_clock.Start()
    # enable sound alarm
    gui.EnableSound()
    # show best individuals
    first = 0
    while interactivity == True and generation%interact == 0:
        # show six individuals
        for i in range(6):
            ind = population[first+i]
            gui.DrawTrajectory(screen.subscreen[i], ind.simulator, ind.stats, ind.results)
            gui.ShowInfo(screen.subscreen[i],'ID: ' + str(ind.id),(screen.subscreen[i].res[0]-120,screen.subscreen[i].res[1]-30),10)
            gui.ShowInfo(screen.subscreen[i],'Fitness: ' + "%.2f"%ind.fitness,(screen.subscreen[i].res[0]-120,screen.subscreen[i].res[1]-20),10)
        # show gui
        result = gui.ShowMultiScreen(screen)
        # manage clocks
        waiting_clock.Stop()
        interaction_clock.Start()
        # Mute sound alarm on interaction
        gui.MuteSound()
        # Handle user exiting the program
        if result == 0:
            user_exit = True
            break
        # continue evolution
        if result == 9: break
        # handle individuals to be shown next
        change = 0
        if result == 7: change = 6
        if result == 8: change = -6
        first = (len(population)+first+change)%len(population)
        # update fitness of selected individual
        if abs(result) <= 6:
            index = abs(result)-1
            if result > 0:
                population[first+index].fitness *= 2/3
            if result < 0:
                population[first+index].fitness *= 3/2
    # handle user exiting the program
    if user_exit: break
    # manage clocks
    waiting_clock.Stop()
    interaction_clock.Stop()
    evolution_clock.Start()
    # show info
    gui.ClrScr(screen)
    gui.ShowInfo(screen,'Updating population...')
    # Sort individuals according to their meta-fitness
    population = sorted(population, key=lambda ind: ind.fitness)
    # delete worst individuals
    deleted = offsprings+migration
    del_index = len(population)-deleted
    population = population[:del_index]
    # migrate new individuals
    for i in range(migration):
        migrant = struct()
        migrant.id = id
        migrant.genotype = Individual(chromosomes)
        migrant.fenotype = FCMcontroller(listToMatrix(migrant.genotype.chromosome))
        population.append(migrant)
        id += 1
    # produce offsprings
    for i in range(offsprings):
        # select parents
        parentA = population[i]
        parentB = population[random.randint(0, del_index)]
        # initialize child
        child = struct()
        child.id = id
        # crossover
        child.genotype = parentA.genotype.crossover(parentB.genotype,crosspoints)
        # mutation
        child.genotype.mutate(mutation)
        # generate fenotype
        child.fenotype = FCMcontroller(listToMatrix(child.genotype.chromosome))
        # add to population
        population.append(child)
        id += 1
    # run simulation for each individual
    for ind in population[del_index:]:
        # init simulation objects
        car = simulation.Car(x_pos=track.point[start].x, y_pos=track.point[start].y, direction=track.gate[start].angle+90)
        navigator = simulation.Navigator(track, car, start, navdist, stopdist)
        controller = ind.fenotype
        timer = simulation.Timer()
        statistics = []
        simulator = simulation.Simulator(track, car, navigator, controller, timer)
        # run control loop
        while True:
            # run simulation step
            simulator.runSimulationStep(fast=True)
            simulator.saveStats(statistics)
            # stop conditions
            if (simulator.navigator.finished == True or simulator.navigator.lost == True):
                break
            if (simulator.timer.getRealTime() > max_time):
                simulator.navigator.lost = True
                break
            # refresh gui
            key = gui.Refresh(screen)
            if key == 2:
                interactivity = not interactivity
            # handle user exiting the program
            if key == 0:
                user_exit = True
                break
        # handle user exiting the program
        if user_exit: break
        # average statistics
        results = simulator.aggregateStats(statistics)
        # store results for individual
        ind.stats = statistics
        ind.results = results
        ind.simulator = simulator
        # store meta-fittness
        ind.fitness = abs(results.distance-track.length)/track.length + abs(results.remaining)/track.length + 1/results.avg_speed + results.avg_goalangle/45
        # save individual
        iec.saveIndividual(ind,folder)
        # refresh gui
        gui.ClrScr(screen)
        gui.DrawTrajectory(screen, simulator, statistics, results)
        gui.ShowInfo(screen,'Individual ID:' + str(ind.id),(0.6*screen.res[0],0.2*screen.res[1]),12)
        line = 0.2*screen.res[1]+30
        for g in ind.genotype.chromosome:
            gui.ShowInfo(screen,str(g),(0.6*screen.res[0],line),12)
            line+=20
        gui.ShowInfo(screen,"Fitness:",(0.6*screen.res[0],line+40),12)
        gui.ShowInfo(screen,str(ind.fitness),(0.6*screen.res[0],line+60),12)
        gui.ShowInfo(screen,"Interactivity " + ("enabled." if interactivity else "disabled."),(12,12),8)
    # handle user exiting the program
    if user_exit: break
    # Sort individuals according to their meta-fitness
    population = sorted(population, key=lambda ind: ind.fitness)
    # Save generation
    generation += 1
    iec.saveGeneration(population,folder,generation)
    # Finishing criterion
    if population[0].results.time < lap_time and population[0].results.finished == True:
        break
    
# manage clocks
interaction_clock.Stop()
evolution_clock.Stop()
waiting_clock.Stop()
program_clock.Stop()
# gather runtime statistics
simstats = struct()
simstats.totaltime = program_clock.getTimeString()
simstats.evotime = evolution_clock.getTimeString()
simstats.waittime = waiting_clock.getTimeString()
simstats.intertime = interaction_clock.getTimeString()
simstats.individuals = id
simstats.generations = generation
simstats.best = population[0].fitness
simstats.interactive = interactivity
simstats.interact = interact
simstats.finish = user_exit
# save runtime statistics
iec.saveSimStats(simstats,folder)
# show info
gui.ClrScr(screen)
gui.ShowInfo(screen,'Evolution finished.\nResults stored in \''+folder+'\'\nPress ESC to exit.')
# wait for user to close program
while user_exit == False:
    if gui.Refresh(screen) == 0: user_exit = True
# end program
    