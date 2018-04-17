import copy
import sys
import numpy as np
from random import *
from math import *


### ------ Final Variables ------ ###

borderMap = [[-1,-1,-1,-1,-1,-1],
             [-1,0,0,0,0,-1],
             [-1,0,-1,0,0,-1],
             [-1,0,0,0,0,-1],
             [-1,-1,-1,-1,-1,-1]]
states = [[1,1],[1,2],[1,3],[1,4],
          [2,1],[2,3],[2,4],
          [3,1],[3,2],[3,3],[3,4]];
actions = [0,1,2,3] # 0 - Up
                    # 1 - Down
                    # 2 - Left
                    # 3 - Right
gamma = 0.99999
delta = 0.001
alpha = 0.1


### ------ Methods ------ ###

def R (s):
    rewardMap = [[0,0,0,0,0,0],
                [0,-0.04,-0.04,-0.04,1,0],
                [0,-0.04,0,-0.04,-1,0],
                [0,-0.04,-0.04,-0.04,-0.04,0],
                [0,0,0,0,0,0]]
    return rewardMap[s[0]][s[1]]

def P (s,a):
    possible = [[s[0],s[1],0]]
    if(s==[1,4] or s==[2,4]):
        return possible
    
    if(a==0): #checking up
        checkLR(s,possible)
        if(borderMap[s[0]-1][s[1]] == 0): #check up
            possible.append([s[0]-1,s[1],.8])
        else:
            possible[0][2] += 0.8
        
    if(a==1): #checkingDown
        if(borderMap[s[0]+1][s[1]] == 0): #check down
            possible.append([s[0]+1,s[1],.8])
        else:
            possible[0][2] += 0.8
        checkLR(s,possible)
            
    if(a==2): #checkingLeft
        if(borderMap[s[0]][s[1]-1] == 0): #check left
            possible.append([s[0],s[1]-1,.8])
        else:
            possible[0][2] += 0.8
        checkUD(s,possible)
        
    if(a==3):
        if(borderMap[s[0]][s[1]+1] == 0): #check right
            possible.append([s[0],s[1]+1,.8])
        else:
            possible[0][2] += 0.8
        checkUD(s,possible)
        
    if(possible[0][2] == 0): possible.remove(possible[0])
    return possible

def checkLR (s,possible):
    if(borderMap[s[0]][s[1]-1] == 0 and borderMap[s[0]][s[1]+1] == 0): #check both
        possible.append([s[0],s[1]-1,.1])
        possible.append([s[0],s[1]+1,.1])
    elif(borderMap[s[0]][s[1]+1] == 0): #check right
        possible.append([s[0],s[1]+1,.1])
        possible[0][2] += 0.1
    elif(borderMap[s[0]][s[1]-1] == 0): #check left
        possible.append([s[0],s[1]-1,.1])
        possible[0][2] += 0.1
    else:
        possible[0][2] += 0.2
        
def checkUD (s,possible):
    if(borderMap[s[0]-1][s[1]] == 0 and borderMap[s[0]+1][s[1]] == 0): #check both
        possible.append([s[0]-1,s[1],.1])
        possible.append([s[0]+1,s[1],.1])
    elif(borderMap[s[0]-1][s[1]] == 0): #check up
        possible.append([s[0]-1,s[1],.1])
        possible[0][2] += 0.1
    elif(borderMap[s[0]+1][s[1]] == 0): #check down
        possible.append([s[0]+1,s[1],.1])
        possible[0][2] += 0.1
    else:
        possible[0][2] += 0.2

def value_iteration (states,actions,gamma,epsilon):
    U = [[0 for i in range(4)] for j in range(3)]
    U1 = [[0 for i in range(4)] for j in range(3)]
    count = 0
    while True:
        U = copy.deepcopy(U1)
        U1 = [[0 for i in range(4)] for j in range(3)]
        delta = -sys.maxsize-1
        direction = [0 for i in range (4)]
        for s in states:
            i = 0
            for a in actions:
                possible = P(s,a)
                temp = 0
                for p in possible:
                    #print(a, s, p)
                    temp += p[2] * U[p[0]-1][p[1]-1]
                direction[i] = temp
                i += 1
            U1[s[0]-1][s[1]-1] = R(s) + gamma * max(direction)
            delta = max(delta,abs(U1[s[0]-1][s[1]-1] - U[s[0]-1][s[1]-1]))
        count += 1
        if delta < (epsilon * (1 - gamma) / gamma):
            print(count)
            return U

#Given a fixed Utility from value iteration
def best_policy(states,actions,U):
    pi = [[0 for i in range(4)] for j in range(3)]
    pi[1][1] = None
    for s in states:
        f = lambda a:expected_utility(a,s,U)
        l = [f(a) for a in actions]
        pi[s[0]-1][s[1]-1] = actions[l.index(max(l))]
    return pi
    
def expected_utility(a,s,U):
    possible = P(s,a)
    total = sum([p[2] * U[p[0]-1][p[1]-1] for p in possible])
    return total

def policy_iteration(states,actions,gamma):
    U = [[0 for i in range(4)] for j in range(3)]
    pi = [[0 for i in range(4)] for j in range(3)]
    pi[1][1] = None
    while True:
        U = policy_evaluation(pi, U, states, gamma)
        unchanged = True
        for s in states:
            f = lambda a:expected_utility(a,s,U)
            l = [f(a) for a in actions]
            a = actions[l.index(max(l))]
            if a != pi[s[0]-1][s[1]-1]:
                pi[s[0]-1][s[1]-1] = a
                unchanged = False
            if unchanged:
                return pi
    
def policy_evaluation(pi, U, states, gamma, k=100):
    for i in range(k):
        for s in states:
            possible = P(s,pi[s[0]-1][s[1]-1])
            total = sum([p[2] * U[p[0]-1][p[1]-1] for p in possible])
            U[s[0]-1][s[1]-1] = R(s) + gamma * total
    return U

def simulation(states, initState, policy, runTimes):
    for i in range(runTimes):
        possible = P(initState,policy[initState[0]-1][initState[1]-1])
        percent = 0
        for p in possible:
            percent += p[2]
        timeStep = 0
        startingState = initState
        decision = []
        while True:
            #print(possible)
            if (percent!=0):
                roulette = random()
                prevState = initState
                test = possible[0][2]
                for i in range(len(possible)):
                    if test >= roulette:
                        decision = prevState
                        break
                    test += possible[i+1][2]
                    prevState = [possible[i+1][0],possible[i+1][1]]
            else:
                print("Reached Terminal State")
                break
            print(timeStep, startingState, policy[startingState[0]-1][startingState[1]-1], decision)
            startingState = decision
            
            possible = P(startingState, policy[startingState[0]-1][startingState[1]-1])
            percent = 0
            for p in possible:
                percent += p[2]
            timeStep += 1

def roulette (state, action):
    possible = P(state, action)
    roulette = random()
    prevState = state
    test = possible[0][2]
    decision = []
    for i in range(len(possible)):
        if test>= roulette:
            decision = prevState
            break
        else:
            test += possible[i+1][2]
            prevState = [possible[i+1][0],possible[i+1][1]]
    return decision

'''def passiveTD (perceptS, pi, prevInfo):
    s,a,r = None
    U = prevInfo[3], N=prevInfo[4]
    i = perceptS[0]-1, j = perceptS[1]-1
    previ = prevInfo[0][0]-1, prevj = prevInfo[0][1]-1
    if (N[i][j] == 0): U[i][j] = R(perceptS)
    if prevInfo[0]!= None:
        N[previ][prevj] += 1
        U[previ][prevj] = U[previ][prevj] + alpha*N[previ][prevj]*(prevInfo[2] + gamma*U[newi][newj]-U[i][j])
    if (prevInfo[0] != [1,4] and prevInfo[0]!=[2,4]):
        s = perceptS, a = pi[s], r = R(perceptS)
    return [s,a,r,U]
'''

def greedy(state, q):
    return action;
#[s,a,r,U]
def passiveTD (perceptS, pi, prevInfo):
    s = None
    a = None
    r = None
    U = prevInfo[3]
    prevS = prevInfo[0]
    i = prevInfo[0][0]-1
    j = prevInfo[0][1]-1
    r = prevInfo[2]
    newI = perceptS[0]-1
    newJ = perceptS[1]-1

    #if N[newI][newJ] == 0: U[newI][newJ] = R(perceptS)
    #else:
    #N[i][j] += 1
    U[i][j] = U[i][j] + alpha*(r + gamma*U[newI][newJ] - U[i][j])
    if (perceptS != [1,4] and perceptS != [2,4]):
        s = perceptS
        a = pi[i][j]
        r = R(perceptS)
    return [s,a,r,U]

def sim (pi):
    U = [[0 for i in range(4)] for j in range(3)]
    N = [[0 for i in range(4)] for j in range(3)]
    #pi = best_policy(states,actions,U)
    for epoc in range (5):  
        initS = [1,1]
        initA = pi[initS[0]-1][initS[1]-1] 
        initR = R(initS)
        info = [initS,initA,initR,U,N]
        perceptS = roulette(initS, initA)
        #print(U)
        for episode in range(5):
            info = passiveTD(perceptS, pi, info)
            U = info[3]
            N = info[4]
            #pi = best_policy(states,actions,U)
            if (info[1] == None): break
            perceptS = roulette(info[0],info[1])
            print(U)
        #print(str(epoc))
        #print(pi)
    #print(info[3])

#=========================== SARSA ================================#

def prettyPrint(table):
    for i in range(len(table)):
        print(table[i][0], table[i][1], table[i][2], table[i][3])
    print("")

def stateRoulette (state, action):
    possible = P(state, action)
    roulette = random()
    prevState = state
    test = possible[0][2]
    decision = []
    for i in range(len(possible)):
        if test>= roulette:
            decision = prevState
            break
        else:
            test += possible[i+1][2]
            prevState = [possible[i+1][0],possible[i+1][1]]
    return decision

def policyDis (s, a, Q):
    col = s[1]-1 + (s[0]-1)*4
    l = [x[col] for x in Q]
    e_x = exp(Q[a][col])
    total= 0
    for i in range(len(l)):
        total += exp(l[i])
    return e_x / total

def policyRoulette (s, Q):
    actionList = []
    for i in range(4):
        actionList.append(policyDis(s,actions[i],Q))
    roulette = random()
    test = actionList[0]
    prevA = actions[0]
    decision = prevA
    for i in range(len(actionList)):
        if test>=roulette:
            decision = prevA
            break
        else:
            test += actionList[i+1]
            prevA = actions[i+1]
    return decision
    
    

'''
def expected(a,s,U):
    possible = P(s,a)
    total = sum([U[p[0]-1][p[1]-1] for p in possible])
    return total

def updatePi(pi, Q, s):
    f = lambda a:expected_utility(a,s,Q)
    l = [f(a) for a in actions]
    pi[s[0]-1][s[1]-1] = actions[l.index(max(l))]
    return pi
'''
def updatePi(pi, Q, s):
    col = s[1]-1 + (s[0]-1)*4
    #find the index of largest value
    l = [x[col] for x in Q]
    #print(l, l.index(max(l)))
    pi[s[0]-1][s[1]-1] = l.index(max(l))
    return pi

def terminate(s):
    if (s == [1,4] or s == [2,4]):
        return True
    else:
        return False

def sarsa_update(Q, oldS, newS, oldA, newA, r):
    col = (oldS[1]-1) + (oldS[0]-1)*4
    col_t1 = (newS[1]-1) + (newS[0]-1)*4
    Q[oldA][col] += alpha * (r + gamma*Q[newA][col_t1] - Q[oldA][col])
    return Q
    
def sarsa(episodes):
    Q = [[0 for i in range(12)] for j in range(4)]
    pi = [[0 for i in range(4)] for j in range(3)]
    for epoc in range(episodes):
        s = choice(states)
        a = pi[s[0]-1][s[1]-1]
        #a = policyRoulette(s, Q)
        for step in range(1000):
            if terminate(s):
                col = s[1]-1 + (s[0]-1)*4
                for i in range(4):
                    Q[i][col] = R(s)
                break
            #a = pi[s[0]-1][s[1]-1]
            r = R(s)
            newS = stateRoulette(s, a)
            newA = pi[newS[0]-1][newS[1]-1]
            #newA = policyRoulette(newS, Q)
            Q = sarsa_update(Q, s, newS, a, newA, r)
            pi = updatePi(pi, Q, s)
            #print(s, a, newS, newA)
            s = newS
            a = newA
            #print(pi)
        #print("================================" + str(epoc))
        #prettyPrint(pi)

    #pretty printing Q
    #print(Q)
    for i in range(12):
        l = [x[i] for x in Q]
        print(str(max(l)) + ","),
        #probList = []
        #for j in range(4):
        #    prob = policyDis(s, j, Q)
        #    test = l[j]
        #    probList.append(prob*test)
        #print(str(sum(probList)) + ","),
        if ((i+1)%4 == 0): print("")
    #prettyPrint(Q)
    #pi = updatePi(pi, Q, s)
    prettyPrint(pi)

### ------ Main Program ------ ###

utility = value_iteration(states, actions, gamma, delta)
prettyPrint(utility)
U = [[0 for i in range(4)] for j in range(3)]
policy = best_policy(states, actions, utility)
prettyPrint(policy)
#print(policy)
#simulation(states, [3,1], policy, 5)

sarsa(100000);
