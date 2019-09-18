#!/usr/bin/env python3

import numpy as np
import pandas as pd
import sys
from datetime import datetime


def convert_points_to_board(point_b): #function not used in minimax, just to print the coordinates in board format for better vizualization
    board=np.array([['.']*n]*(n+3))   
    for p in range(0,len(point_b[0])):        
        board[point_b[0][p],point_b[1][p]]='x'
    for p in range(0,len(point_b[2])):
        board[point_b[2][p],point_b[3][p]]='o'
    return(board)

        

def convert_board_to_points(board): 
    p=[[],[],[],[]]
    for i in range(0,n+3):
        for j in range(0,n):
            if board[i][j]=='x':
                p[0].append(i)
                p[1].append(j)
            if board[i][j]=='o':
                p[2].append(i)
                p[3].append(j)
    return(p)
    
def convert_state_to_board(state):
    board=np.array([['.']*n]*(n+3))
    r=0
    c=0
    for st in state:        
        board[r,c]=st
        if c==n-1:
            c=0
            r+=1
        else:
            c+=1
        if r==n+3 and c==n:
            break
    return(board)
        
    
def convert_points_to_state(points):
    output=('.')*(n+3)*n
    for i in range(0,len(points[0])):
        k=points[0][i]*n+points[1][i]        
        output=output[:k]+'x'+output[k+1:]
    for i in range(0,len(points[2])):
        k=points[2][i]*n+points[3][i]
        output=output[:k]+'o'+output[k+1:]
    return(output)

def successors(board,player='max'):  
    succ=[]   
    visited.append(board)
    if player=='max':
        pos=0
        pother=2
    elif player=='min':
        pos=2
        pother=0
        
        #successor is a list of lists with 'x' coordinates kept first in board, and list of 'o' coordinates kept next
        #=[x_x,x_y,o_x,o_y]
        #where x_x,x_y are list of x and y coordinates i.e. row and column
    
    p_board=board[:]
    rot_board=board[:]
    
    if len(board[0])==0 and len(board[2])==0:
        for i in range(0,n):
            p_board=board[:pos]+[[n-1+3]]+[[i]]+board[pos:] 
           # print(convert_points_to_board(p_board))
            if p_board not in visited:
                succ.append(p_board)
            
    elif len(board[0])==len(board[1]) and len(board[2])==len(board[3]):        
        
        for i in range(0,n):     
            
            list_y_pos=np.array(board[pos+1])                        
            y_ind_pos=np.where(list_y_pos==i)[0]            
            
            list_y_pother=np.array(board[pother+1])            
            y_ind_pother=np.where(list_y_pother==i)[0]
            
            x_ind=[]
            if len(y_ind_pos)>0:
                x_ind.extend([board[pos][j] for j in y_ind_pos])
            if len(y_ind_pother)>0:
                x_ind.extend([board[pother][j] for j in y_ind_pother])
            
            
            
            #where the player will rotate column i    
            rot_board=board[:]
            if len(y_ind_pos)!=0 or len(y_ind_pother)!=0: #no rotation if neither min nor max pebbles in column i.e. column i is empty
                min_x=min(x_ind)
                #print('minx',x_ind)
                for j in  y_ind_pos:
                    if board[pos][j]>=n+3-1:
                        rot_board=rot_board[:pos]+[rot_board[pos][:j]+[min_x]+rot_board[pos][j+1:]]+rot_board[pos+1:]
                    else:
                        rot_board=rot_board[:pos]+[rot_board[pos][:j]+[rot_board[pos][j]+1]+rot_board[pos][j+1:]]+rot_board[pos+1:]
                for j in  y_ind_pother:
                    if board[pother][j]>=n+3-1:
                        rot_board=rot_board[:pother]+[rot_board[pother][:j]+[min_x]+rot_board[pother][j+1:]]+rot_board[pother+1:]
                    else:
                        rot_board=rot_board[:pother]+[rot_board[pother][:j]+[rot_board[pother][j]+1]
                                                      +rot_board[pother][j+1:]]+rot_board[pother+1:]
                #print('rot',convert_points_to_board(rot_board))                
                if (not np.array_equal(np.array(convert_points_to_board(rot_board)),np.array(convert_points_to_board(board)))) and rot_board not in visited:
                    succ.append(rot_board)
                    
            
            #add pebbles of current player pos to ith column
            if len(y_ind_pos)==0 and len(y_ind_pother)==0: #when column does not have max or min pebbles
                
                p_board=board[:pos]+[board[pos][:]+[n+3-1]]+[board[pos+1][:]+[i]]+board[pos+2:]                
               # print('add',convert_points_to_board(p_board))  
                #print(p_board)
                if p_board not in visited:
                    succ.append(p_board)
            else:                                  
                if min_x>0: #add pebbles to column only when column is not full
                    ins=[board[pos][:]+[min_x-1]]
                    p_board=board[:pos]+[board[pos][:]+[min_x-1]]+[board[pos+1][:]+[i]]+board[pos+2:]                    
                    #print('add',convert_points_to_board(p_board))
                   # print(p_board)
                    if p_board not in visited:
                        succ.append(p_board)                
           
            
                
    else:
        print("Error: Code issue")
        
    return(succ)


def vis_col(xlist,lenl,item):#for xlist( list of x cordinates of a column size=lenlx1 ) return an array of strings showing where x (i.e.item) sits 
    bcol=['_']*lenl
    for i in xlist:        
        bcol[i]=item    
    return(bcol)
    
def calc_heu_col(points,player):# for a board find out the minimum cost for winning any column
    if player=='max':
        play=1
        opp=3
        item='x'        
    elif player=='min':
        play=3
        opp=1
        item='o'
        
    col_cost=[n*n*n]*n         #default high cost               
    
    for j in range(0,n):#for each column j
        y_ind_opp=np.where(np.array(points[opp])==j)[0]        
        x_val_opp=[points[opp-1][i] for i in y_ind_opp]         
        y_ind_play=np.where(np.array(points[play])==j)[0]        
        if len(y_ind_play)>0:     #if the columnj has player       
            x_val_play=[points[play-1][i] for i in y_ind_play]            
            x_play=np.array(x_val_play)            
            x_val_play_nxn=x_play[x_play<n]            
            x_val_play_3x3=x_play[x_play>=n]            
            fix_cost=min(x_val_opp+x_val_play) #there will be  min(x_val_opp+x_val_play) number of empty spaces that need to be filled          
            min_x_j=min(x_val_opp+x_val_play)
            if len(x_val_opp)<=3: #if there are more than 3 opponent pieces sitting in column j then the player 
                                #can never complete win the column->cost is set to n*n*n by default for such cases
                k=n-min_x_j      #k gives number of pieces filled in first nxn grid in column j       
                lenstr=k+3                
                consec_str_all=vis_col(x_val_play,n+3,item) 
                consec_str_all=consec_str_all[min_x_j:] 
                consec_str_3x3=vis_col(x_val_play_3x3,n+3,item)
                all_str=consec_str_all+consec_str_all
                pattern=[item]*k #we expect eg. k=2 then xx pattern to fill the occupied places in nxn grid
                if ( ''.join(pattern) in ''.join(all_str) ): #check if we get pattern on rotation
                    x_new=np.array(x_val_play)                    
                    for q in range(0,n+4):    #rotate n+3 times intially 0 to check if existing is correct
                        x_new_nxn=x_new[x_new<n]                        
                        if ''.join(pattern) in ''.join(vis_col(x_new_nxn,n,item)): #if pattern matches on rotation then break
                            col_cost[j]=fix_cost+q
                            break                   
                        x_new=x_new+1
                        x_new[x_new>=n+3]=min_x_j 
        else:
            if len(x_val_opp)<=3 and len(x_val_opp)>0 :            
                col_cost[j]=min(x_val_opp)
            elif len(x_val_opp)==0:
                col_cost[j]=n+3
                    
    return(min(col_cost))

def calc_heu_row(points,player):# for a board find the minimum cost of winning any row
    if player=='max':
        play=1
        opp=3
        item='x'        
    elif player=='min':
        play=3
        opp=1
        item='o'
        
    row_cost=[n*n*n]*n    #default high cost             
    for i in range(0,n): # for each row i
        col_cost=[n*n*n]*n #default high cost
        for j in range(0,n): # for each column j
            y_ind_opp=np.where(np.array(points[opp])==j)[0]        
            x_val_opp=[points[opp-1][i] for i in y_ind_opp]         
            y_ind_play=np.where(np.array(points[play])==j)[0] 
            x_val_play=[points[play-1][i] for i in y_ind_play]            
            if len(x_val_play)>0: # if player in column j
                min_x_j=min(x_val_play+x_val_opp)
                if min_x_j>i:#if there are empty spaces at or below row i
                    col_cost[j]=min_x_j-i                
                else:
                    x_new=np.array(x_val_play)                    
                    for q in range(0,n+4):    # if the pieces have filled up columnj till i or more than i,
                                                # then we rotate and check if we get player at row i
                        if i in x_new:
                            col_cost[j]=q
                            break
                        x_new=x_new+1
                        x_new[x_new>=n+3]=min_x_j  
            elif len(x_val_opp)>0:# if the column j does not have player but has opponent
                x_opp=np.array(x_val_opp)
                min_x_opp=min(x_val_opp)
                if min_x_opp>i:          #if the pieces are filled below the row i (technically above but visually below)  
                                        #if opponent fills the column at or above row i then player cannot win cost is default
                    col_cost[j]=min_x_opp-i 
            else:# if the column is empty
                col_cost[j]=n+3-i               
        
        row_cost[i]=sum(col_cost)
    return(min(row_cost))

def calc_heu_diag(points,player): # use same code as calc_heu_row but instead of running n columns for each row we run it
                                # for j= n-1-i index for right diagonal and j=i for left diagonal
    if player=='max':
        play=1
        opp=3
        item='x'        
    elif player=='min':
        play=3
        opp=1
        item='o'
        
    right_diag_cost=n*n*n 
    col_cost=[n*n*n]*n
    for i in range(0,n):        
        j=n-1-i
        y_ind_opp=np.where(np.array(points[opp])==j)[0]        
        x_val_opp=[points[opp-1][i] for i in y_ind_opp]         
        y_ind_play=np.where(np.array(points[play])==j)[0] 
        x_val_play=[points[play-1][i] for i in y_ind_play]       
        if len(x_val_play)>0:
            min_x_j=min(x_val_play+x_val_opp)
            if min_x_j>i:
                col_cost[j]=min_x_j-i                
            else:
                x_new=np.array(x_val_play)                    
                for q in range(0,n+4):                     
                    if i in x_new:
                        col_cost[j]=q
                        break
                    x_new=x_new+1
                    x_new[x_new>=n+3]=min_x_j  
        elif len(x_val_opp)>0:
            x_opp=np.array(x_val_opp)
            min_x_opp=min(x_val_opp)
            if min_x_opp>i:            
                col_cost[j]=min_x_opp-i
        else:
            col_cost[j]=n+3-i               
        
    right_diag_cost=sum(col_cost)
    
    left_diag_cost=n*n*n
    col_cost=[n*n*n]*n
    for i in range(0,n):        
        j=i
        y_ind_opp=np.where(np.array(points[opp])==j)[0]        
        x_val_opp=[points[opp-1][i] for i in y_ind_opp]         
        y_ind_play=np.where(np.array(points[play])==j)[0] 
        x_val_play=[points[play-1][i] for i in y_ind_play]        
        if len(x_val_play)>0:
            min_x_j=min(x_val_play+x_val_opp)
            if min_x_j>i:
                col_cost[j]=min_x_j-i                
            else:
                x_new=np.array(x_val_play)                    
                for q in range(0,n+4):                     
                    if i in x_new:
                        col_cost[j]=q
                        break
                    x_new=x_new+1
                    x_new[x_new>=n+3]=min_x_j  
        elif len(x_val_opp)>0:
            x_opp=np.array(x_val_opp)
            min_x_opp=min(x_val_opp)
            if min_x_opp>i:            
                col_cost[j]=min_x_opp-i
        else:
            col_cost[j]=n+3-i               
        
    left_diag_cost=sum(col_cost)
    
    #return("left_diag_cost",left_diag_cost,"right_diag_cost",right_diag_cost)
    return(min(left_diag_cost,right_diag_cost))

def heuristic(points,recent_player):
    ret_val=n*n*n*n
    heu_player=min(calc_heu_row(points,player),calc_heu_col(points,player),calc_heu_diag(points,player))
    heu_opp=min(calc_heu_row(points,opp),calc_heu_col(points,opp),calc_heu_diag(points,opp))
    if heu_player>=n*n*n and heu_opp>=n*n*n:
        ret_val=n*n*n
    elif heu_player<heu_opp:
        ret_val=heu_player
    elif heu_player==heu_opp:
        if heu_player==0 and recent_player=='max':
            ret_val=heu_player
        elif heu_player>0 and recent_player=='opp':
            ret_val=heu_player
    return(ret_val)
    
            
def max_value(Sb,alpha,beta,depth,prev_cost): 
    current=(float(str(datetime.now()).split(':')[1]))*60+float(str(datetime.now()).split(':')[2])    
    if (current-start)>=t:       
        return(prev_cost)
    if depth==4 or heuristic(Sb,player)==0 :
        return(heuristic(Sb,player)+depth)
    depth+=1
    for succ in successors(Sb,opp):        
        res=min_value(succ,alpha,beta,depth,prev_cost)      
        alpha=max(alpha,res)       
        if alpha>=beta:
            return(alpha)
    return(alpha)

def min_value(Sb,alpha,beta,depth,prev_cost):
    current=(float(str(datetime.now()).split(':')[1]))*60+float(str(datetime.now()).split(':')[2])    
    if (current-start)>=t:        
        return(prev_cost)
    if depth==4 or heuristic(Sb,opp)==0:
        return(heuristic(Sb,opp)+depth)
    depth+=1
    for succ in successors(Sb,player):        
        res=max_value(succ,alpha,beta,depth,prev_cost)       
        beta=min(beta,res)
        if alpha>=beta:
            return(beta)
    return(beta)
    

def minimax(Sb,alpha,beta,depth):    
    depth+=1     
    prev=n*n*n*n*n
    ans=[]
    for succ in successors(Sb,player): 
        current=(float(str(datetime.now()).split(':')[1]))*60+float(str(datetime.now()).split(':')[2])
        if (current-start)>=t:
            print("Stopping abruptly")
            if len(ans)==0:
                return(succ)
            else:
                return(ans)
        if len(ans)==0:
            print(str(next_move(succ))+' '+convert_points_to_state(succ))        
        res=max_value(succ,alpha,beta,depth,prev)
        if res<=prev:            
            prev=res
            ans=succ        
        print(str(next_move(ans))+' '+convert_points_to_state(ans))
    return(ans)
          
def next_move(points):
    initial_points=initial_board
    if player=='max':
        pos=0
    elif player=='min':
        pos=2
    length=len(points[pos])        
    if len(initial_points[pos])<len(points[pos]):
        return(points[pos+1][length-1]+1)
    elif len(initial_points[pos])==len(points[pos]):
        p=np.array(points)
        init=np.array(initial_points)
        for j in range(0,n):            
            y_ind_new=np.where(np.array(points[pos+1])==j)[0]            
            x_val_new=[points[pos][i] for i in y_ind_new]            
            y_ind_old=np.where(np.array(init[pos+1])==j)[0]            
            x_val_old=[init[pos][i] for i in y_ind_old]            
            if not np.array_equal(np.array(x_val_new),np.array(x_val_old)):
                return(-(j+1))
    return(n)

# n=3
# p='x'
# # STATE='...o..x.ooooxxxxxo'
# #STATE='......o..x.oxxxoxo'
# STATE='...x..x.ox.oxxooxx'
# #STATE='...x..o.oxooxxxoxo'
# t=5

n=int(sys.argv[1])
p=str(sys.argv[2])
STATE=str(sys.argv[3])
t=int(sys.argv[4])


depth=0 # run minimax till depth 5
# a bit confusing, max is just a word for 'x'
#the variable "player" signifies the max player and the variable "opp" signifies the min player in a minimax algo
if p=='x':
    player='max'
    opp='min'
elif p=='o':
    player='min'
    opp='max'
ALPHA=-(n*n+100)
BETA=n*n+100
visited=[]

start = (float(str(datetime.now()).split(':')[1]))*60+float(str(datetime.now()).split(':')[2])


initial_board=convert_board_to_points(convert_state_to_board(STATE))
print('you entered:')
print(convert_points_to_board(initial_board))

print('your next move')
next_board=minimax(initial_board,ALPHA,BETA,depth)
action=str(next_move(next_board))
if int(action)>0:
    print("I would recommend dropping a pebble in column "+action)
else:
    print("I would recommend rotating column "+action)
print(action+" "+convert_points_to_state(next_board))

