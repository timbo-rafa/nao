# -*- coding: utf-8 -*-

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

#number of training iterations
TRAIN_ITERATIONS=100
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
HIDDEN_NEURONS=50

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
  red = []
  green = []
  blue = []
  
  if (grayscale):
    pixels = [p[0] for p in list(im.getdata())]
  else:
    for p in list(im.getdata()):
      red.append(p[0]/255.0)
      green.append(p[1]/255.0)
      blue.append(p[2]/255.0)
    #features will be the red pixels then green pixels then blue pixels
    #resulting in 3*width*height features
    pixels = list(red + green + blue)
    #print("green sum={s}".format(s=sum(green)))
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
    ans = [1.0, 0.0]
  else:
    ans = [0.0, 1.0]
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

def readTrainSet():
  train_set = []
  for filename in glob.glob(TRAIN_SET):
    #get the image from file and use the most important central rectangle
    im = I.open(filename).crop((160, 0, 480, 480))
    width, height = im.size
    print("Loaded " + filename + " {w}x{h}".format(w=width, h=height))
    #extract features from the image(its pixels)
    pixels = imageIntoFeatures(im)
    #supervised learning: what is the expected answer for this input?
    isPlant = isPlantPicture(filename)
    answer = expected_answer(isPlant)
    train_set.append( Trainer( filename, pixels, answer ) )
  print("Loaded {n} images. {p} features each".format(
    n=len(train_set), p=len(train_set[0].inputs)))

  return train_set

def newNeuralNetwork(load=LOAD_NN, train=TRAIN_NN, save=SAVE_NN):

  nn = None
  if (load):
    with open(NN_FILENAME, 'rb') as f:
      nn = pickle.load(f)
    print("Loaded neural network from file: " + NN_FILENAME)

  if (train):
    train_set = readTrainSet()
    if (not load):
      n_neurons = len(train_set[0].inputs)
      #initialize nn with
      # number_of_inputs = number of pixels = width * height
      # number of neurons of hidden layer = HIDDEN_NEURONS
      # number of outputs = 2
      nn = NeuralNetwork(n_neurons, HIDDEN_NEURONS, 2)

    print("Training Neural Network")
    for i in range(TRAIN_ITERATIONS):
      print("Training {n}/{t}".format(n=i+1,t=TRAIN_ITERATIONS))
      for t in train_set:
        # train neural network with images
        nn.train(t.inputs, t.answer )
        if (i%10 == 0):
          #print how much nn differ from expected answer
          print("  " + t.name + " Error=" + str(
            round(nn.calculate_total_error([[ t.inputs, t.answer ]] ), 9)))

    for t in train_set:
      print(t.name, round(nn.calculate_total_error([[ t.inputs, t.answer ]] ), 3))
      assertAnswer(nn.feed_forward(t.inputs))

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
      answer = nn.feed_forward(imageIntoFeatures(im))
      #assertAnswer(answer)
      assertAnswerStrong(answer)

    if (SAVE_VISION and count % 60 == 0):
      name = str(count//60) + ".png"
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
