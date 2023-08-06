from typing import Dict as __Dict
from typing import List as __List

# json
__all_lib = {
    "native": [
        "os","random","string","subprocess","typing","hashlib",
        "datetime","json","sys","math","base64","codecs",
        "zlib","inspect","functools","tracemalloc", "re",
        "collections", "urllib", "time",
    ],
    "external": [
        "rich","click","colorama","requests","numpy","pandas",
        "matplotlib","LunarCalendar",
    ],
    "dev-only": [
        "twine", "virtualenv", "setuptools", "wheel",
        "autoimport", "black", "pytest", "tox", "build",
    ],
    "unused": [
        "sortedcontainers", "tomli",
    ],
    "future": [
        "scikit-learn", "opencv-python",
    ],
}

LibraryDict = __Dict[str,__List[str]]

def show_lib_from_json(
        lib_dict: LibraryDict,
        hidden: bool = False,
        to_json: bool = True
    ) -> str:
    """
    Show libraries
    
    lib_dict: a dict that converted from jso
    hidden: import as __[lib name]
    to_json: save as json format
    """

    catergory = [x for x in lib_dict.keys()] # get keys
    libs = [x for x in lib_dict.values()] # get values

    lib_import = [] # New list
    for lib_list in libs: # Take each lib list in a list of lib list
        temp = []
        for item in sorted(list(set(lib_list))):
            if hidden:
                hidden_text = f" as __{item}"
            else:
                hidden_text = ""
            temp.append(f"import {item}{hidden_text}")
        lib_import.append(temp)

    new_lib = dict(zip(catergory, lib_import))

    if to_json:
        import json
        return str(json.dumps(new_lib, indent=4))
    else:
        out_text = ""
        for idx, val in enumerate(catergory):
            out_text += f"# {val} libs\n"
            for x in lib_import[idx]:
                out_text += x+"\n"
            out_text += "\n"
        return out_text