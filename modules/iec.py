# This Python file uses the following encoding: utf-8

from modules import gui
from modules.utils import makedir

def saveSimStats(simstats,folder):
    filename = folder + '/Statistics.txt'
    with open(filename, 'w') as f:
        f.write('Runtime:           '+simstats.totaltime+'\n')
        f.write('Evolution time:    '+simstats.evotime+'\n')
        f.write('Waiting time:      '+simstats.waittime+'\n')
        f.write('Interaction time:  '+simstats.intertime+'\n')
        f.write('Total generations: '+str(simstats.generations)+'\n')
        f.write('Total individuals: '+str(simstats.individuals)+'\n')
        f.write('Best fitness:      '+str(simstats.best)+'\n')
        f.write('Interactive mode:  '+(('Enabled (every '+str(simstats.interact)+' generations)') if simstats.interactive else 'Disabled')+'\n')
        f.write('\nProgram terminated by user.' if simstats.finish else '\nFinishing criterion achieved.')

def saveGeneration(population,folder,id):
    experiment_folder = folder
    generations_folder = folder + "/Generations"
    generation_file = generations_folder + "/" + str(id) + ".generation.txt"
    makedir(experiment_folder)
    makedir(generations_folder)
    with open(generation_file, 'w') as f:
        line = 'ID;Fitness;Time;Distance;RemainingDistance;SpeedAVG;AccelerationAVG;Turn;GoalAngle;Lost;Finished'
        f.write(line+'\n')
        for ind in population:
            line=str(ind.id)
            line+=';'+str(ind.fitness)
            line+=';'+str(ind.results.time)
            line+=';'+str(ind.results.distance)
            line+=';'+str(ind.results.remaining)
            line+=';'+str(ind.results.avg_speed)
            line+=';'+str(ind.results.avg_acc)
            line+=';'+str(ind.results.avg_turn)
            line+=';'+str(ind.results.avg_goalangle)
            line+=';'+str(ind.results.lost)
            line+=';'+str(ind.results.finished)
            f.write(line+'\n')

def saveIndividual(individual,folder):
    experiment_folder = folder
    genotype_folder = folder + "/Individual-genotypes"
    fenotype_folder = folder + "/Individual-fenotypes"
    stats_folder = folder + "/Individual-stats"
    trajectories_folder = folder + "/Individual-trajectories"
    makedir(experiment_folder)
    saveGenotype(individual,genotype_folder)
    saveFenotype(individual,fenotype_folder)
    saveStats(individual,stats_folder)
    saveTrajectory(individual,trajectories_folder)

def saveGenotype(individual,folder):
    filename = folder + '/Individual-ID'+str(individual.id)+'.txt'
    makedir(folder)
    with open(filename, 'w') as f:
        f.write('Genotype of individual ID:' + str(individual.id) + '\n')
        for val in individual.genotype.chromosome:
            f.write(str(val) + '\n')

def saveFenotype(individual,folder):
    filename = folder + '/Individual-ID'+str(individual.id)+'.txt'
    makedir(folder)
    with open(filename, 'w') as f:
        f.write('Fenotype of individual ID:' + str(individual.id))
        mat = individual.fenotype.matrix
        for x in range(len(mat)):
            f.write('\n|')
            for y in range(len(mat[0])):
                f.write(str(mat[x][y])+'|')

def saveStats(individual,folder):
    filename = folder + '/Individual-ID'+str(individual.id)+'.txt'
    makedir(folder)
    with open(filename, 'w') as f:
        line = 'Time;Distance;Speed;Acceleration;Direction;Turn;GoalAngle;X;Y'
        f.write(line+'\n')
        for stat in individual.stats:
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

def saveTrajectory(individual,folder):
    filename = folder + '/Individual-ID'+str(individual.id)+'.png'
    makedir(folder)
    screen = gui.InitSubscreen(0,(0,0),(800,800))
    screen.zoom_mode = 0
    gui.DrawTrajectory(screen, individual.simulator, individual.stats, individual.results)
    gui.ShowInfo(screen,'Individual ID:' + str(individual.id),(10,10),15)
    gui.saveScreen(screen,filename)
    