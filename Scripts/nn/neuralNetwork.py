import random
import math
from neuronLayer import NeuronLayer

#
# Shorthand:
#  "pd_" as a variable prefix means "partial derivative"
#  "d_" as a variable prefix means "derivative"
#  "_wrt_" is shorthand for "with respect to"
#  "w_ho" and "w_ih" are the index of weights from hidden to output layer neurons and input to hidden layer neurons respectively
#
# Comment references:
#
# [1] Wikipedia article on Backpropagation
#  http://en.wikipedia.org/wiki/Backpropagation#Finding_the_derivative_of_the_error
# [2] Neural Networks for Machine Learning course on Coursera by Geoffrey Hinton
#  https://class.coursera.org/neuralnets-2012-001/lecture/39
# [3] The Back Propagation Algorithm
#  https://www4.rgu.ac.uk/files/chapter3%20-%20bp.pdf

class NeuralNetwork:
  LEARNING_RATE = 0.05

  def __init__(self, num_inputs, num_hidden, num_outputs, hidden_layer_weights = None, hidden_layer_bias = None, output_layer_weights = None, output_layer_bias = None):
    self.num_inputs = num_inputs

    self.hidden_layer = NeuronLayer(num_hidden, hidden_layer_bias)
    self.output_layer = NeuronLayer(num_outputs, output_layer_bias)

    self.init_weights_from_inputs_to_hidden_layer_neurons(hidden_layer_weights)
    self.init_weights_from_hidden_layer_neurons_to_output_layer_neurons(output_layer_weights)

  def init_weights_from_inputs_to_hidden_layer_neurons(self, hidden_layer_weights):
    weight_num = 0
    for h in range(len(self.hidden_layer.neurons)):
      for i in range(self.num_inputs):
        if not hidden_layer_weights:
          self.hidden_layer.neurons[h].weights.append(random.random())
        else:
          self.hidden_layer.neurons[h].weights.append(hidden_layer_weights[weight_num])
        weight_num += 1

  def init_weights_from_hidden_layer_neurons_to_output_layer_neurons(self, output_layer_weights):
    weight_num = 0
    for o in range(len(self.output_layer.neurons)):
      for h in range(len(self.hidden_layer.neurons)):
        if not output_layer_weights:
          self.output_layer.neurons[o].weights.append(random.random())
        else:
          self.output_layer.neurons[o].weights.append(output_layer_weights[weight_num])
        weight_num += 1

  def inspect(self):
    print('------')
    print('* Inputs: {}'.format(self.num_inputs))
    print('------')
    print('Hidden Layer')
    self.hidden_layer.inspect()
    print('------')
    print('* Output Layer')
    self.output_layer.inspect()
    print('------')

  def feed_forward(self, inputs):
    hidden_layer_outputs = self.hidden_layer.feed_forward(inputs)
    return self.output_layer.feed_forward(hidden_layer_outputs)

  # Uses online learning, ie updating the weights after each training case
  def train(self, training_inputs, training_outputs):
    self.feed_forward(training_inputs)

    # 1. Output neuron deltas
    pd_errors_wrt_output_neuron_total_net_input = [0] * len(self.output_layer.neurons)
    for o in range(len(self.output_layer.neurons)):

      # dE/dZj
      pd_errors_wrt_output_neuron_total_net_input[o] = self.output_layer.neurons[o].calculate_pd_error_wrt_total_net_input(training_outputs[o])

    # 2. Hidden neuron deltas
    pd_errors_wrt_hidden_neuron_total_net_input = [0] * len(self.hidden_layer.neurons)
    for h in range(len(self.hidden_layer.neurons)):

      # We need to calculate the derivative of the error with respect to the output of each hidden layer neuron
      # dE=dyj = sum dE/dzj * dz/dyj = sum dE/dzj * wij
      d_error_wrt_hidden_neuron_output = 0
      for o in range(len(self.output_layer.neurons)):
        d_error_wrt_hidden_neuron_output += pd_errors_wrt_output_neuron_total_net_input[o] * self.output_layer.neurons[o].weights[h]

      # dE/dZj = dE/dYj * dzj/d
      pd_errors_wrt_hidden_neuron_total_net_input[h] = d_error_wrt_hidden_neuron_output * self.hidden_layer.neurons[h].calculate_pd_total_net_input_wrt_input()

    # 3. Update output neuron weights
    for o in range(len(self.output_layer.neurons)):
      for w_ho in range(len(self.output_layer.neurons[o].weights)):

        # dEj/dWij = dE/dzj * dzi/ dwij
        pd_error_wrt_weight = pd_errors_wrt_output_neuron_total_net_input[o] * self.output_layer.neurons[o].calculate_pd_total_net_input_wrt_weight(w_ho)

        # deltaW = a * dEj /dwi
        self.output_layer.neurons[o].weights[w_ho] -= self.LEARNING_RATE * pd_error_wrt_weight

    # 4. Update hidden neuron weights
    for h in range(len(self.hidden_layer.neurons)):
      for w_ih in range(len(self.hidden_layer.neurons[h].weights)):

        pd_error_wrt_weight = pd_errors_wrt_hidden_neuron_total_net_input[h] * self.hidden_layer.neurons[h].calculate_pd_total_net_input_wrt_weight(w_ih)

        self.hidden_layer.neurons[h].weights[w_ih] -= self.LEARNING_RATE * pd_error_wrt_weight

  def calculate_total_error(self, training_sets):
    total_error = 0
    for t in range(len(training_sets)):
      training_inputs, training_outputs = training_sets[t]
      self.feed_forward(training_inputs)
      for o in range(len(training_outputs)):
        total_error += self.output_layer.neurons[o].calculate_error(training_outputs[o])
    return total_error
