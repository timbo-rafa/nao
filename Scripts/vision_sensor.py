# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 15:30:54 2015

@author: Pierre Jacquot
"""

import vrep,time,sys
import matplotlib.pyplot as plt
from PIL import Image as I
import array
import ImageChops
import glob
from nn.neuralNetwork import NeuralNetwork
from nn.trainer import Trainer
from itertools import repeat
import math
import cPickle as pickle

TRAIN_REPEAT=int(8/NeuralNetwork.LEARNING_RATE)
SAVE_VISION=False
NN_FILENAME="neuralNetwork.save"
LOAD_NN=True
TRAIN_NN=False
SAVE_NN=False
COUNTER = 3451

THRESHOLD_POSITIVE = 0.7
THRESHOLD_NEGATIVE = 0.2
THRESHOLD_DOUBT_POSITIVE = 0.55
THRESHOLD_DOUBT_NEGATIVE = 0.4


def imageIntoFeatures(im):
  #im = im.convert("LA")
  red = []
  green = []
  blue = []
  for p in list(im.getdata()):
    red.append(p[0])
    green.append(p[1])
    blue.append(p[2])
  #gray_pixels = [p[0] for p in list(im.getdata())]
  pixels = list(red + green + blue)
  return pixels

def isPlantPicture(filename):
  return "y" in filename

def expected_answer(isPlant):
  if isPlant:
    ans = [1.0, 0.0]
  else:
    ans = [0.0, 1.0]
  return ans

def assertAnswer(answer):
  print("I am " + str(round(answer[0],4) * 100) + "% sure I see a plant.")
  print("I am " + str(round(answer[1],4) * 100) + "% sure I don't see a plant.")

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

def readTrainSet():
  train_set = []
  for filename in glob.glob("img/*.png"):
    im = I.open(filename)
    width, height = im.size
    print("Loaded " + filename + " {w}x{h}".format(w=width, h=height))
    pixels = imageIntoFeatures(im)
    isPlant = isPlantPicture(filename)
    answer = expected_answer(isPlant)
    train_set.append( Trainer( filename, pixels, answer ) )
  print("Loaded {n} images. {p} features each".format(
    n=len(train_set), p=len(train_set[0].inputs)))

  return train_set

def trainNeuralNetwork(load=LOAD_NN, train=TRAIN_NN, save=SAVE_NN):

  nn = None
  if (load):
    with open(NN_FILENAME, 'rb') as f:
      nn = pickle.load(f)
    print("Loaded neural network from file: " + NN_FILENAME)
  else:
    nn = NeuralNetwork(len(train_set[0].inputs), 1, 2)

  if (train):
    train_set = readTrainSet()

    print("Training Neural Network")
    for i in range(TRAIN_REPEAT):
      print("Training {n}/{t}".format(n=i+1,t=TRAIN_REPEAT))
      for t in train_set:
        nn.train(t.inputs, t.answer )
        print(" ", t.name, round(nn.calculate_total_error([[ t.inputs, t.answer ]] ), 9))

    for t in train_set:
      print(t.name, round(nn.calculate_total_error([[ t.inputs, t.answer ]] ), 3))
      assertAnswer(nn.feed_forward(t.inputs))

  if (save):
    with open(NN_FILENAME, 'wb') as f:
      pickle.dump(nn, f , pickle.HIGHEST_PROTOCOL)

  #sys.exit()
  return nn


def streamVisionSensor(visionSensorName,clientID,pause=0.0001):

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
  fig = plt.figure(1)    
  fig.canvas.set_window_title(visionSensorName)
  #inverse the picture
  plotimg = plt.imshow(im,origin='lower')
  #Let some time to Vrep in order to let him send the first image, otherwise the loop will start with an empty image and will crash
  time.sleep(1)

  nn = trainNeuralNetwork()
  
  filename = 1
  #im = None
  count = COUNTER
  while (vrep.simxGetConnectionId(clientID)!=-1):
    #Get the image of the vision sensor
    res,resolution,image=vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_buffer)
    #Transform the image so it can be displayed using pyplot
    image_byte_array = array.array('b',image)
    im = I.frombuffer("RGB", (resolution[0],resolution[1]), image_byte_array, "raw", "RGB", 0, 1)
    # Grayscale
    #im = im.convert('LA')
    #Update the image

    plotimg.set_data(im)
    #Refresh the display
    plt.axis("off")
    plt.show()
    #The mandatory pause ! (or it'll not work)
    plt.pause(pause)
    answer = nn.feed_forward(imageIntoFeatures(im))
    assertAnswer(answer)
    assertAnswerStrong(answer)
    if (SAVE_VISION and count % 100 == 0):
      name = str(count//100) + ".png"
      print("Saving " + name)
      im.save(name)
    count += 1
  print 'End of Simulation'
    
def getVisionSensor(visionSensorName,clientID):
  #Get the handle of the vision sensor
  res1,visionSensorHandle=vrep.simxGetObjectHandle(clientID,visionSensorName,vrep.simx_opmode_oneshot_wait)
  #Get the image
  res2,resolution,image=vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_streaming)
  time.sleep(1)
  while (vrep.simxGetConnectionId(clientID)!=-1): 
    #Get the image of the vision sensor
    res,resolution,image=vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_buffer)
    print resolution
  print 'End of Simulation'
    
if __name__ == '__main__':


  vrep.simxFinish(-1)
  clientID=vrep.simxStart('127.0.0.2',19999,True,True,5000,5)
  if clientID!=-1:
    print 'Connected to remote API server'
    #Get and display the pictures from the camera
    streamVisionSensor('NAO_vision1',clientID,0.0001)
    #Only get the image
    #getVisionSensor('NAO_vision1',clientID)

  else:
    print 'Connection non successful'
    sys.exit('Could not connect')
