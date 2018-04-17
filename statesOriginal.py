#State Calcuation

import math
import time
statesFile = open("states.txt", "w")
indexFile = open("index.txt", "w")

def RemoveDup (duplicate):
    final = []
    for num in duplicate:
        if num not in final:
            final.append(num)
    return final


posList = []
listing = 1
posList.append(listing)
for i in range(29):
    listing += 3;
    posList.append(listing)

def RemoveInv(invalid):
    byteMask1 = '001'
    byteMask2 = '100'
    byteMask3 = '000'
    length = len(invalid)
    i = 0
    count = 0
    for i in range(length):
        s = invalid[i-count]
        #print(str(i) + " - " + str(len(invalid)) + " - " + bin(s))
        length = len(bin(s))
        while (length>=0):
            if ((bin(s)[length-3:length] == byteMask1) or 
                (bin(s)[length-3:length] == byteMask2) or
                (bin(s)[length-3:length] == byteMask3)):
                del invalid[i-count]
                count += 1
                #print("======removed: " + bin(s))
                break;
            else:
                length -= 3
    return invalid


def printing(states):
    for i in range(len(states)):
        print("[" + str(i) + "] " + bin(states[i]))
        
def createStates(start, end, moves,timeStep):
    tempList = []
    for i in range(start,end):
        for j in range(moves):
            temp = states[i] - (1<<j) + (1<<(9+timeStep))
            if (bin(temp).count("1")==9):
                tempList.append(temp)
    testList = RemoveDup(tempList)
    #printing(testList)
    finalList = RemoveInv(testList)
    #while(True):
        #length = len(testList)
        #print("length of testList: " + str(length))
        #testList = RemoveInv(testList)
        #if(length == len(testList)): break
    printing(finalList)
    return finalList

states=[0]
init = 111111111;
goal = 1010010010010010010010010;
byte1 = int(str(init), 2)
byteGoal = int(str(goal),2)
states[0] = (byte1)
#print((bin(states[0]))[0:4])

statesFile.write(bin(states[0]) + '\n')
indexFile.write('0' + '\n' + '1' + '\n')

t1 = []
startTime = time.time()
for i in range(6):
    temp = states[0] - (1<<i) + (1<<9);
    t1.append(temp)
elapsed = time.time() - startTime
states.extend(t1)
print("t=1: " + str(len(t1)) + " --- Total: " + str(len(states)) + " --- Time(min)" + str(elapsed/60) + "\n" )
printing(states)

start = len(t1)
i = 2

# Follows the rule completely!! cannot reach goal state
'''
while(True):
    end = len(states)
    moves = len(bin(states[end-1])) - 2
    moves = math.floor(moves/3)*3 - 3
    print("[" + str(i) + "] createStates " + "(" + str(end-start) + ", " + str(end) + ", " + str(moves) + ")")
    startTime = time.time()
    t = createStates(end-start,end,moves,i-1)
    elapsed = time.time() - startTime
    states.extend(t)
    print("t=" + str(i) + ": " + str(len(t)) + " --- Total: " + str(len(states)) + " --- Time(min)" + str(elapsed/60) + "\n")
    
    for j in range(end-start,end):
        statesFile.write(bin(states[j]) + "\n")
		
    indexFile.write(str(end) + '\n')
    #if(i == 5): break;
    if(len(t) == 0):
        break;
        
    i += 1
    start = len(t)
'''

# Can reach goal state - but breaks rule at the end
while(True):
    end = len(states)
    moves = len(bin(states[end-1])) - 2
    moves = int(math.floor(moves/3)*3 - 3)
    print("[" + str(i) + "] createStates " + "(" + str(end-start) + ", " + str(end) + ", " + str(moves) + ")")
    startTime = time.time()
    t = createStates(end-start,end,moves,i-1)
    elapsed = time.time() - startTime
    states.extend(t)
    print("t=" + str(i) + ": " + str(len(t)) + " --- Total: " + str(len(states)) + " --- Time(min)" + str(elapsed/60) + "\n")
    5
    for j in range(end-start,end):
        statesFile.write(bin(states[j]) + "\n")
    indexFile.write(str(end) + '\n')
    
    if(len(t) == 0):
        print("Through with first iteration\n")
        while(True):
            end = len(states)
            moves = len(bin(states[end-1])) - 2
            moves = int(math.floor(moves/3)*3)
            print("[" + str(i) + "] createStates " + "(" + str(end-start) + ", " + str(end) + ", " + str(moves) + ")")
            startTime = time.time()
            t = createStates(end-start,end,moves,i-1)
            elapsed = time.time() - startTime
            states.extend(t)
            print("t=" + str(i) + ": " + str(len(t)) + " --- Total: " + str(len(states)) + " --- Time(min)" + str(elapsed/60) + "\n")
    
            for j in range(end-start,end):
                statesFile.write(bin(states[j]) + "\n")
            indexFile.write(str(end) + '\n')
				
            i += 1
            start = len(t)
            if(len(t) == 0): 
                states.append(byteGoal)
                statesFile.write(bin(byteGoal) + "\n")
                indexFile.write(str(end+1) + '\n')
                break
        break
		
    i += 1
    start = len(t)    
    
	
statesFile.close()
indexFile.close()
