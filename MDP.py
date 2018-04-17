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
           
futureStates = []
t = 0
height = 3
blocks = height*3
maxHeight = height*blocks*3
fallenIndex = -1
fallenReward = -10
goalIndex = 0   #to be changed after index.txt is read in
goalReward = 10
#otherReward = is currently based on how many move has been made
resultFile = open("result.txt", "w")

#alpha = tbd - possible not even final because of dynamic changing alpha
gamma = 0.99
#ROS variables
#pub = rospy.Publisher('/game_msgs/action', Int32)

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
    
def move(stateIndex):
    return [0,0]
    
def reward(stateIndex, timeStep):
    if (stateIndex == -1): return fallenReward
    elif (stateIndex == len(states)-1): return goalReward
    else: return timeStep

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

#============================ SARSA ==========================================



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
Q #state_action matrix

def reset_callback(empty):
    global waitingForServer
    global newState

    waitingForServer = True
    newState = None

    print("FALLEN!")

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

    #how do I reset??

    #one iteration of sarsa until you reach a terminal state

    state_info = locateState(state, t)
    action = policyRoulette(state, Q)
    t = 0
    while not rospy.is_shutdown() and state!=states[len(states)-1]:
        rospy.sleep(sleep_time)

        if not waitingForServer:
            
            r = R(state_info[0], state_info[1])
            
            try:
                res = jenga_move(action)
            except rospy.service.ServiceException:
                pass
            newState = res.data
            t += 1
            newState_info = locateState(newState, t)
            newAction = policyRoulette(newState, Q)
            Q = sarsa_update(Q, state_info[0], newState_info[0], action, newAction, r)
            state_info = newState_info
            action = newAction

    print("Reached Goal State")
    #somehow print Q
    #---end of 1 iteration of SARSA
            
