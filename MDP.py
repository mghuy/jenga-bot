import math
import random
'''
import roslib; roslib.load_manifest('jenga_robot_gazebo')
import rospy
from std_msgs.msg import Empty, Int32, String
from jenga_robot_gazebo.srv import Move, MoveResponse
'''
# === Final Variables
states = []
index = [] #format [start0, end0/start1, end1/start2] 
           #inclusive lowerBound, exclusive upperBound
           
height = 3
blocks = height*3

fallenIndex = -1
fallenReward = -10
#gaolIndex is specified after index file is read in
goalReward = 10
#otherReward = is currently based on how many move has been made

resultFile = open("result.txt", "w")

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

goalIndex = index[len(index)-1]
#example - print goal state
#print(bin(states[goalIndex]))

#============================== MDP =============================================

def action(state, futureStates):
    action = None
    newState = random.choice(futureStates)
    xor = state ^ newState
    blockNum = math.log2(xor&-xor) #0-index
    return blockNum
    
def reward(stateIndex, timeStep):
    if (stateIndex == -1): return fallenReward
    elif (stateIndex == len(states)-1): return goalReward
    else: return timeStep

# TODO - Finish creating correct stateActionMatrix
def createStateAction():
    Q = [[0 for i in range(blocks)] for j in range(len(states))]
    #for i in range(len(states)):
    return Q

    for i in range(len(states)):
        for j in range(blocks):
            Q[i][j] = None
        
    
#returns [stateIndex (int), timeStep of currentState (int), futureStates(list)]
def locateState(rosState, t):
    if (rosState == None):
        return [-1, t, []]
    rosState = rosState[::-1]   #reverse string
    rosState = int(rosState,2)
    #t = len(bin(rosState))-2 - blocks
    futureStates = states[index[t+1]:index[t+2]]
    for i in range(index[t], index[t+1]):
        if (rosState == states[i]):
            stateInformation = [i, t, futureStates]
            return stateInformation
    return "State not found"

#============================ SARSA UPDATES ==========================================

def sarsa_update(Q, oldS, newS, oldA, newA, r):
    Q[oldS][oldA] += alpha * (r + gamma*Q[newS][newA] - Q[oldS][oldA])
    return Q

def updatePi (pi, Q, s):
    actionValue = filter(None,Q[s])
    pi[s] = Q[s].index(max(actionValue)) + 1  #plus 1 because blocks are 1-indexed
    return pi

#========= JUST TESTING =============#

test = locateState("1011111111",1);
print(test)
print(len(bin(states[18]))-2)
Q = createStateAction();
print (Q)
listing = [1,7,4,None, 7]
print(listing.index(max(filter(None,listing))))
    
#============================ ROS STUFF ==========================================
jenga_move = None
waitingForServer = True
state = None
newState = None
Q = createStateAction() #state_action matrix
pi = [0 for i range(len(states))]
t = 0
totalReward = 0
epoc = 0

def reset_callback(empty):
    global waitingForServer
    global newState
    global Q
    global t
    global totalReward
    global epoc

    waitingForServer = True
    newState = None
    epoc += 1
    
    # write Q value for each state into the columns and the total actions taken
    resultFile.write(str(t) + "," + str(totalReward) + ",")
    for i in range(len(Q)):
        resultFile.write(str(max(Q[i])) + ",")
    resultFile.write("\n")
    
    t = 0
    totalReward = 0
    print("FALLEN!")
    print("Epoc " + str(epoc) + ": " + str(t) + ", " + srt(totalReward)) 
    #TODO figure out how to print Q
    
def state_pub_callback(res):
    global waitingForServer
    global state

    waitingForServer = False
    state = res.data
    
if __name__ == 'main':

    rospy.init_node('rl_jenga_player')
    rospy.sleep(2.0)
    rospy.wait_for_service("/game_msgs/move")
    jenga_move = rospy.ServiceProxy("/game_msgs/move", Move)

    rospy.Subscriber("/game_msgs/reset", Empty, reset_callback)
    rospy.Subscriber("/game_msgs/state", String, state_pub_callback)

    waitingForServer = True

    desired_freq = rospy.get_param('~frequency', default = 1.0)
    sleep_time = 1.0 / desired_freq

    while not rospy.is_shutdown():
        rospy.sleep(sleep_time)

        if not waitingForServer:
            if newState == None:
                state_info = locateState(state, t)
                action = pi[state_info[0]]
                
            r = R(state_info[0], state_info[1])
            totalReward += r
            try:
                res = jenga_move(action)
            except rospy.service.ServiceException:
                pass
            newState = res.data
            rospy.sleep(sleep_rate) #see if the tower is fallen
            t += 1
            newState_info = locateState(newState, t)
            newAction = pi[newState_info[0]]
            #TODO figure out properly handling of array of index -1
            
            Q = sarsa_update(Q, state_info[0], newState_info[0], action, newAction, r)
            pi = updatePi(pi, Q, state_info[0])
            
            state_info = newState_info
            action = newAction

    print("Done!!!!!!!!!!")
            
