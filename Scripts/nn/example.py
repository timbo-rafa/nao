
# Blog post example:
from neuralNetwork import NeuralNetwork
import random

nn = NeuralNetwork(2, 2, 2, hidden_layer_weights=[0.15, 0.2, 0.25, 0.3], hidden_layer_bias=0.35, output_layer_weights=[0.4, 0.45, 0.5, 0.55], output_layer_bias=0.6)
for i in range(10000):
  nn.train([0.05, 0.1], [0.01, 0.99])
  print(i, round(nn.calculate_total_error([[[0.05, 0.1], [0.01, 0.99]]]), 9))

print("Training example:in=[0.05, 0.1], r=[0.01, 0.99]", nn.feed_forward([0.05, 0.1]))
r1 = random.random()
r2 = random.random()
print("Random example:in=[ {r1}, {r2} ] r=".format(r1=r1, r2=r2), nn.feed_forward([r1, r2]))

# XOR example:

# training_sets = [
#   [[0, 0], [0]],
#   [[0, 1], [1]],
#   [[1, 0], [1]],
#   [[1, 1], [0]]
# ]

# nn = NeuralNetwork(len(training_sets[0][0]), 5, len(training_sets[0][1]))
# for i in range(10000):
#   training_inputs, training_outputs = random.choice(training_sets)
#   nn.train(training_inputs, training_outputs)
#   print(i, nn.calculate_total_error(training_sets))




