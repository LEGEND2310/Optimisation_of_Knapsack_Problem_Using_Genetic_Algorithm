#Importing the required libraries.
from random import random
from typing import Callable, List, Tuple
from random import choices, randint, randrange
from functools import partial
import time

#Defining each variable and function type

Genome = List[int]  #Genome is just a list of 0,1 eg> g1 = [0,1,1,0,0], g2 = [1,0,1,1,0]
Population = List[Genome]  #Population is a list of all genomes eg> p1 = [g1,g2,...]
FitnessFunc = Callable[[Genome], float]  #The fitness function takes a Genome and returns a fitness value for the given Genome
PopulationFunc = Callable[[],Population]  #The population function generates a list of Genomes, the list is called the current generation population
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]  #The Selection function takes a population and the fitness function and gives us a pair of genomes (called parents) prefering genomes with higher fitness values
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]  #The Crossover Function takes two parent genomes sptilts them randomly at an index and then switches the sliced parts of the genome
MutationFunc = Callable[[Genome], Genome]  #Mutation function changes the given number of values in a genome depending on the given value of probability and returns the mutated genome

#A general purpose thing object to store each item, an named tupple could also be used for the same

class Thing:
    def __init__(self,name,value,weight):
        self.name = name
        self.value = value
        self.weight = weight
# Thing = namedtuple('Thing',['name','value','weight'])

things = []

#defining all of the above mentioned functions

def generate_genome(length: int) -> Genome:
    return choices([0,1],k=length)

def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]

def fitness(genome: Genome, things: List[Thing], weight_limit: float) -> float:
    if len(genome) != len(things):
        raise ValueError("Genome and Thimgs must be of same length")
    
    weight  = 0
    value = 0
    for i, thing in enumerate(things):
        if genome[i] == 1:
            weight += thing.weight
            value += thing.value

            if weight > weight_limit:
                return 0
    
    return value

def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population= population,
        weights= [fitness_func(genome) for genome in population],
        k=2
    )

def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome,Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b need to be of the same length")

    length = len(a)
    if length < 2:
        return a,b
    
    p = randint(1,length-1)
    return a[:p] + b[p:] , b[:p] + a[p:]

def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random() > probability else abs(genome[index]-1)
    return genome

def run_evolution(
    populate_func: PopulationFunc,
    fitness_func: FitnessFunc,
    fitness_limit: float,
    selection_func: SelectionFunc = selection_pair,
    crossover_func: CrossoverFunc = single_point_crossover,
    mutation_func: MutationFunc = mutation,
    generation_limit: int = 100) -> Tuple[Population, int]:

    population = populate_func()

    for i in range(generation_limit):
        population = sorted(
            population,
            key= lambda genome: fitness_func(genome),
            reverse= True
        )

        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[:2]

        for j in range(int(len(population)/2)-1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    population = sorted(
        population,
        key= lambda genome: fitness_func(genome),
        reverse= True
    )

    return population, i

def genome_to_things(genome: Genome, things: List[Thing]) -> List[Thing]:
    result = []
    for i,thing in enumerate(things):
        if genome[i]==1:
            result += [thing.name]
    
    return result

#Taking input of the list of items

print("Enter the number of items you want to choose from: ")
num_items = int(input())

for i in range(num_items):
    print(f"Enter the Name item number {i+1}: ")
    item_name = input()
    print(f"Enter the Value item number {i+1}: ")
    item_value = float(input())
    print(f"Enter the Weight item number {i+1}: ")
    item_weight = float(input())
    print("\n")
    things.append(Thing(item_name,item_value,item_weight))

#defining the weight and fitness limits

print("Enter the weight limit: ")
inp_weight_limit = float(input())

print("\nEnter the max value you want out of the solution (fitness limit): ")
inp_fitness_limit = float(input())

start = time.time()
population, generations = run_evolution(
    populate_func= partial(
        generate_population, size = 10, genome_length = len(things)
    ),
    fitness_func=partial(
        fitness, things = things, weight_limit = inp_weight_limit
    ),
    fitness_limit= inp_fitness_limit,
    generation_limit=100
)
end = time.time()

print(f"\nnumber of generations: {generations}")
print(f"time:{end - start}s")
print(f"best solution: {genome_to_things(population[0], things)}")
print(f"value: {fitness(population[0], things, inp_weight_limit)}")