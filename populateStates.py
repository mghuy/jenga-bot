# Author: Leng Ghuy
# Version: April 30th, 2018

# Calculate all possible valid states for a specified height and output the binary
#       states and the indeces of each time step to two specified output files

###================================= IMPORTS =================================###

import math
import time

###============================ GLOBAL VARIABLES =============================###

states=[]
init = 111111111;
height = 3
blocks = height * 3

statesFile = open("states.txt", "w")
indexFile = open("index.txt", "w")


###============================ HELPHER METHODS ==============================###

def RemoveDup (duplicate):
    final = []
    for num in duplicate:
        if num not in final:
            final.append(num)
    return final

def RemoveInv(invalid):
    byteMask1 = '001'
    byteMask2 = '100'
    byteMask3 = '000'
    length = len(invalid)
    i = 0

    #every time an object is deleted, the length changes...adding count handles
    #this live update...do not remove
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
            temp = states[i] - (1<<j) + (1<<(blocks+timeStep))
            if (bin(temp).count("1")==blocks):
                tempList.append(temp)
    testList = RemoveDup(tempList)
    finalList = RemoveInv(testList)
    #printing(finalList)
    return finalList

###============================== MAIN PROGRAM ===============================###

byte1 = int(str(init), 2)
states[0] = (byte1)

statesFile.write(bin(states[0]) + '\n')
indexFile.write('0' + '\n' + '1' + '\n')

t1 = []
startTime = time.time()
for i in range(blocks-3):
    temp = states[0] - (1<<i) + (1<<blocks);
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
    
    if(len(t) == 0):
        print("Through with first iteration - Now we break the rule \n")
        while(True):
            end = len(states)
            length = len(bin(states[end-1])) - 2
            moves = int(math.floor(length/3)*3)
            if length % 3 == 0: moves -= 3
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
            if(len(t) == 0): break
            
        break
    
    for j in range(end-start,end):
        statesFile.write(bin(states[j]) + "\n")
    indexFile.write(str(end) + '\n')
    
    i += 1
    start = len(t)    
	
statesFile.close()
indexFile.close()
