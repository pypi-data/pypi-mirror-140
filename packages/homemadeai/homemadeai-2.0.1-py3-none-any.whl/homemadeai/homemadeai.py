# imports
import random
# imports

# single neuron model
def neuron(input1, input2, weight, noise):
    global out
    avg = (input1 + input2) / 2
    out = avg * weight + random.randint(-noise, noise) * 0.1
# single neuron model