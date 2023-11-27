import asyncio

import random

def randomize_members(members):
    pairs = {}
    members.sort()
    reciver_list = members.copy()

    if 1513119067 in members and 1338914722 in members:
        reciver_list.pop(reciver_list.index(1513119067))
    if 1515123223 in members and 5025889207 in members:
        reciver_list.pop(reciver_list.index(1515123223))

    for member in members:
        while True:

            if member == 1338914722 and 1513119067 in members:
                reciver = 1513119067
                break
            if member == 5025889207 and 1515123223 in members:
                reciver = 1515123223
                break

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