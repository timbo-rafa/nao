import math
import random

class Neuron:
  def __init__(self, bias):
    self.bias = bias
    self.weights = []

  def calculate_output(self, inputs):
    self.inputs = inputs
    self.output = self.squash(self.calculate_total_net_input())
    return self.output

  def calculate_total_net_input(self):
    total = 0
    for i in range(len(self.inputs)):
      total += self.inputs[i] * self.weights[i]
    return total + self.bias

  # Apply the logistic function to squash the output of the neuron
  # The result is sometimes referred to as 'net' [2] or 'net' [1]
  def squash(self, total_net_input):
    return 1 / (1 + math.exp(-total_net_input))

  # Determine how much the neuron's total input has to change to move closer to the expected output
  #
  # the derivative of the output with respect to the total net input (dy/dz) we can calculate
  # the partial derivative of the error with respect to the total net input.
  # This value is also known as the delta () [1]
  #
  def calculate_pd_error_wrt_total_net_input(self, target_output):
    return self.calculate_pd_error_wrt_output(target_output) * self.calculate_pd_total_net_input_wrt_input();

  # The error for each neuron is calculated by the Mean Square Error method:
  def calculate_error(self, target_output):
    return 0.5 * (target_output - self.output) ** 2

  # The partial derivate of the error with respect to actual output then is calculated by:
  # = 2 * 0.5 * (target output - actual output) ^ (2 - 1) * -1
  # = -(target output - actual output)
  #
  # The Wikipedia article on backpropagation [1] simplifies to the following, but most other learning material does not [2]
  # = actual output - target output
  #
  # Alternative, you can use (target - output), but then need to add it during backpropagation [3]
  #
  def calculate_pd_error_wrt_output(self, target_output):
    return -(target_output - self.output)

  # The total net input into the neuron is squashed using logistic function to calculate the neuron's output:
  #
  # The derivative (not partial derivative since there is only one variable) of the output then is:
  def calculate_pd_total_net_input_wrt_input(self):
    return self.output * (1 - self.output)

  # The total net input is the weighted sum of all the inputs to the neuron and their respective weights:
  #
  # The partial derivative of the total net input with respective to a given weight (with everything else held constant) then is:
  def calculate_pd_total_net_input_wrt_weight(self, index):
    return self.inputs[index]
