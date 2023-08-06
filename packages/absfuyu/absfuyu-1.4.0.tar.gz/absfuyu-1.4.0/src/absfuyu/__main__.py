#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABSFUYU
-------
COMMAND LINE INTERFACE
"""


# Library
##############################################################
from email.policy import default
from random import choice as __randc
from subprocess import run as __run

CLI_MODE = False
try:
    import click as __click
    import colorama as __colorama
except ImportError:
    # Auto install absfuyu[cli]
    from .config import show_cfg as __aie
    if __aie("auto-install-extra", raw=True):
        __cmd: str = "python -m pip install -U absfuyu[cli]".split()
        __run(__cmd)
    else:
        raise SystemExit("This feature is in absfuyu[cli] package")
else:
    CLI_MODE = True

from .config import (
    show_cfg as __scfg,
    reset_cfg as __reset,
    welcome as __welcome,
    toggle_setting as __togg,
)

from . import core as __core
from . import version as __v
from .generator import randStrGen as __randStr




# Color stuff
##############################################################
if CLI_MODE:
    if __colorama is not None:
        __colorama.init(autoreset=True)
        __COLOR = __core.Color
    else:
        __COLOR = {"green":"", "blue":"", "red":"", "yellow":"", "reset":""}



# Main group
##############################################################
@__click.command()
def welcome():
    """Welcome message"""
    import os as __os
    try:
        user = __os.getlogin()
    except:
        import getpass
        user = getpass.getuser()
    welcome_msg = f"{__COLOR['green']}Welcome {__COLOR['red']}{user} {__COLOR['green']}to {__COLOR['blue']}absfuyu's cli"
    __click.echo(f"""
        {__COLOR['reset']}{'='*(len(welcome_msg)-20)}
        {welcome_msg}
        {__COLOR['reset']}{'='*(len(welcome_msg)-20)}
    """)
    __welcome()


@__click.command()
@__click.argument("name")
def greet(name):
    """Greet"""
    __click.echo(f"{__COLOR['yellow']}Hello {name}")


@__click.command()
@__click.option(
    "--setting", "-s",
    type=__click.Choice(["luckgod", "install-extra"]),
    help="Toggle on/off selected setting")
def toggle(setting: str):
    """Toggle on/off setting"""

    # Dictionary
    trans = {
        "luckgod": "luckgod-mode",
        "install-extra": "auto-install-extra",
    } # trans[setting]

    if setting is None:
        __click.echo(f"{__COLOR['red']}Invalid setting")
    else:
        __togg(trans[setting])
        out = __scfg(trans[setting])
        __click.echo(f"{__COLOR['red']}{out}")
    pass


@__click.command()
def version():
    """Check current version"""
    __click.echo(f"{__COLOR['green']}absfuyu: {__v.__version__}")



# Do group
##############################################################
@__click.command(name="gen-pass")
@__click.argument("size", type=int, default=8)
@__click.option(
    "--password_type", "-p",
    type=__click.Choice(["default","full"], case_sensitive=False),
    default="full", show_default=True,
    help="default: [a-zA-Z0-9] | full: [a-zA-Z0-9] + special char")
def gen_password(size, password_type):
    """Generate password of choice"""
    __click.echo(__randStr(
        size=size,
        char=password_type,
        string_type_if_1=True))


@__click.command()
@__click.option(
    "--force_update/--no-force-update","-F/-f", "force_update",
    type=bool, default=True,
    show_default=True,
    help="Update the package")
def update(force_update: bool):
    """Update the package to latest version"""
    __click.echo(__COLOR['green'])
    __v.check_for_update(force_update=force_update)


@__click.command()
def reset():
    """Reset config to default value"""
    __reset()
    __click.echo(f"{__COLOR['green']}All settings have been reseted")
    pass


@__click.command()
@__click.option(
    "--game_name", "-g",
    type=__click.Choice(
        ["random", "esc", "rps", "ttt"],
        case_sensitive=False
    ),
    default="random", show_default=True,
    help="Play game",)
@__click.option(
    "--size", "-s",
    type=int, default=3,
    show_default=True,
    help="Change game's size (if any)")
def game(game_name: str, size: int):
    """Play game. By default: random game"""
    from absfuyu.fun import game_escapeLoop, game_RockPaperScissors
    if game_name.startswith("random"):
        if __randc([0,1]) == 0:
            game_escapeLoop()
        else:
            game_RockPaperScissors()
    else:
        if game_name.startswith("esc"):
            game_escapeLoop()
        elif game_name.startswith("rps"):
            game_RockPaperScissors()
        elif game_name.startswith("ttt"):
            from absfuyu.extensions.extra.tictactoe import game_tictactoe
            game_tictactoe(size=size)


@__click.command()
@__click.argument("pkg",type=__click.Choice(__core.ModulePackage))
def install(pkg: str):
    """Install absfuyu's extension"""
    cmd = f"pip install -U absfuyu[{pkg}]".split()
    try:
        __run(cmd)
    except:
        try:
            cmd2 = f"python -m pip install -U absfuyu[{pkg}]".split()
            __run(cmd2)
        except:
            __click.echo(f"{__COLOR['red']}Unable to install absfuyu[{pkg}]")
        else:
            __click.echo(f"{__COLOR['green']}absfuyu[{pkg}] installed")
    else:
        __click.echo(f"{__COLOR['green']}absfuyu[{pkg}] installed")
    

@__click.command()
def advice():
    """Give some recommendation when bored"""
    from .fun import im_bored
    __click.echo(f"{__COLOR['green']}{im_bored()}")
    pass



@__click.group(name="do")
def do_group():
    """Perform functinalities"""
    pass
do_group.add_command(gen_password)
do_group.add_command(reset)
do_group.add_command(update)
do_group.add_command(game)
do_group.add_command(install)
do_group.add_command(advice)



# Main group init
##############################################################
@__click.group()
def main():
    """
    absfuyu's command line interface
    
    Usage:
        python -m absfuyu --help
        fuyu --help
    """
    pass
main.add_command(welcome)
main.add_command(greet)
main.add_command(toggle)
main.add_command(version)
main.add_command(do_group)


if __name__ == "__main__":
    if CLI_MODE:
        main()