# -*- coding: utf-8 -*-

import vrep,time,sys
import matplotlib.pyplot as plt
from PIL import Image as I
import array
import glob
from nn.trainer import Trainer
from itertools import repeat
import math
import pickle
from sklearn.neural_network import MLPClassifier
import numpy as np

#number of training iterations
TRAIN_ITERATIONS=1
#files used for training
TRAIN_SET="img/*.png"
#fille to save the neural network instance
NN_FILENAME="neuralNetwork.save"
#load nn from file?
LOAD_NN=False
#train nn?
TRAIN_NN=True
#save nn to file?
SAVE_NN=False
#save what the nao sees to use as database
SAVE_VISION=False
# counter to use as filename for database files
COUNTER = 1
#number of neurons in hidden layer
HIDDEN_NEURONS=5

# Thresholds to assert if we (dont) see the plant
THRESHOLD_POSITIVE = 0.75
THRESHOLD_NEGATIVE = 0.2
THRESHOLD_DOUBT_POSITIVE = 0.6
THRESHOLD_DOUBT_NEGATIVE = 0.4

#convert the image into features
#returns the image's pixels
def imageIntoFeatures(im, grayscale=True):
  if (grayscale):
    im = im.convert("LA")
  if (grayscale):
    pixels = np.array(list(im.getdata()))
    pixels = np.delete(pixels, [[1]], axis=1).flatten()
  #print("imageIntoFeatures:")
  #print(pixels.shape)
  return pixels

#is the picture a plant?
#used for supervised learning
def isPlantPicture(filename):
  return "y" in filename

#the first output says how sure the network is that the image has a plant
#the second output says how sure the network is that the image is not a plant
#both values close to 0.5 in the answer would indicate uncertainty
def expected_answer(isPlant):
  if isPlant:
    ans = 255
  else:
    ans = 0
  return ans

#convert answer to a human readable answer
def assertAnswer(answer):
  print("I am " + str(round(answer[0],4) * 100) + "% sure I see a plant.")
  print("I am " + str(round(answer[1],4) * 100) + "% sure I don't see a plant.")

#make an affirmation based on network's answer
def assertAnswerStrong(answer):
  pPlant = answer[0]
  pNotPlant = answer[1]

  if   (pPlant    > THRESHOLD_POSITIVE       or pNotPlant < THRESHOLD_NEGATIVE):
    print("I see a plant.")
  elif (pPlant    > THRESHOLD_DOUBT_POSITIVE or pNotPlant < THRESHOLD_DOUBT_NEGATIVE):
    print("I think I see a plant.")
  elif (pNotPlant > THRESHOLD_POSITIVE       or pPlant    < THRESHOLD_NEGATIVE):
    print("I don't see a plant.")
  elif (pNotPlant > THRESHOLD_DOUBT_POSITIVE or pPlant    < THRESHOLD_DOUBT_NEGATIVE):
    print("I think I don't see a plant.")
  else:
    print("I am not sure of what I see.")

def readTrainSet(train_set=TRAIN_SET):
  for filename in glob.glob(train_set):
    #get the image from file and use the most important central rectangle
    im = I.open(filename).crop((160, 0, 480, 480))
    width, height = im.size
    print("Loaded " + filename + " {w}x{h}={f} features".format(
      w=width, h=height,f=width*height))
    #extract features from the image(its pixels)
    pixels = imageIntoFeatures(im)
    #supervised learning: what is the expected answer for this input?
    isPlant = isPlantPicture(filename)
    answer = expected_answer(isPlant)

    try:
      trainer.append(filename, pixels, answer)
    except NameError:
      trainer = Trainer(filename, pixels, answer)

    #print("Trainer Shape:", trainer.inputs.shape)
  print("Loaded {n} images. {p} features each".format(
    n=trainer.n, p=trainer.input_size))

  return trainer

def newMLP(n_neurons=HIDDEN_NEURONS):
  nn = MLPClassifier(hidden_layer_sizes=(n_neurons,),
    #algorithm='l-bfgs',
    random_state=1, learning_rate='constant',
    learning_rate_init=0.05)
  return nn

def newNeuralNetwork(load=LOAD_NN, train=TRAIN_NN, save=SAVE_NN):

  nn = None
  if (load):
    with open(NN_FILENAME, 'rb') as f:
      nn = pickle.load(f)
    print("Loaded neural network from file: " + NN_FILENAME)

  if (train):
    trainer = readTrainSet()
    print("Trainer")
    print(trainer.inputs.shape, trainer.answers.shape)
    if (not load):
      #initialize nn with
      # number_of_inputs = number of pixels = width * height
      # number of neurons of hidden layer = HIDDEN_NEURONS
      # number of outputs = 2
      nn = newMLP()

    print("Training Neural Network")
    nn.fit(trainer.inputs, trainer.answers )
    print("Training Score:",
      trainer.inputs, trainer.answers, nn.score(trainer.inputs, trainer.answers))

    #trainer = readTrainSet("img/y*.png")
    #nn.fit(trainer.inputs, trainer.answers)
    
  if (save and nn):
    print("Saving Neural Network as " + NN_FILENAME)
    with open(NN_FILENAME, 'wb') as f:
      pickle.dump(nn, f , pickle.HIGHEST_PROTOCOL)

  if (nn):
    pass
    #nn.inspect()
  return nn

def streamVisionSensor(visionSensorName,clientID,pause=0.0001):

  nn = newNeuralNetwork()
  #print("Neural Network num_inputs:{n}".format(n=nn.num_inputs))

  #Get the handle of the vision sensor
  res1,visionSensorHandle=vrep.simxGetObjectHandle(clientID,visionSensorName,vrep.simx_opmode_oneshot_wait)
  #Get the image
  res2,resolution,image=vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_streaming)
  #Allow the display to be refreshed
  plt.ion()
  #Initialiazation of the figure
  time.sleep(0.5)
  res,resolution,image=vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_buffer)
  im = I.new("RGB", (resolution[0], resolution[1]), "white")
  #Give a title to the figure
  im = im.crop((160, 0, 480, 480))
  fig = plt.figure(1)    
  fig.canvas.set_window_title(visionSensorName)
  #inverse the picture
  plotimg = plt.imshow(im,origin='lower')
  #Let some time to Vrep in order to let him send the first image, otherwise the loop will start with an empty image and will crash
  time.sleep(1)
  
  count = COUNTER
  while (vrep.simxGetConnectionId(clientID)!=-1):
    #Get the image of the vision sensor
    res,resolution,image=vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_buffer)
    #Transform the image so it can be displayed using pyplot
    image_byte_array = array.array('b',image)
    im = I.frombuffer("RGB", (resolution[0],resolution[1]), image_byte_array, "raw", "RGB", 0, 1)
    im = im.crop((160, 0, 480, 480))
    #Update the image

    plotimg.set_data(im)
    #Refresh the display
    plt.axis("off")
    plt.show()
    #The mandatory pause ! (or it'll not work)
    plt.pause(pause)
    if (nn):
      # feed the neural network with the image and get its prediction (if it has a plant)

      trainer = Trainer("live", imageIntoFeatures(im))
      answer = nn.predict(trainer.inputs)
      print(answer)
      #assertAnswer(answer)
      #assertAnswerStrong(answer)

    if (SAVE_VISION and count % 60 == 0):
      name = str(count//60) + ".png"
      print("Saving " + name)
      im.save(name)
    count += 1
  print('End of Simulation')
    
def getVisionSensor(visionSensorName,clientID):
  #Get the handle of the vision sensor
  res1,visionSensorHandle=vrep.simxGetObjectHandle(clientID,visionSensorName,vrep.simx_opmode_oneshot_wait)
  #Get the image
  res2,resolution,image=vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_streaming)
  time.sleep(1)
  while (vrep.simxGetConnectionId(clientID)!=-1): 
    #Get the image of the vision sensor
    res,resolution,image=vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_buffer)
    print(resolution)
  print('End of Simulation')
    
if __name__ == '__main__':

  vrep.simxFinish(-1)
  clientID=vrep.simxStart('127.0.0.2',19999,True,True,5000,5)
  if clientID!=-1:
    print('Connected to remote API server')
    #Get and display the pictures from the camera
    streamVisionSensor('NAO_vision1',clientID,0.0001)
    #Only get the image
    #getVisionSensor('NAO_vision1',clientID)

  else:
    print('Connection non successful')
    sys.exit('Could not connect')
