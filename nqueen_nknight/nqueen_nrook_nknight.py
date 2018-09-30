#!/usr/bin/env python3
# nrooks.py : Solve the N-Rooks problem!
# The N-rooks problem is: Given an empty NxN chessboard, place N rooks on the board so that no rooks
# can take any other, i.e. such that no two rooks share the same row or column.
#sample input  python nqueen_nrook_nknight.py nrook 7 1 1 1
#max for nrook- 778x778
#              python nqueen_nrook_nknight.py nqueen 8 2 1 2 1 8
#max for nqueen- 27x27
#              python nqueen_nrook_nknight.py nknight 8 2 1 2 1 8
import sys

#list of unavailable points
def coordinate_list(length):
    X=[]
    for i in range(1, length + 1):
        x = int(sys.argv[2*i+2])
        y = int(sys.argv[2*i+3])
        X.append([x, y])
    return(X)

# Return a string with the board rendered in a human-friendly format
def nqueen_printboard(board):
    return "\n".join(
        [" ".join(["X" if [row + 1, col + 1] in X else "Q" if [row,col] in board else "_" for col in range(0, N)]) for row in range(0, N)])


def nrook_printboard(board):
    return "\n".join(
        [" ".join(["X" if [row + 1, col + 1] in X else "R" if [row, col] in board else "_" for col in range(0, N)]) for row in range(0, N)])

def nknight_printboard(board):
    return "\n".join(
        [" ".join(["X" if [row + 1, col + 1] in X else "K" if [row, col] in board else "_" for col in range(0, N)]) for row in range(0, N)])

#nqueen successor!
def nqueen_successor3(board):
    board_suc=[]
    if len(board)==0:
        c=0
    else:
        c=board[len(board)-1][1]+1
    for r in range(0,N):
        #successor do not lie in same row or column as the predecessors
        if (r in [each[0] for each in board]) or ([r+1,c+1] in X):
            continue
        else:
            flag=1
            for point in board:
                # successor do not lie diagonally to the predecessors - used slope formula to test
                if (point[1]-c)/((point[0]-r)*1.0)==1 or (point[1]-c)/((point[0]-r)*1.0)==-1:
                    flag=0
                    break
            if flag==1:
                board_suc+=[board[0:N]+[[r,c]]]

    return(board_suc)

#nrook successor!
def nrook_successor3(board):
    board_suc=[]
    if len(board)==0:
        c=0
    else:
        c=board[len(board)-1][1]+1
    # successor do not lie in same row or column as the predecessors
    for r in range(N-1,-1,-1):
        if (r in [each[0] for each in board]) or ([r+1,c+1] in X):
            continue
        else:
            board_suc+=[board[0:N]+[[r,c]]]
    return(board_suc)




def nknight_successor3(board):
    board_suc=[]
    if (len(board)<N):# do not add successors if the rooks on board are already N in number
        for c in range (0,N): #for every point on board check
            for r in range(0,N):
                if [r+1,c+1] in X or [r,c] in board:
                    continue
                if len(board)==0: #initially board has no pieces
                    board_suc+=[board[0:N]+[[r,c]]]
                else:
                    flag=0
                    for each in board:
                        x=each[0]; y=each[1]
                       #points that are under attack
                        attack = [[x - 1, y + 2], [x + 1, y + 2], [x - 2, y + 1], [x - 2, y - 1], [x - 1, y - 2],
                              [x + 1, y - 2],[x + 2, y - 1], [x + 2, y + 1]]

                        if [r,c] in attack:
                            flag=1
                            break
                    if flag==0:
                        #print('add',r,c) add a piece on board if  r,c is not under attack by other pieces or is not an existing piece
                        board_suc += [board[0:N] + [[r, c]]]
    return(board_suc)


def nknight_is_goal(board):
    if(len(board)) == N:
        for p in range(1, N):
            x = board[p][0];
            y = board[p][1]
            attack = [[x - 1, y + 2], [x + 1, y + 2], [x - 2, y + 1], [x - 2, y - 1], [x - 1, y - 2],
                      [x + 1, y - 2], [x + 2, y - 1], [x + 2, y + 1]]
            for i in range(0, p):
                if ([board[i][0], board[i][1]] not in attack):
                    return True
    return False




# check if board is a goal state
def nqueen_is_goal(board):
    if(len(board)) != N:
        return False
    else:
        for p in range(1,N):
            for i in range(0,p):
                if (board[p][0]==board[i][0]) or (board[p][1]==board[i][1]) or (board[p][1]-board[i][1])/((board[p][0]-board[i][0])*1.0)==1  or (board[p][1]-board[i][1])/((board[p][0]-board[i][0])*1.0)==-1:
                    return False

    return True

def nrook_is_goal(board):
    if(len(board)) != N:
        return False
    else:
        for p in range(1,N):
            for i in range(0,p):
                if (board[p][0]==board[i][0]) or (board[p][1]==board[i][1]):
                    return False

    return True


def nqueen_solve(initial_board):
    fringe = [initial_board]
    while len(fringe) > 0:
        for s in nqueen_successor3(fringe.pop()):
            if nqueen_is_goal(s):
                return(s)
            fringe.append(s)
    return False

def nrook_solve(initial_board):
    fringe = [initial_board]
    while len(fringe) > 0:
        for s in nrook_successor3(fringe.pop()):
            if nrook_is_goal(s):
                return(s)
            fringe.append(s)
    return False

def nknight_solve(initial_board):

    fringe = [initial_board]
    while len(fringe) > 0:
        for s in nknight_successor3(fringe.pop()):
            if nknight_is_goal(s):
                return(s)
            fringe.append(s)
    return False

#nqueen or nrook
PType=str(sys.argv[1])
if (PType!= "nqueen" and PType!="nrook" and PType!="nknight"):
    print('Invalid input. Please try again!')
    exit()

#NxN list
N = int(sys.argv[2])

#make list of unavailable points
X=[]
if (int(sys.argv[3])>0):
    X = coordinate_list(int(sys.argv[3]))


# The board is stored as a list-of-lists. Each inner list is a point with a piece on the board.
#initially no pieces are placed so initial board is empty
initial_board = []

if(PType== "nqueen"):
    solution = nqueen_solve(initial_board)
elif (PType=="nrook"):
    solution = nrook_solve(initial_board)
else:
    solution = nknight_solve(initial_board)

print ( "Sorry, no solution found. :(" if not solution else nknight_printboard(solution) if PType=='nknight'  else nqueen_printboard(solution) if PType=='nqueen' else nrook_printboard(solution))


