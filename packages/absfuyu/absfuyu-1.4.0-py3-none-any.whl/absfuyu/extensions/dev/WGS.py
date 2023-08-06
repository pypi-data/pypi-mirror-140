# -*- coding: utf-8 -*-
"""
Print out my favourite weapon: Wolf's Gravestone
"""


# Library
##############################################################
import re as __re

try:
    import colorama as __colorama
except ImportError:
    # Auto install absfuyu[cli]
    from absfuyu.config import show_cfg as __aie
    if __aie("auto-install-extra", raw=True):
        from subprocess import run as __run
        __cmd: str = "python -m pip install -U absfuyu[cli]".split()
        __run(__cmd)
    else:
        raise SystemExit("This feature is in absfuyu[cli] package")



# Function
##############################################################
def wgs_old(size: str = "big"):
    """
    Return Wolf's Gravestone
    
    size: "big" | "small"
    """

    sizes = ["big", "small"]
    if size not in sizes:
        size = "big"
    
    WGS = r"""
                                                                                            
                                                                                ..:=+:        
                                                                            =*****.        
                                                                            .=*#*++        
                                                                            -#+%+ :.        
                                                                            -##%+.           
                                                                        .*#%*.             
                                                                        :##%=               
                                                                        =###:                
                                                                        +#%+                  
                                                                    -###-                   
                                                            =+    =%##.                    
                                                :##%+..--=- :##*=*#%%=                      
                                                #%%%%#%##%%%%%%###%%:                      
                                                    :=%%@%####%#%%%%%%=--:                   
                                                    .%*:%%#%%%##%%%%%%*=                    
                                                    :##=++#%##+*%%#%%*:                     
                                                    :=**####%#%#%%%%%%%#+                    
                                                    .=+**#%%%###%##%%%%%%+                    
                                                    *%###%####@#%#+=-#@%%#+=-                 
                                                :+*#%@%%##%%%#%#%#**.:+%%##.                
                                                -*##%%@%%%%%%#%-.+=     :+--.                
                                                -*##%@@%#%@@%#%@+                             
                                            .-#%%%@%%@@#%%#*.                              
                                            .=##%%%%%%%%#%%=.                               
                                            .-*#%%%%%%@%%%#*-                                 
                                        .:*%%%%%%%%%%#*+.                                  
                                        :*#%%%%%%%%%#=:                                    
                                        . -######%%%%%#-                                      
                                        =####%##%%#=*.                                       
                                    :+######%%%*--.                                        
                                    .-*####%#%%%*-:.                                         
                                    =++****##**=-.                                           
                                .-+***+**###*=:                                             
                                -++++*##+*#*=.                                              
                            .:+**#####%#*=-                                                
                            . :+*########*=:                                                 
                            . =+*#*+#####+-                                                   
                        . .=**#*-*###*=-                                                    
                        :+**#+=*###*=:                                                     
                        -+***-=**+*+=.                                                      
                        .=+**+-*#***+-.                                                       
                    .:-=+**-=##**+=:                                                         
                    :-=++**-+#***+-                                                           
                    :=+++  :***+=:                                                            
                :=+**--=***+=:                                                             
                -=+**-++++=:.                                                               
                :==+*+:==:.                                                                   
            :=++*-                                                                         
            .-=++-.                                                                          
        .:=-:.                                                                             
        .::.                                                                                 
                                                                                            
    """

    WGS_SMALL = r"""
                                    
                                        ::    
                                        .**+    
                                        .*#..    
                                    :#+       
                                    =#:        
                                ..  **          
                        =%+=++##*#*           
                            +*%#%#%%#=          
                            +**###%%%=          
                            +##%###**%#:         
                        .+#%%%%%+*: -*-        
                        =#%%%%%+.              
                        .=#%%%%#=                
                    .*%%%%%+.                 
                    .*#%%%#-                   
                    -###%#=.                    
                .=***#*:                      
                :+*##*+.                       
                -**###-                         
            .=*+*#*:                          
            :+*+**=.                           
            .-+++**-                             
        .=*--*+:                              
        .=+==-.                                
        :+=                                     
    .:.                                       

    """

    pics = [WGS, WGS_SMALL]
    out = dict(zip(sizes, pics))

    return out[size]


def str_to_pixel(px_str: str, px_size: int = 2, line_break: bool = True):
    """
    Convert string into colored pixel

    pixel_string format:
        <number_of_pixel><color_code>
    
    Example:
        50w20b = 50 white pixels and 20 black pixels
    """

    # Type check
    if isinstance(px_str, list):
        px_str = "1N".join(px_str)
    elif not isinstance(px_str, str):
        raise ValueError("Must be a string")
    else:
        pass
    
    # Pixel character - Unicode character
    if px_size < 1:
        px_size = 2
    PIXEL = u"\u2588"*px_size

    # Translation to color
    translate = {
        "w": __colorama.Fore.WHITE,
        "b": __colorama.Fore.BLACK,
        "B": __colorama.Fore.BLUE,
        "g": __colorama.Fore.LIGHTBLACK_EX, # Gray
        "G": __colorama.Fore.GREEN,
        "r": __colorama.Fore.LIGHTRED_EX,
        "R": __colorama.Fore.RED, # Dark red
        "m": __colorama.Fore.MAGENTA,
        "y": __colorama.Fore.YELLOW,
        "N": "\n", # New line
        "E": __colorama.Fore.RESET
    }
    
    # Extract
    num = __re.split("[a-zA-Z]", px_str)
    char = __re.split("[0-9]", px_str)

    # Clean
    for x in num[:]:
        if x == "":
            num.remove(x)
    for i in range(len(num)):
        num[i] = int(num[i])
    for x in char[:]:
        if x == "":
            char.remove(x)

    # Pixel string
    px = []
    for i in range(len(num)):
        px.append(num[i])
        px.append(char[i])

    # OUTPUT
    out = ""
    for i in range(len(px)):
        if isinstance(px[i], str):
            temp = PIXEL*px[i-1]
            out += f"{translate[px[i]]}{temp}{translate['E']}"
    
    if line_break:
        return out+"\n"
    else:
        return out


def wgs(size: int = 2):
    """
    Draw Wolf's Gravestone in command-line interface

    Art Credit: https://www.reddit.com/r/PixelArt/comments/n6xyrb/wolfs_gravestone_genshin_impact/
    """

    # Data of each line in pixel art
    pixel_art_wgs = [
        "51w", "46w3b1w", "43w2b1w1b1R1b1w", "43w1b1R1b1R2b1w",
        "43w2b1r1b3w", "41w3b1r1b1r1b2w", "28w3b10w1b1g5b2w",
        "28w1b1r1b9w1b3g1b5w", "28w2b1R1b1w2b4w1b3g2b5w",
        "30w1b1m1b1g1b1w1b1w1b3g1b7w", "30w3b2g3b3g1b8w",
        "29w1b2g1b5g1b1g1b9w", "29w1b1g2b1g4b1g1b10w",
        "29w1b3g2b1R2b1g2b9w", "27w7b3r1b1g1b10w",
        "27w1b5g1b1r1w2b2g2b8w", "26w2b3g6b4g1b8w",
        "26w1b2g2b2R1b1g1b1g4b9w", "25w1b2g1b2R2r1b1g1b1g1b1g1b1m1b8w",
        "24w1b1w1m1g1b3r1b2g1b3g2b1R2b6w",
        "21w3b2w1m1b3r1w1b2g4b2w1b1r1b6w",
        "21w1b2w3m1b1r1w2b3g1b5w3b6w", "21w1b1w3m1b1r2b3g3b14w",
        "20w1b1w2R1m1b1r1b3m1g2b16w", "19w1b1w3R1b1r1b2m2w1b18w",
        "18w1b1w3R1b1r1b3m1w1b19w", "17w1b1r3R1b1w1b2R1m1w1b20w",
        "16w1b1w1R1r1R1b1r1b3R2w1b20w", "15w1b1w1r1R1y1R2b3R1w3b20w",
        "14w1b3r1y1R2r4y1b23w", "13w1b1w3r4y2R1w1b24w",
        "12w1b1w2r2R3r1R2y1b25w", "10w2b1w2r1R2b1R3r1w1b26w",
        "9w1b2w2r1R1b1w1b1R2r1w1b27w", "9w1b1w2r1R1b1w1b1R2r1y1b28w",
        "8w1b1w1r2R1b1w1b2r1y1w1b29w", "7w1b1w1r1R2b1w1b4y1b30w",
        "6w1b1w1r1R1b2w1b1R2r1w1b31w", "5w1b1w2r1R1b2w1b1R1r2w1b31w",
        "4w1b1w2r1R1b1w2b2r1w2b32w", "3w1b1w1r1y1R1b1w1b3y1w1b34w",
        "2w1b1w1r2y1b1w6b35w", "1w6b43w", "50w"
    ]

    # Join data
    out = "1N".join(pixel_art_wgs)
    out = out.replace("y", "r") # Convert yellow into red
    out = out.replace("m", "R") # Convert magenta into dark red
    
    # Output
    return str_to_pixel(out, px_size=size)


def wgs_slow(duration: int = 1, size: int = 2):
    """
    Slower version because why not
    """

    from time import sleep

    new_wgs = [
        '50w', '46w3b1w', '43w2b1w1b1R1b1w', '43w1b1R1b1R2b1w',
        '43w2b1r1b3w', '41w3b1r1b1r1b2w', '28w3b10w1b1g5b2w',
        '28w1b1r1b9w1b3g1b5w', '28w2b1R1b1w2b4w1b3g2b5w',
        '30w1b1R1b1g1b1w1b1w1b3g1b7w', '30w3b2g3b3g1b8w',
        '29w1b2g1b5g1b1g1b9w', '29w1b1g2b1g4b1g1b10w',
        '29w1b3g2b1R2b1g2b9w', '27w7b3r1b1g1b10w', '27w1b5g1b1r1w2b2g2b8w',
        '26w2b3g6b4g1b8w', '26w1b2g2b2R1b1g1b1g4b9w',
        '25w1b2g1b2R2r1b1g1b1g1b1g1b1R1b8w', '24w1b1w1R1g1b3r1b2g1b3g2b1R2b6w',
        '21w3b2w1R1b3r1w1b2g4b2w1b1r1b6w', '21w1b2w3R1b1r1w2b3g1b5w3b6w',
        '21w1b1w3R1b1r2b3g3b14w', '20w1b1w2R1R1b1r1b3R1g2b16w',
        '19w1b1w3R1b1r1b2R2w1b18w', '18w1b1w3R1b1r1b3R1w1b19w',
        '17w1b1r3R1b1w1b2R1R1w1b20w', '16w1b1w1R1r1R1b1r1b3R2w1b20w',
        '15w1b1w1r1R1r1R2b3R1w3b20w', '14w1b3r1r1R2r4r1b23w', '13w1b1w3r4r2R1w1b24w',
        '12w1b1w2r2R3r1R2r1b25w', '10w2b1w2r1R2b1R3r1w1b26w',
        '9w1b2w2r1R1b1w1b1R2r1w1b27w', '9w1b1w2r1R1b1w1b1R2r1r1b28w',
        '8w1b1w1r2R1b1w1b2r1r1w1b29w', '7w1b1w1r1R2b1w1b4r1b30w',
        '6w1b1w1r1R1b2w1b1R2r1w1b31w', '5w1b1w2r1R1b2w1b1R1r2w1b31w',
        '4w1b1w2r1R1b1w2b2r1w2b32w', '3w1b1w1r1r1R1b1w1b3r1w1b34w',
        '2w1b1w1r2r1b1w6b35w', '1w6b43w', '50w'
    ]

    for x in new_wgs:
        sleep(duration/len(new_wgs))
        print(str_to_pixel(x, px_size=size), end="")

    pass