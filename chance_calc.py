import random

def calc_chance(population, weights):
    for (item, weight) in zip(population, weights):
        chance = round((weight / sum(weights)) * 100, 2)
        print(f'{item=}, {weight=}, {chance=}')
    sample = random.choices(population, weights, k=10)
    print(f'{sample=}')

pix_types = ['basic', 'mask', 'furry', 'grated', 'combined', 'linear', 'wild', 'thorny', 'poisonous', 'mystical', 'elemental', 'ancient']
pix_type_weights = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
calc_chance(pix_types, pix_type_weights)