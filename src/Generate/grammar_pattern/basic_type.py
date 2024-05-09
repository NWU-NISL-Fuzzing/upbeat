import math
import random

def generate_integer():
    power = random.randint(0, 3)
    width = -(math.pow(10, power))
    return str(random.randint(width, -width))

def generate_double():
    return str(generate_integer()) + (str(random.random())[1:])
