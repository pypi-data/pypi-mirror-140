#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABSFUYU-EXTRA: TIC TAC TOE
-------------
"""



# Library
##############################################################
import random as __random
import time as __time
from typing import Optional as __Optional
from subprocess import run as __run

from sys import version_info as __py_ver
if __py_ver[0] == 3:
    if __py_ver[1] == 7:
        try:
            from typing_extensions import Literal as __Literal
        except ImportError as err:
            __cmd = [
                "python -m pip install typing_extensions".split(),
            ]
            for x in __cmd:
                __run(x)
    else:
        from typing import Literal as __Literal
else:
    raise SystemExit("Not Python 3")

__EXTRA_MODE = False
try:
    import numpy as __np
except ImportError:
    from absfuyu.config import show_cfg as __aie
    if __aie("auto-install-extra", raw=True):
        __cmd: str = "python -m pip install -U absfuyu[extra]".split()
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

# TYPE HINT
Gamemode = __Literal["1v1", "1v0", "0v0"]

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

def game_tictactoe(
        size: int = 3,
        mode: Gamemode = "1v0",
        board_game: __Optional[bool] = True,
        bot_time: float = 0
    ):
    """
    Tic Tac Toe

    Parameters:
    ---
    mode : str
        "1v1": Player vs player
        "1v0": Player vs BOT
        "0v0": BOT vs BOT
    
    board_game : True | False | None
        True: draw board
        False: print array
        None: no board or array

    bot_time : float
        time sleep between each bot move
    
    Return:
    ---
    Game stats
    """

    # Init game
    board = __np.full((size,size)," ")
    filled = 0
    current_player = X
    # state = __check_state(board)
    state = __check_state(board)["key"]
    BOT = False
    BOT2 = False

    # Welcome message
    if board_game is not None:
        print(f"""\
{__C['green']}Welcome to Tic Tac Toe")

{__C['yellow']}Match three lines vertically, horizontally or diagonally")
{__C['yellow']}{X} goes first, then {O}")
{__C['RED']}Type 'END' to end the game{__C['reset']}""")
    else:
        print("Tic Tac Toe")

    # Check gamemode
    game_mode = [
        "1v1", # Player vs player
        "1v0", # Player vs BOT
        "0v0" # BOT vs BOT
    ]
    if mode not in game_mode:
        mode = game_mode[1] # Force vs BOT
    if mode.startswith("1v0"):
        BOT = True
    if mode.startswith("0v0"):
        BOT2 = True
    
    # Game
    if board_game:
        __print_board(board)
    elif board_game is None:
        pass
    else:
        print(board)
    while state == BLANK and filled < size**2:
        if board_game is not None:
            print(f"{__C['blue']}{current_player}'s turn:{__C['reset']}")
        
        try: # Error handling
            if BOT and current_player == O:
                move = f"{__random.randint(1,size)},{__random.randint(1,size)}"
            elif BOT2:
                move = f"{__random.randint(1,size)},{__random.randint(1,size)}"
            else:
                move = input(f"Place {current_player} at row, col: ")
            
            if move.upper() == "END": # Failsafe
                print(f"{__C['red']}Game ended{__C['reset']}")
                break
            
            move = move.split(",")
            row = int(move[0])
            col = int(move[1])

            if board[row-1][col-1] == BLANK:
                board[row-1][col-1] = current_player
            else:
                if board_game is not None:
                    if (BOT and current_player == O) or (BOT2):
                        print(f"{__C['red']}Move failed, trying again...{__C['reset']}")
                        continue
                    print(f"{__C['red']}Invalid move, please try again{__C['reset']}")
                continue
        except:
            if board_game is not None:
                if (BOT and current_player == O) or (BOT2):
                    print(f"{__C['red']}Move failed, trying again...{__C['reset']}")
                    continue
                print(f"{__C['red']}Invalid move, please try again{__C['reset']}")
            continue
        
        state = __check_state(board)["key"]
        if board_game:
            __print_board(board)
        elif board_game is None:
            pass
        else:
            print(board)

        # state = __check_state(board)
        if state != BLANK:
            print(f"{__C['green']}{state} WON!{__C['reset']}")
            if board_game:
                __win_hightlight(board)
            break

        # Change turn
        filled += 1
        if BOT2:
            __time.sleep(bot_time)
        if current_player == X:
            current_player = O
        else:
            current_player = X

    if state == BLANK and filled == size**2:
        print(f"{__C['yellow']}Draw Match!{__C['reset']}")
    
    return {"number of move": filled}