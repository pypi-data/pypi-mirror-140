"""
absfuyu's current version
-------------------------
"""

# Module level
##############################################################
__all__ = [
    "__version__",
    "check_for_update",
]



# Library
##############################################################
import json as __json
import subprocess as __subprocess
# from typing import Dict as __Dict
from typing import Optional as __Optional
# from typing import Union as __Union
from urllib.error import URLError as __URLError
from urllib.request import Request as __Request
from urllib.request import urlopen as __urlopen

from . import config as __config


# Function
##############################################################
#__ABSFUYU_RSS = "https://pypi.org/rss/project/absfuyu/releases.xml"

def __get_latest_version_legacy(package_name: str = "absfuyu"):
    """
    Load data from PyPI's RSS -- OLD
    """
    rss = f"https://pypi.org/rss/project/{package_name}/releases.xml"
    req = __Request(rss)
    try:
        response = __urlopen(req)
    except __URLError as e:
        if hasattr(e, "reason"):
            print("Failed to reach server.")
            print("Reason: ", e.reason)
        elif hasattr(e, "code"):
            print("The server couldn\'t fulfill the request.")
            print("Error code: ", e.code)
    else:
        xml_file = response.read().decode()
        ver = xml_file[xml_file.find("<item>"):xml_file.find("</item>")]
        version = ver[ver.find("<title>")+len("<title>"):ver.find("</title>")]
        return version

def __load_data_from_json_api(api: str):
    """
    Load data from api then convert to json
    """
    req = __Request(api)
    try:
        response = __urlopen(req)
    except __URLError as e:
        if hasattr(e, "reason"):
            print("Failed to reach server.")
            print("Reason: ", e.reason)
        elif hasattr(e, "code"):
            print("The server couldn't fulfill the request.")
            print("Error code: ", e.code)
    else:
        json_file = response.read().decode()
        return __json.loads(json_file)

def __get_latest_version(package_name: str = "absfuyu"):
    """
    Get latest version from PyPI's API
    """
    api = f"https://pypi.org/pypi/{package_name}/json"
    ver = __load_data_from_json_api(api)
    return ver["info"]["version"]

def __get_update(
        package_name: str = "absfuyu",
        version: __Optional[str] = None
    ):
    """
    Run pip upgrade command
    """
    # python -m pip install -U {package_name}
    if version is None:
        cmd = f"pip install -U {package_name}".split()
    else:
        cmd = f"pip install -U {package_name}=={version}".split()
    # return __subprocess.run(cmd)
    try:
        return __subprocess.run(cmd)
    except:
        cmd = f"python -m pip install -U {package_name}=={version}"
        return __subprocess.run(cmd)

def check_for_update(
        package_name: str = "absfuyu",
        force_update: bool = False,
    ):
    """
    Check for latest update
    """
    
    latest: str = ""
    try:
        latest = __get_latest_version(package_name)
    except:
        latest = __get_latest_version_legacy(package_name)
    current = __version__
    
    if current == latest:
        print(f"You are using the latest version ({latest})")
    else:
        if force_update:
            print(f"Newer version ({latest}) available. Upgrading...")
            try:
                __get_update(package_name, version=latest)
            except:
                print(f"""
                Unable to perform update.
                Please update manually with:
                pip install -U {package_name}=={latest}
                """)
        else:
            print(f"Newer version ({latest}) available. Upgrade with:\npip install -U {package_name}=={latest}")
    return f"latest: {latest}\ncurrent: {current}"

#######

def __get_ver_from_config(string_mode: bool = False):
    """Get current version"""
    cfg = __config.__load_cfg()
    ver: dict = cfg["version"]
    if string_mode:
        ver_str = f"{ver['major']}.{ver['minor']}.{ver['patch']}"
        if ver["release_level"] == "final":
            return ver_str
        else:
            return f"{ver_str}{ver['release_level']}{ver['serial']}"
        # return ".".join([str(x) for x in ver.values()])
    else:
        return ver

def __bump_version(option: str = "patch", channel: str = "final"):
    """bump version"""
    
    # Bump ver option
    bump_option = ["major", "minor", "patch"]
    release_level_option = [
        "final",
        "rc", # release candidate
        "dev",
    ]

    # Check conditions - use default values if fail
    if option not in bump_option:
        option = "patch"
    if channel not in release_level_option:
        channel = "final"
    
    # Bump ver and save
    cfg = __config.__load_cfg()
    if channel.startswith("final"): # Final version
        if cfg["version"]["release_level"] in ["rc", "dev"]:
            cfg["version"]["release_level"] = "final"
            cfg["version"]["serial"] = 0
        else:
            if option.startswith("major"):
                cfg["version"][option] += 1
                cfg["version"]["minor"] = 0
                cfg["version"]["patch"] = 0
            elif option.startswith("minor"):
                cfg["version"][option] += 1
                cfg["version"]["patch"] = 0
            else:
                cfg["version"][option] += 1
        # cfg["version"]["release_level"] = "final"
        # cfg["version"]["serial"] = 0
    
    elif channel.startswith("rc"): # release candidate version
        if cfg["version"]["release_level"] == "dev":
            cfg["version"]["release_level"] = "rc"
            cfg["version"]["serial"] = 0
        elif channel==cfg["version"]["release_level"]:
            cfg["version"]["serial"] += 1
        else:
            cfg["version"]["release_level"] = channel
            cfg["version"]["serial"] = 0

            if option.startswith("major"):
                cfg["version"][option] += 1
                cfg["version"]["minor"] = 0
                cfg["version"]["patch"] = 0
            elif option.startswith("minor"):
                cfg["version"][option] += 1
                cfg["version"]["patch"] = 0
            else:
                cfg["version"][option] += 1
    
    else: # dev version
        if channel==cfg["version"]["release_level"]:
            cfg["version"]["serial"] += 1
        else:
            cfg["version"]["release_level"] = channel
            cfg["version"]["serial"] = 0

            if option.startswith("major"):
                cfg["version"][option] += 1
                cfg["version"]["minor"] = 0
                cfg["version"]["patch"] = 0
            elif option.startswith("minor"):
                cfg["version"][option] += 1
                cfg["version"]["patch"] = 0
            else:
                cfg["version"][option] += 1
        
    # Save
    __config.__save_cfg(cfg)

    # Get current ver
    global __version__
    __version__ = __get_ver_from_config(string_mode=True)


def __release_to_pypi(
        option: str = "patch",
        channel: str = "final",
        safety_lock_off: bool = False,
        debug: bool = False,
    ):
    """
    Not intended for end-user
    
    Developer only!
    """

    if safety_lock_off:

        if debug:
            print("Bumping version...")
        
        try:
            __bump_version(option=option, channel=channel)
        except:
            return None

        if debug:
            print(f"Version bumped. Current verion: {__version__}")
            print("Initialize building package")
        
        cmd1 = "python -m build".split()
        cmd2 = "twine upload dist/*".split()
        try:
            __subprocess.run(cmd1)
            try:
                __subprocess.run(cmd2)
                if debug:
                    print("Release published!")
            except:
                return None
        except:
            return None
        else:
            return None
    else:
        return None



# Get version
##############################################################
__version__ = __get_ver_from_config(string_mode=True)