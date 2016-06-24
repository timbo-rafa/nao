# -*- encoding: UTF-8 -*-

''' Whole Body Motion: kick '''
''' This example is only compatible with NAO '''

import argparse
import motion
import time
import almath
import vrep,sys
from naoqi import ALProxy
from manage_joints import get_first_handles,JointControl

CHOREO_PORT=26000
VREP_PORT=25000

def computePath(proxy, effector, frame):
  dx      = 0.05                 # translation axis X (meters)
  dz      = 0.05                 # translation axis Z (meters)
  dwy     = 5.0*almath.TO_RAD    # rotation axis Y (radian)

  useSensorValues = False

  path = []
  currentTf = []
  try:
    currentTf = proxy.getTransform(effector, frame, useSensorValues)
  except Exception, errorMsg:
    print str(errorMsg)
    print "This example is not allowed on this robot."
    exit()

  # 1
  targetTf  = almath.Transform(currentTf)
  targetTf *= almath.Transform(-dx, 0.0, dz)
  targetTf *= almath.Transform().fromRotY(dwy)
  path.append(list(targetTf.toVector()))

  # 2
  targetTf  = almath.Transform(currentTf)
  targetTf *= almath.Transform(dx, 0.0, dz)
  path.append(list(targetTf.toVector()))

  # 3
  path.append(currentTf)

  return path

def vrep_connect():
  print '================ Program Sarted ================'

  vrep.simxFinish(-1)
  clientID=vrep.simxStart('127.0.0.1',25000,True,True,5000,5)
  if clientID!=-1:
    print 'Connected to remote API server'
  else:
    print 'Connection non successful'
    sys.exit('Could not connect')
  return clientID

def main(robotIP, PORT=CHOREO_PORT):
  ''' Example of a whole body kick
  Warning: Needs a PoseInit before executing
    Whole body balancer must be inactivated at the end of the script
  '''

  clientID = vrep_connect()

  Head_Yaw=[];Head_Pitch=[];
  L_Hip_Yaw_Pitch=[];L_Hip_Roll=[];L_Hip_Pitch=[];L_Knee_Pitch=[];L_Ankle_Pitch=[];L_Ankle_Roll=[];
  R_Hip_Yaw_Pitch=[];R_Hip_Roll=[];R_Hip_Pitch=[];R_Knee_Pitch=[];R_Ankle_Pitch=[];R_Ankle_Roll=[];
  L_Shoulder_Pitch=[];L_Shoulder_Roll=[];L_Elbow_Yaw=[];L_Elbow_Roll=[];L_Wrist_Yaw=[]
  R_Shoulder_Pitch=[];R_Shoulder_Roll=[];R_Elbow_Yaw=[];R_Elbow_Roll=[];R_Wrist_Yaw=[]
  R_H=[];L_H=[];R_Hand=[];L_Hand=[];
  Body = [Head_Yaw,Head_Pitch,L_Hip_Yaw_Pitch,L_Hip_Roll,L_Hip_Pitch,L_Knee_Pitch,L_Ankle_Pitch,L_Ankle_Roll,R_Hip_Yaw_Pitch,R_Hip_Roll,R_Hip_Pitch,R_Knee_Pitch,R_Ankle_Pitch,R_Ankle_Roll,L_Shoulder_Pitch,L_Shoulder_Roll,L_Elbow_Yaw,L_Elbow_Roll,L_Wrist_Yaw,R_Shoulder_Pitch,R_Shoulder_Roll,R_Elbow_Yaw,R_Elbow_Roll,R_Wrist_Yaw,L_H,L_Hand,R_H,R_Hand]

  get_first_handles(clientID,Body)


  motionProxy  = ALProxy("ALMotion", robotIP, PORT)
  postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)

  print '========== NAO is listening =========='
  commandAngles = motionProxy.getAngles('Body', False)

  # Wake up robot
  motionProxy.wakeUp()
  JointControl(clientID,motionProxy,0,Body)

  # Send robot to Stand Init
  postureProxy.goToPosture("StandInit", 0.5)
  JointControl(clientID,motionProxy,0,Body)

  # Activate Whole Body Balancer
  isEnabled  = True
  motionProxy.wbEnable(isEnabled)
  JointControl(clientID,motionProxy,0,Body)

  # Legs are constrained fixed
  stateName  = "Fixed"
  supportLeg = "Legs"
  motionProxy.wbFootState(stateName, supportLeg)
  JointControl(clientID,motionProxy,0,Body)

  # Constraint Balance Motion
  isEnable   = True
  supportLeg = "Legs"
  motionProxy.wbEnableBalanceConstraint(isEnable, supportLeg)
  JointControl(clientID,motionProxy,0,Body)

  # Com go to LLeg
  supportLeg = "LLeg"
  duration   = 2.0
  motionProxy.wbGoToBalance(supportLeg, duration)
  JointControl(clientID,motionProxy,0,Body)

  # RLeg is free
  stateName  = "Free"
  supportLeg = "RLeg"
  motionProxy.wbFootState(stateName, supportLeg)
  JointControl(clientID,motionProxy,0,Body)

  # RLeg is optimized
  effector = "RLeg"
  axisMask = 63
  frame    = motion.FRAME_WORLD

  # Motion of the RLeg
  times   = [2.0, 2.7, 4.5]

  path = computePath(motionProxy, effector, frame)

  motionProxy.transformInterpolations(effector, frame, path, axisMask, times)
  JointControl(clientID,motionProxy,0,Body)

  # Example showing how to Enable Effector Control as an Optimization
  isActive     = False
  motionProxy.wbEnableEffectorOptimization(effector, isActive)
  JointControl(clientID,motionProxy,0,Body)

  # Com go to LLeg
  supportLeg = "RLeg"
  duration   = 2.0
  motionProxy.wbGoToBalance(supportLeg, duration)
  JointControl(clientID,motionProxy,0,Body)

  # RLeg is free
  stateName  = "Free"
  supportLeg = "LLeg"
  motionProxy.wbFootState(stateName, supportLeg)
  JointControl(clientID,motionProxy,0,Body)

  effector = "LLeg"
  path = computePath(motionProxy, effector, frame)
  motionProxy.transformInterpolations(effector, frame, path, axisMask, times)
  JointControl(clientID,motionProxy,0,Body)

  time.sleep(1.0)

  # Deactivate Head tracking
  isEnabled = False
  motionProxy.wbEnable(isEnabled)
  JointControl(clientID,motionProxy,0,Body)

  # send robot to Pose Init
  postureProxy.goToPosture("StandInit", 0.3)
  JointControl(clientID,motionProxy,0,Body)

  # Go to rest position
  motionProxy.rest()
  JointControl(clientID,motionProxy,0,Body)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", type=str, default="127.0.0.1",
                      help="Robot ip address")
  parser.add_argument("--port", type=int, default=CHOREO_PORT,
                      help="Robot port number")

  args = parser.parse_args()
  main(args.ip, args.port)
