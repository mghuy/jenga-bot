#!/usr/bin/env python

import math
import random
import roslib; roslib.load_manifest('jenga_robot_gazebo')
import rospy
from std_msgs.msg import Empty, Int32, String
from jenga_robot_gazebo.srv import Move, MoveResponse

# === Final Variables
states = []
index = [] #format [start0, end0/start1, end1/start2] 
           #inclusive lowerBound, exclusive upperBound
           
height = 3
blocks = height*3

fallenIndex = -1
fallenReward = -50
#gaolIndex is specified after index file is read in
goalReward = 35
#otherReward = is currently based on how many move has been made

resultFile = open("result.txt", "w")
policyFile = open("policy.txt", "w")

alpha = 0.1
gamma = 0.9999

with open("states.txt") as f:
    readIn = f.read().splitlines()
    
for i in range(len(readIn)):
    byte = int(readIn[i], 2)
    states.append(byte)

with open("index.txt") as f:
    index = f.read().splitlines()
    index = list(map(int, index)) #python3 - take out list() around map() for python2

goalIndex = len(states)-1
#example - print goal state
#print(bin(states[goalIndex]))

#============================== MDP =============================================

def action(state, futureState):
    action = None
    xor = state ^ futureState
    blockNum = int(math.log(xor&-xor, 2)) #0-index
    mask = int("1", 2)
    for i in range (blockNum):
        temp = 1<<(i+1)
        mask |= temp
    action = bin(mask & state).count("1")
    #print(bin(mask), blockNum, action)
    return (action-1)

def possibleFuture(state, futureStates):
    possibleFuture = []
    for futureState in futureStates:
        if (bin(state ^ futureState).count("1") == 2):
            possibleFuture.append(futureState)
    return possibleFuture
    
def reward(stateIndex, timeStep):
    if (stateIndex == -1): return fallenReward
    elif (stateIndex == len(states)-1): return goalReward
    else: return timeStep

def createStateAction():
    Q = [[None for i in range(blocks)] for j in range(len(states))]
    for i in range(len(states)-1):
        length = len(bin(states[i]))-2
        moves = blocks
        moves -= length % 3
        if length % 3 == 0: moves -= 3
        for j in range(moves):
            Q[i][j] = 0
    return Q
        

    
#returns [stateIndex (int), timeStep of currentState (int), futureStates(list)]
def locateState(rosState, t):
    if (rosState == None):
        return [-1, t, []]
    rosState = rosState[::-1]   #reverse string
    rosState = int(rosState,2)
    #t = len(bin(rosState))-2 - blocks
    if t>12: 
        print("Oh no")
        return [-1, t, []]
    futureStates = []
    if t<12: futureStates = states[index[t+1]:index[t+2]]
    for i in range(index[t], index[t+1]):
        if (rosState == states[i]):
            stateInformation = [i, t, futureStates]
            return stateInformation
    print("State Not Found - assuming fallen")
    return [-1, t, []]

#============================ SARSA UPDATES ==========================================

def sarsa_update(Q, oldS, newS, oldA, newA, r):
    print(oldS, newS, oldA, newA)
    if oldS == -1 or oldS == len(states)-1: return Q
    q = Q[oldS][oldA]
    if q == None: q = 0
    q_t1 = Q[newS][newA]
    if q_t1 == None:
          if newS!=(len(states)-1): q_t1 = fallenReward
          else: q_t1 = goalReward
    q += alpha * (r + gamma*q_t1 - q)
    Q[oldS][oldA] = q
    return Q

def updatePi (pi, Q, s):
    length = len(bin(states[s]))-2
    moves = blocks
    moves -= length % 3
    if length % 3 == 0: moves -= 3
    print(bin(states[s]) + " Number of Moves: " + str(moves))
    actionValue = [0 for i in range(moves)]
    for i in range(moves):
        actionValue[i] = Q[s][i]
    randomZeros = []
    move = max(actionValue)
    print(actionValue)
    if actionValue.count(move) > 1: 
            randomZeros = [i for i, x in enumerate(Q[s]) if x == move]
            print(randomZeros)
            pi[s] = random.choice(randomZeros)
    else:
        pi[s] = Q[s].index(move)
    print(pi[s])
    return pi

#========= JUST TESTING =============#
'''
test = locateState("01001001001001011011",11);
print(test)
#print(len(bin(states[18]))-2)
Q = createStateAction();
for i in range(len(Q)):
    print (bin(states[i]), Q[i])
#listing = [1,7,4,None, 7]
#print(listing.index(max(filter(None,listing))))
''' 
#============================ ROS STUFF ==========================================
jenga_move = None
waitingForServer = True
state = None
newState = None
Q = createStateAction() #state_action matrix
#for i in range(len(Q)):
#    print(bin(states[i]), Q[i])
pi = [0 for i in range(len(states))]
policyFile.write("[")
for i in range(len(pi)):
    policyFile.write(str(pi[i]) + ", ")
policyFile.write("]\n")
#print(pi)
#pi = [random.randint(0,blocks-4) for i in range(len(states))]
t = 0
totalReward = 0
epoc = 0
state_info = None
iteration = 0

def reset_callback(empty):
    global waitingForServer
    global newState
    global Q
    global t
    global totalReward
    global epoc
    global iteration

    waitingForServer = True
    newState = None
    epoc += 1
  
    # write Q value for each state into the columns and the total actions taken
    resultFile.write(str(t) + "," + str(totalReward))
    for i in range(len(Q)):
        resultFile.write( "," + str(max(Q[i])))
    resultFile.write("\n")
    
    print("Epoc " + str(epoc) + ": #Actions = " + str(t) + ", Reward = " + str(totalReward)) 

    t = 0
    totalReward = 0
    
    print("FALLEN!")

    iteration += 1
    if iteration == 5:
        print(pi)
        policyFile.write("[")
        for i in range(len(pi)):
            policyFile.write(str(pi[i]) + ", ")
        policyFile.write("]\n")
        iteration = 0

    
    
    
    print("Printing Q")
    for i in range(len(Q)):
        print ("[" + str(i) + "] " + str((Q[i])))
'''
    print("Printing pi")
    for i in range(len(pi)):
        print ("[" + str(i) + "] " + str(pi[i]) + ",")
        if (i%20 == 0): print("\n")
    '''
    
def state_pub_callback(res):
    global waitingForServer
    global state

    waitingForServer = False
    state = res.data


if __name__ == '__main__':


    rospy.init_node('rl_jenga_player')
    rospy.sleep(2.0)
    rospy.wait_for_service("/game_msgs/move")
    jenga_move = rospy.ServiceProxy("/game_msgs/move", Move)

    rospy.Subscriber("/game_msgs/reset", Empty, reset_callback)
    rospy.Subscriber("/game_msgs/state", String, state_pub_callback)

    waitingForServer = True

    desired_freq = rospy.get_param('~frequency', default = 1.0)
    sleep_time = 1 / (desired_freq)

    while not rospy.is_shutdown():
        for i in range(5):
            rospy.sleep(sleep_time)

            if not waitingForServer:
                if newState == None:
                    t=0
                    print("New Start - Observed state = " + state)
                    state_info = locateState(state, t)
                    action = pi[state_info[0]]
                    if action == None: action = random.randint(0, blocks-5)
            
                
                print("Moving Block #: " + str(action))
                try:
                    res = jenga_move(action)
                except rospy.service.ServiceException:
                    pass
                newState = res.data
                print("Observed State = " + newState)

                rospy.sleep(sleep_time) #see if the tower is fallen

                r = reward(state_info[0], state_info[1])
                totalReward += r

                

                t += 1
                newState_info = locateState(newState, t)
                newAction = random.randint(1, blocks-5)
                if (newState_info[0] != -1): newAction = pi[newState_info[0]]

                if newAction == None: newAction = random.randint(0, blocks-5)
            
                Q = sarsa_update(Q, state_info[0], newState_info[0], action, newAction, r)
                pi = updatePi(pi, Q, state_info[0])
            
                state_info = newState_info
                action = newAction

    print("Done!!!!!!!!!!")

    resultFile.close()
    policyFile.close()
            
