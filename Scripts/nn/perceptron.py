import random

class Perceptron:
  def __init__(self, n, c):
    self.weights = []
    self.c = c
    for i in range(0, n):
      self.weights.append(random.uniform(-1, 1))
 
  def train(self, inputs, desired):
    guess = self.feedforward(inputs)
    error = desired - guess
    for i in range(0, len(self.weights)):
      self.weights[i] += self.c * error * inputs[i]
 
  def feedforward(self, inputs):
    sum = 0
    for i in range(0, len(self.weights)):
      sum += inputs[i] * self.weights[i]
    return self.activate(sum)
 
  def activate(self, sum):
    if sum > 0:
      return 1
    else:
      return -1
 
  def getWeights(self):
    return self.weights
