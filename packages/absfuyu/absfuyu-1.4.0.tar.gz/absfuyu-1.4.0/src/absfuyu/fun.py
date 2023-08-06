#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fun Module
------------------
Some fun or weird stuff

Contain:
- Game
- happy_new_year
"""


# Module level
##############################################################
__all__ = [
    "game_escapeLoop", "game_RockPaperScissors",
    "happy_new_year", "zodiac_sign", "im_bored"
]





# Library
##############################################################
from datetime import date as __date
from random import choice as __randChoice




# Game
##############################################################
def game_escapeLoop():
    """Try to escape the infinite loop"""
    
    init = True
    welcome_messages = [
        "Congrats! You are now stuck inside an infinite loop.",
        "Do you want to escape this loop?"
    ]

    num1 = __randChoice([2,3,4,5,6,7,8,9,10,11,12])
    num2 = __randChoice([2,3,4,5,6,7,8,9,10,11,12])
    hidden_answer = str(num1 * num2)

    game_messages = [
        "Are you sure about this?",
        "Don't leave me =((",
        "I can't believe you did this to me!",
        "Are you very much sure?",
        "I'll be sad. Pick again please.",
        "I still don't believe you.", 
        "Choose again.",
        "You actually have to answer the correct keyword",
        "I think you need to choose again.",
        "Last chance!",
        "Okay okay, i believe you ;)",
        "Almost there.",
        "I can do this all day", 
        "So close!",
        "You can't escape from me.",
        "How are you still here, just to suffer?",
        "Never gonna give you up",
        "Never gonna let you down",
        f"Hint 01: The keyword is: {num1}",
        f"Hint 02: *{num2}",
    ]

    congrats_messages = [
        "Congratulation! You've escaped."
    ]
    
    while True:
        # Welcome
        if init:
            for x in welcome_messages:
                print(x)
            answer = str(input())
            init = False
        
        # Random text
        mess = __randChoice(game_messages)
        print(mess)

        # Condition check
        answer = str(input())
        if answer == hidden_answer:
            for x in congrats_messages:
                print(x)
            break
    pass


def game_RockPaperScissors(hard_mode=False):
    """Rock Paper Scissors"""
    
    state_dict = {
        0: "rock",
        1: "paper",
        2: "scissors"
    }
    
    init = True

    end_message = "end"

    welcome_messages = [
        "Welcome to Rock Paper Scissors",
        f"Type '{end_message}' to end",
    ]

    game_messages = [
        "Pick one option to begin:",
    ]

    game_summary = {
        "Win": 0,
        "Draw": 0,
        "Lose": 0
    }
    
    while True:
        # Welcome
        if init:
            for x in welcome_messages:
                print(x)
            init = False
        
        # Game start
        print("")
        for x in game_messages:
            print(x)
        print(state_dict)
        
        # Player's choice
        answer = input()

        # Condition check
        if answer == end_message:
            print(game_summary)
            break
        
        elif answer not in ["0","1","2"]:
            print("Invalid option. Choose again!")
        
        else:
            # Calculation
            answer = int(answer)
            if hard_mode:
                if answer == 0:
                    game_choice = __randChoice([0,1])
                if answer == 1:
                    game_choice = __randChoice([1,2])
                if answer == 2:
                    game_choice = __randChoice([0,2])
            else:
                game_choice = __randChoice([0,1,2])
            print(f"You picked: {state_dict[answer]}")
            print(f"BOT picked: {state_dict[game_choice]}")
            
            if answer == 2 and game_choice == 0:
                print("You Lose!")
                game_summary["Lose"] += 1
            elif answer == 0 and game_choice == 2:
                print("You Win!")
                game_summary["Win"] += 1
            elif answer == game_choice:
                print("Draw Match!")
                game_summary["Draw"] += 1
            elif answer > game_choice:
                print("You Win!")
                game_summary["Win"] += 1
            else:
                print("You Lose!")
                game_summary["Lose"] += 1

    return game_summary




# Function
##############################################################
def zodiac_sign(
        day: int,
        month: int,
        zodiac13: bool = False,
        debug: bool = False
    ):
    """
    Calculate zodiac sign

    Include 13 zodiacs mode
    """

    # Condition check
    conditions = [
        0 < day < 32,
        0 < month < 13,
    ]
    if not all(conditions):
        raise SystemExit("Value out of range")

    zodiac = {
        "Aquarius": any([
            month == 1 and day >= 20,
            month == 2 and day <= 18
        ]), # 20/1-18/2
        "Pisces": any([
            month == 2 and day >= 19,
            month == 3 and day <= 20
        ]), # 19/2-20/3
        "Aries": any([
            month == 3 and day >= 21,
            month == 4 and day <= 19
        ]), # 21/3-19/4
        "Taurus": any([
            month == 4 and day >= 20,
            month == 5 and day <= 20
        ]), # 20/4-20/5
        "Gemini": any([
            month == 5 and day >= 21,
            month == 6 and day <= 20
        ]), # 21/5-20/6
        "Cancer": any([
            month == 6 and day >= 21,
            month == 7 and day <= 22
        ]), # 21/6-22/7
        "Leo": any([
            month == 7 and day >= 23,
            month == 8 and day <= 22
        ]), # 23/7-22/8
        "Virgo": any([
            month == 8 and day >= 23,
            month == 9 and day <= 22
        ]), # 23/8-22/9
        "Libra": any([
            month == 9 and day >= 23,
            month == 10 and day <= 22
        ]), # 23/9-22/10
        "Scorpio": any([
            month == 10 and day >= 23,
            month == 11 and day <= 21
        ]), # 23/10-21/11
        "Sagittarius":any([
            month == 11 and day >= 22,
            month == 12 and day <= 21
        ]), # 22/11-21/12
        "Capricorn": any([
            month == 12 and day >= 22,
            month == 1 and day <= 19
        ]), # 22/12-19/1
    }
    
    if zodiac13: # 13 zodiac signs
        zodiac = {
            "Aquarius": any([
                month == 2 and day >= 17,
                month == 3 and day <= 11
            ]), # 17/2-11/3
            "Pisces": any([
                month == 3 and day >= 12,
                month == 4 and day <= 18
            ]), # 12/3-18-4
            "Aries": any([
                month == 4 and day >= 19,
                month == 5 and day <= 13
            ]), # 19/4-13-5
            "Taurus": any([
                month == 5 and day >= 14,
                month == 6 and day <= 21
            ]), # 14/5-21/6
            "Gemini": any([
                month == 6 and day >= 22,
                month == 7 and day <= 20
            ]), # 22/6-20/7
            "Cancer": any([
                month == 7 and day >= 21,
                month == 8 and day <= 10
            ]), # 21/7-10/8
            "Leo": any([
                month == 8 and day >= 11,
                month == 9 and day <= 16
            ]), # 11/8-16/9
            "Virgo": any([
                month == 9 and day >= 17,
                month == 10 and day <= 30
            ]), # 17/9-30/10
            "Libra": any([
                month == 10 and day >= 31,
                month == 11 and day <= 23
            ]), # 31/10-23/11
            "Scorpio": any([
                month == 11 and day >= 24,
                month == 11 and day <= 29
            ]), # 24/11-29/11
            "Ophiuchus": any([
                month == 11 and day >= 30,
                month == 12 and day <= 17
            ]), # 30/11-17/12
            "Sagittarius":any([
                month == 12 and day >= 18,
                month == 1 and day <= 20
            ]), # 18/12-20/1
            "Capricorn": any([
                month == 1 and day >= 21,
                month == 2 and day <= 16
            ]), # 21/1-16/2
        }

    if debug:
        print(zodiac)
    
    for k, v in zodiac.items():
        if v is True:
            return k

def im_bored():
    from absfuyu import version as v
    api = "https://www.boredapi.com/api/activity"
    return v.__load_data_from_json_api(api)["activity"]


def force_shutdown():
    """Force the computer to shutdown"""
    
    import subprocess
    import sys
    
    # get operating system
    os_name = sys.platform

    # shutdown
    shutdown = {
        # Windows
        "win32": "shutdown -f -s -t 0".split(),
        "cygwin": "shutdown -f -s -t 0".split(),
        # Mac OS
        "darwin": ['osascript', '-e', 'tell app "System Events" to shut down'],
        # Linux
        "linux": "shutdown -h now".split(),
    }

    if os_name in shutdown:
        return subprocess.run(shutdown[os_name])
    else:
        return subprocess.run(shutdown["linux"])


# For new year only
def happy_new_year(forced: bool = False):
    """Only occurs on 01/01 every year"""

    if forced:
        return force_shutdown()

    m = __date.today().month
    d = __date.today().day

    if m==1 and d==1:
        print("Happy New Year! You should take rest now.")
        return force_shutdown()
    else:
        raise SystemExit("The time has not come yet")