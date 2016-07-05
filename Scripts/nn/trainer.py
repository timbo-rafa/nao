import numpy as np

class Trainer():
  def __init__(self, name, inputs, answers=None):
    self.names = [name]
    self.inputs = np.asarray(inputs, dtype=int)
    if (answers != None):
      self.answers = np.asarray(answers, dtype=int)

    self.inputs = self.inputs.reshape(1,self.inputs.size)
    self.n = self.inputs.shape[0]
    self.input_size = self.inputs.shape[1]


  def append(self, name, inputs, answer):
    if (isinstance(inputs, list)):
      inputs = np.array(inputs, dtype=int)
    if (isinstance(answer, int) or isinstance(answer, float)):
      answer = np.array(answer, dtype=int)
    self.names.append(name)
    self.inputs = np.append(self.inputs, inputs.reshape(1,inputs.size), axis=0)
    self.answers = np.append(self.answers, answer)
    self.n = self.n + 1
