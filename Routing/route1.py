#!/bin/python
#building on file bfs_no_wts
# put your routing program here!

import sys

def map_locations(Filename):
    f=open(Filename,'r')
    data=f.read()
    la=data.split('\n')
    la =la[0:len(la)-1]
    map={}
    for row in la:
        templist=row.split(' ')
        if templist[0] in (list(map.keys())):
            tempvalues=map[templist[0]]
            tempvalues.append(templist[1:5])
            map[templist[0]]=tempvalues
        else:
            map[templist[0]] = [templist[1:5]]
        if templist[1] in (list(map.keys())):
            tempvalues=map[templist[1]]
            tempvalues.append(templist[0:1]+templist[2:5])
            map[templist[1]]=tempvalues
        else:
            map[templist[1]] = [templist[0:1]+templist[2:5]]
    return map

def result(lst_res):
    tot_dis=0.0; tot_time=0.0; route=''
    route+=lst_res[0]
    for i in range (1,len(lst_res),3):
        route+=' '+lst_res[i]
        tot_dis+=lst_res[i+1]
        tot_time+=lst_res[i+2]
    return str(int(tot_dis))+' '+str(round(tot_time,3))+' '+route

def cost_distance(ldst):
    #print('list=',ldst)
    if algo == 'uniform':
        ldst.sort(key=lambda b: float(b[1]))
       # print('sorted=',ldst)
    elif algo in ['dfs','ids']:
        ldst.sort(key=lambda b: float(b[1]),reverse=True)
    return ldst

def cost_time(srt_ldst):
    if algo == 'uniform':
        srt_ldst.sort(key=lambda d: round(float(d[1])/float(d[2]),3))
    elif algo in ['dfs', 'ids']:
        srt_ldst.sort(key=lambda d: round(float(d[1]) / float(d[2]), 3),reverse=True)
    return srt_ldst

def successors(parent):
    succ=[]
    temp={}
    P=list(parent.keys())[0]
    lst_dst=MAP[P]
    ldst=lst_dst
    #print(ldst)
    if cost_func=='distance' and algo!='bfs':
        print('Imhere')
        ldst=cost_distance(lst_dst)
    elif cost_func=='time' and algo!='bfs':
        ldst=cost_time(lst_dst)
    for each in ldst:
        #print(each)
        if each[2]=='' or each[2]=='0':
            continue
        else:
            temp[each[0]]= parent[P] + [each[0],float(each[1]),round(float(each[1])/float(each[2]),3)]
        succ.append(temp)
        temp={}
    return(succ)

def is_goal(city):
    if (city==destination):
        return True
    return False

def solve_breadth(initial_board):
    visited_nodes = [initial_board]
    fringe = [{initial_board:[initial_board]}]
    for p in fringe:
        print("fringe=", fringe)

        for s in successors(p):
           # print('s',s)
            s_key=list(s.keys())[0]
            if is_goal(s_key):
                return(result(s[s_key]))
            if s_key not in visited_nodes:
                visited_nodes.append(s_key)
                fringe.append(s)
    return False

def solve_depth(initial_board):
    visited_nodes = [initial_board]
    fringe = [{initial_board:[initial_board]}]


        #print('visited=', visited_nodes)
        #print('p',p)
    while len(fringe) > 0:
        print("fringe=", fringe)
        for s in successors(fringe.pop()):
           # print('s',s)
            s_key=list(s.keys())[0]
            if is_goal(s_key):
                return(result(s[s_key]))
            if s_key not in visited_nodes:
                visited_nodes.append(s_key)
                fringe.append(s)
        #fringe=fringe[1:]
        #print('fringe=',fringe)
    return False



source=str(sys.argv[1])
destination=str(sys.argv[2])
algo=str(sys.argv[3])
cost_func=str(sys.argv[4])

MAP=map_locations('road-segments.txt')
if (algo in ['bfs','uniform']):
    print(solve_breadth(source))
elif (algo in ['dfs','ids']):
    print(solve_depth(source))
else:
    print("Error input. Please try again")

