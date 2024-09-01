import asyncio

import random

def randomize_members(members):
    pairs = {}
    members.sort()
    reciver_list = members.copy()
    
    for member in members:
        while True:
            reciver = random.choice(reciver_list)
            if len(reciver_list)==2  and members[-1] in reciver_list:
                reciver = members[-1]

            if reciver!=member:
                reciver_list.pop(reciver_list.index(reciver))
                break
        pairs[member] = reciver
    return pairs

if __name__ =="__main__":
    members =[1,2,3,4]
    print(randomize_members(members))
