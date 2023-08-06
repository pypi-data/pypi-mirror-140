# -*- coding: utf-8 -*-
"""
SUDOKU MODULE
-------------

Sudoku solver
9x9 only
"""

# Module level
##############################################################
__all__ = [
    # Demo data
    "demo_sudoku_data",
    # Function
    "sudoku_to_string", "string_to_sudoku",
    "print_board", "solve_sudoku",
]


# Library
##############################################################
from typing import (
    Dict as __Dict,
    Union as __Union,
)

from absfuyu.core import (
    Sudoku as __Sudoku,
    SudokuStr as __SudokuStr,
    SudokuStrStyle as __SudokuStrStyle,
    Position as __Pos,
)



# Demo Data
##############################################################
demo_sudoku_data: __Dict[str, __Sudoku] = {
    "hardest_sudoku": [ # https://www.telegraph.co.uk/news/science/science-news/9359579/Worlds-hardest-sudoku-can-you-crack-it.html
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 6, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 9, 0, 2, 0, 0],
        [0, 5, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 4, 5, 7, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 3, 0],
        [0, 0, 1, 0, 0, 0, 0, 6, 8],
        [0, 0, 8, 5, 0, 0, 0, 1, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0],
    ], # 8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..
    "hardest_sudoku_ans": [ # Answer
        [8, 1, 2, 7, 5, 3, 6, 4, 9],
        [9, 4, 3, 6, 8, 2, 1, 7, 5],
        [6, 7, 5, 4, 9, 1, 2, 8, 3],
        [1, 5, 4, 2, 3, 7, 8, 9, 6],
        [3, 6, 9, 8, 4, 5, 7, 2, 1],
        [2, 8, 7, 1, 6, 9, 5, 3, 4],
        [5, 2, 1, 9, 7, 4, 3, 6, 8],
        [4, 3, 8, 5, 2, 6, 9, 1, 7],
        [7, 9, 6, 3, 1, 8, 4, 5, 2],
    ],
    "sudoku": [ # Demo sudoku
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7],
    ],
}




# Function
##############################################################
def sudoku_to_string(
        sudoku: __Sudoku,
        style: __SudokuStrStyle = "zero"
    ) -> __SudokuStr:
    style_option = ["zero", "dot"]
    
    if style not in style_option:
        style = "zero"
    
    out = "".join(str(sudoku))
    remove = ["[", "]", " ", ","]
    for x in remove:
        out = out.replace(x,"")
    
    if style.startswith("zero"):
        return out
    elif style.startswith("dot"):
        out = out.replace("0",".")
        return out
    else:
        return out

def __sudoku_str_validate(sudoku_string: __SudokuStr):
    if len(sudoku_string) == 81:
        return True
    else:
        return False

def string_to_sudoku(sudoku_string: __SudokuStr) -> __Sudoku:
    if __sudoku_str_validate(sudoku_string):
        sdk = str(sudoku_string).replace(".","0")
        # sdk_len = math.sqrt(len(sudoku_string))
        temp = []
        while len(sdk) != 0:
            temp.append(sdk[:9])
            sdk = sdk[9:]
        out = []
        for value in temp:
            temp_list = [int(x) for x in value]
            out.append(temp_list)

        return out
    
    else:
        raise SystemExit("Invalid length")

def print_board(sudoku: __Union[__Sudoku, __SudokuStr]) -> None:
    """
    Print sudoku board
    """
    if isinstance(sudoku, __SudokuStr):
        sudoku = string_to_sudoku(sudoku)
    # row_len = len(sudoku)
    # col_len = len(sudoku[0])
    for i in range(len(sudoku)):
        if i % 3 == 0:
            if i == 0:
                print(" ┎─────────────────────────────┒")
            else:
                print(" ┠─────────────────────────────┨")

        for j in range(len(sudoku[0])):
            if j % 3 == 0:
                print(" ┃ ", end=" ")

            if j == 8:
                print(sudoku[i][j], " ┃")
            else:
                print(sudoku[i][j], end=" ")

    print(" ┖─────────────────────────────┚")
    pass

# Source: https://www.techwithtim.net/tutorials/python-programming/sudoku-solver-backtracking/
def __find_empty(sudoku: __Sudoku) -> __Pos:
    """
    Find the empty cell (value = 0)

    Return postion(row, col)

    If not empty then return None
    """

    row_len = len(sudoku)
    col_len = len(sudoku[0])
    for row in range(row_len):
        for col in range(col_len):
            if sudoku[row][col] == 0:
                # Return position when empty
                return (row, col)
    # Return None when there is no empty cell
    return None

def __is_valid(sudoku: __Sudoku, number: int, position: __Pos) -> bool:
    """
    Check valid number value in row, column, box
    """

    row_len = len(sudoku)
    col_len = len(sudoku[0])
    row, col = position # unpack tuple

    # Check row
    for i in range(col_len): # each item in row i; row i has `col_len` items
        if sudoku[row][i] == number and col != i:
            return False

    # Check column
    for i in range(row_len):
        if sudoku[i][col] == number and row != i:
            return False

    # Check box
    box_x = col // 3
    box_y = row // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if sudoku[i][j] == number and (i,j) != position:
                return False

    # If everything works
    return True

def __solve(sudoku: __Sudoku) -> bool:
    """
    Solve sudoku (backtracking method)
    """

    # Find empty cell
    empty_pos = __find_empty(sudoku)
    if empty_pos is None:
        return True # solve_state (True: every cell filled)
    else:
        # unpack position when exist empty cell
        row, col = empty_pos

    for num in range(1,10): # sudoku value (1-9)
        if __is_valid(sudoku, num, empty_pos):
            sudoku[row][col] = num

            # Recursive
            if __solve(sudoku):
                return True

            sudoku[row][col] = 0

    # End recursive
    return False

def solve_sudoku(sudoku: __Union[__Sudoku, __SudokuStr]) -> __Sudoku:
    if isinstance(sudoku, __SudokuStr):
        ori = string_to_sudoku(sudoku)
        sol = ori
    else:
        ori = sudoku_to_string(sudoku=sudoku, style="dot") # Make backup
        sol = string_to_sudoku(sudoku_string=ori)

    data = {
        "original": ori,
        "solved": []
    }
    __solve(sol)
    
    test_case = sudoku_to_string(sol)
    if "0" in test_case:
        raise SystemExit("Unsolvable")
    
    data["solved"] = sol
    return data["solved"]


# print_board(".......57....563...85....148..7....6..4.6.5...7...8.2..3....2..9.234.7..1.8......")
# print_board(solve_sudoku(".......57....563...85....148..7....6..4.6.5...7...8.2..3....2..9.234.7..1.8......"))