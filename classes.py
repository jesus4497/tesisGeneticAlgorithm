#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy.random as rand
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt


class Individual:
    def __init__(self, c, d):
        self.values = [[rand.normal() for _ in range(c + 1)] for _ in range(d)]
        self.fitness = None

    def evaluate(self, lookupTable):
        self.fitness = 0
        for x in lookupTable.keys():
            image = 0
            for variable in self.values:
                for power, coefficient in enumerate(variable):
                    image += coefficient * x ** power
            target = lookupTable[x]
            mse = (target - image) ** 2
            self.fitness += mse

    def mutate(self, rate):
        self.values = [[rand.uniform(c - rate, c + rate) for c in variable]
                       for variable in self.values]

    def xover(self, split, mother, c):
        xover = []
        for index, variable in enumerate(self.values):
            i = 0
            while (i < split):
                xover.append(variable[i])
                i += 1
        for index, variable in enumerate(mother.values):
            while (i < c + 1):
                xover.append(variable[i])
                i += 1
        self.values = [xover]

    def roulette(self, filter):
        if (rand.random() > filter):
            return True
        else:
            return False

    def display(self):
        # print('Formato polinomico de numpy:')
        for index, variable in enumerate(self.values):
            # print(variable[::-1])
            return variable[::-1]

    def roundCoefficients(self):
        self.values = [[round(value, 4) for value in variable]
                       for variable in self.values]


class Population:

    def __init__(self, c, d, size=100):
        self.individuals = [Individual(c, d) for _ in range(size)]
        self.best = [Individual(c, d)]
        self.rate = 0.1
        self.split = round(c / 2)
        self.filter = 0.9
        self.c = c

    def sort(self):
        self.individuals = sorted(self.individuals, key=lambda
                                  indi: indi.fitness)

    def evaluate(self, lookupTable):
        for indi in self.individuals:
            indi.evaluate(lookupTable)

    def enhance(self, lookupTable):
        newIndividuals = []
        for individual in self.individuals[:10]:
            newIndividuals.append(deepcopy(individual))
            for xindividual in self.individuals[10:15]:
                mother = deepcopy(individual)
                offspring = deepcopy(xindividual)
                offspring.xover(self.split, mother, self.c)
                newIndividuals.append(offspring)
            for _ in range(5):
                newIndividual = deepcopy(individual)
                newIndividual.mutate(self.rate)
                newIndividuals.append(newIndividual)
        for individual in self.individuals[10:]:
            luckyIndividual = deepcopy(individual)
            if (luckyIndividual.roulette(self.filter) is True):
                newIndividuals.append(luckyIndividual)
        self.individuals = newIndividuals
        self.evaluate(lookupTable)
        self.sort()
        self.best.append(self.individuals[0])
        if self.best[-1].fitness == self.best[-2].fitness:
            self.rate += 0.01
        # else:
            # self.rate = 0.1

    def plot2D(self, x, y, generation, path, maxGen):
        X = np.linspace(min(x), max(x))
        Y = [sum(c * x ** p
                 for p, c in enumerate(variable))
             for variable in self.best[-1].values
             for x in X]
        plt.clf()
        plt.scatter(x, y, color='#01D288', s=60, label='Objetivo')
        plt.plot(X, Y, color='#24A599', label='Proyección')
        plt.legend(['Proyección', 'Objetivo'], ncol=2)
        plt.axis('off')
        plt.title('Generación: ' + str(generation) + '\n' +
                  'Error: ' + str(self.best[-1].fitness), size=16)
        plt.savefig(path + '/' + str(generation) + 'scatter.png',
                    figsize=(7, 5), bbox_inches=0, font='Trebuchet MS')
        if generation == maxGen - 1:
            plt.savefig(path + '/web/img/ultimate.png', figsize=(7, 5),
                        bbox_inches=0, font='Trebuchet MS')

    def plotBar(self, x, y, generation, path, maxGen):
        X = np.linspace(min(x), max(x))
        Y = [sum(c * x ** p
                 for p, c in enumerate(variable))
             for variable in self.best[-1].values
             for x in X]
        plt.clf()
        plt.scatter(x, y, color='#66CC66', s=60, label='Objetivo')
        plt.bar(X, Y, color='#24A599', label='Proyección')
        plt.legend(['Proyección', 'Objetivo'], ncol=2)
        plt.axis('off')
        plt.title('Generación: ' + str(generation) + '\n' +
                  'Error: ' + str(self.best[-1].fitness), size=16)
        plt.savefig(path + '/' + str(generation) + 'bar.png', figsize=(7, 5),
                    bbox_inches=0, font='Trebuchet MS')
        if generation == maxGen - 1:
            plt.savefig(path + '/web/img/ultimateBar.png', figsize=(7, 5),
                        bbox_inches=0, font='Trebuchet MS')
