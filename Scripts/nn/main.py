from perceptron import Perceptron
from trainer import Trainer
import random

training = []
 
points = 2000
count = 0
xmin = -400
ymin = -100
xmax =  400
ymax =  100
 
def f(x):
  return 0.4*x+1
 
def slope():
  x1 = xmin;
  y1 = f(x1);
  x2 = xmax;
  y2 = f(x2); 
  return (y2-y1)/(x2-x1)
 
ptron = Perceptron(3, 0.001)
 
# Constructs training points
for i in range(0, points):
  x = random.uniform(xmin, xmax)
  y = random.uniform(ymin, ymax)
  answer = 1
  if y < f(x):
    answer = -1
  training.append(Trainer(x, y, answer))
  ptron.train(training[i].inputs, training[i].answer)
  weights = ptron.getWeights();
  x1 = xmin;
  y1 = (-weights[2] - weights[0]*x1)/weights[1]
  x2 = xmax;
  y2 = (-weights[2] - weights[0]*x2)/weights[1]
  print (y2-y1)/(x2-x1)
 
print "Answer: "+str(slope())
