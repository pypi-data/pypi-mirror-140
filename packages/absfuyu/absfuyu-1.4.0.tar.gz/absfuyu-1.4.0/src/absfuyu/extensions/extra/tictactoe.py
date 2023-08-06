#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABSFUYU-EXTRA: GAME
-------------
"""



# Library
##############################################################
import random as __random

__EXTRA_MODE = False
try:
    import numpy as __np
except ImportError:
    from absfuyu.config import show_cfg as __aie
    if __aie("auto-install-extra", raw=True):
        __cmd: str = "python -m pip install -U absfuyu[extra]".split()
        from subprocess import run as __run
        __run(__cmd)
    else:
        raise SystemExit("This feature is in absfuyu[extra] package")
else:
    __EXTRA_MODE = True

from absfuyu import core as __core

# Tic Tac Toe
##############################################################

# GAME SETTING
X = "X"
O = "O"
BLANK = " "
__C = __core.Color

# FUNCTIONS
def __check_state(table: __np.ndarray):
    """
    Check game winning state
    
    Parameter:
        table: numpy.ndarray
    
    Return:
        "X","O"," "
    """

    # Data
    nrow, ncol = table.shape

    # Check rows
    for row in range(nrow):
        if len(set(table[row])) == 1:
            # return list(set(table[row]))[0]
            key = list(set(table[row]))[0]
            return {"key": key, "location": "row", "pos": row} # modified

    # Check cols
    for col in range(ncol):
        temp = []
        for row in range(nrow):
            temp.append(table[row][col])

        if len(set(temp)) == 1:
            # return list(set(temp))[0]
            key = list(set(temp))[0]
            return {"key": key, "location": "col", "pos": col} # modified
    
    # Check diagonal
    diag1 = [table[i][i] for i in range(len(table))]
    if len(set(diag1)) == 1:
        # return list(set(diag1))[0]
        key = list(set(diag1))[0]
        return {"key": key, "location": "diag", "pos": 1} # modified
    
    diag2 = [table[i][len(table)-i-1] for i in range(len(table))]
    if len(set(diag2)) == 1:
        # return list(set(diag2))[0]
        key = list(set(diag2))[0]
        return {"key": key, "location": "diag", "pos": 2} # modified
    
    # Else
    # return BLANK
    return {"key": BLANK}

def __print_board(table: __np.ndarray):
    """Print Tic Tac Toe board"""
    nrow, ncol = table.shape
    length = len(table)
    print(f"{'+---'*length}+")
    for row in range(nrow):
        for col in range(ncol):
            print(f"| {table[row][col]} ", end="")
        print("|")
        print(f"{'+---'*length}+")

def __win_hightlight(table: __np.ndarray):
    """
    Hight light the win by removing other placed key
    """

    detail = __check_state(table)
    loc = detail["location"]
    loc_line = detail["pos"]

    board = __np.full((len(table),len(table))," ")
    table = board

    if loc.startswith("col"):
        for i in range(len(table)):
            table[i][loc_line] = detail['key']
    elif loc.startswith("row"):
        for i in range(len(table)):
            table[loc_line][i] = detail['key']
    else:
        if loc_line == 1:
            for i in range(len(table)):
                table[i][i] = detail['key']
        else:
            for i in range(len(table)):
                table[i][len(table)-i-1] = detail['key']
    
    __print_board(board)
    pass

def game_tictactoe(size: int = 3, mode: str = "1v0"):
    """
    Tic Tac Toe

    Mode:
        "1v1": Player vs player
        "1v0": Player vs BOT
    """

    # Init game
    board = __np.full((size,size)," ")
    filled = 0
    current_player = X
    # state = __check_state(board)
    state = __check_state(board)["key"]

    # Welcome message
    print(f"""\
{__C['green']}Welcome to Tic Tac Toe")

{__C['yellow']}Match three lines vertically, horizontally or diagonally")
{__C['yellow']}{X} goes first, then {O}")
{__C['RED']}Type 'END' to end the game""")

    # Check gamemode
    game_mode = [
        "1v1", # Player vs player
        "1v0" # Player vs BOT
    ]
    if mode not in game_mode:
        mode = game_mode[1] # Force vs BOT
    if mode.startswith("1v0"):
        BOT = True
    
    # Game
    __print_board(board)
    while state == BLANK and filled < size**2:
        print(f"{__C['blue']}{current_player}'s turn:")
        
        try: # Error handling
            if BOT and current_player == O:
                move = f"{__random.randint(1,size)},{__random.randint(1,size)}"
            else:
                move = input(f"Place {current_player} at row, col: ")
            
            if move.upper() == "END": # Failsafe
                print(f"{__C['red']}Game ended")
                break
            
            move = move.split(",")
            row = int(move[0])
            col = int(move[1])

            if board[row-1][col-1] == BLANK:
                board[row-1][col-1] = current_player
            else:
                if BOT and current_player == O:
                    print(f"{__C['red']}Move failed, trying again...")
                    continue
                print(f"{__C['red']}Invalid move, please try again")
                continue
        except:
            if BOT and current_player == O:
                print(f"{__C['red']}Move failed, trying again...")
                continue
            print(f"{__C['red']}Invalid move, please try again")
            continue
        
        state = __check_state(board)["key"]
        __print_board(board)

        # state = __check_state(board)
        if state != BLANK:
            print(f"{__C['green']}{state} WON!")
            __win_hightlight(board)
            break

        # Change turn
        filled += 1
        if current_player == X:
            current_player = O
        else:
            current_player = X

    if state == BLANK and filled == size**2:
        print(f"{__C['yellow']}Draw Match!")