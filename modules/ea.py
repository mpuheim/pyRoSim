#!/usr/bin/python
# This Python file uses the following encoding: utf-8

import random
            
class Individual():
    # Individual class
    def __init__(self, length):
        self.chromosome = [random.uniform(-1.0, 1.0) for j in range(length)]
        self.fitness = 0
    # Mutation operation
    def mutate(self,mutation=10):
        for i in range(len(self.chromosome)):
            rand = random.randint(0,99)
            if rand < mutation:
                self.chromosome[i] += random.uniform(-0.5, 0.5)
                if self.chromosome[i] < -1: self.chromosome[i] = -1
                elif self.chromosome[i] > 1: self.chromosome[i] = 1
    # Crossover operation
    def crossover(self,other,crosspoints=3):
        if (crosspoints >= len(self.chromosome)):
            raise ValueError('Error. Number of crossing points cannot be larger than number of genes - 1.')
        lst = list(range(1, len(self.chromosome)))
        points = []
        for i in range(crosspoints):
            index = random.randint(1, len(lst)-1)
            points.append(lst[index])
            lst.pop(index)
        points.append(len(self.chromosome))
        points.sort()
        switch = True
        last = 0
        child = Individual(len(self.chromosome))
        for i in points:
            if switch:
                child.chromosome[last:i] = self.chromosome[last:i]
                switch = False
            else:
                child.chromosome[last:i] = other.chromosome[last:i]
                switch = True
            last = i
        return child
