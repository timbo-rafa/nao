import random, math
 
class Trainer:
  # each Trainer object represents a training point with an answer
  def __init__(self, x, y, a):
    self.inputs = []
    self.inputs.append(x)
    self.inputs.append(y)
    self.inputs.append(1) # bias set to 1
    self.answer = a
