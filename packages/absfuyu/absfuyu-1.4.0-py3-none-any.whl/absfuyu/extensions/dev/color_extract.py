# -*- coding: utf-8 -*-
"""
Extract color in picture and return in hex form
"""

# Modified from: https://www.alessandroai.com/extract-and-analyze-colors-from-any-image/


# Module level
##############################################################
__all__ = [
    "extract_color",
]




# Library
##############################################################
IS_LOADED: bool = False
from collections import Counter as __Counter
try:
    from sklearn.cluster import KMeans as __KMeans
    import cv2 as __cv2
except ImportError as err:
    from absfuyu.config import show_cfg as __aie
    if __aie("auto-install-extra", raw=True):
        from subprocess import run as __run
        __cmd = [
            "python -m pip install --upgrade pip".split(),
            "python -m pip install scikit-learn".split(),
            "python -m pip install opencv-python".split(),
        ]
        for x in __cmd:
            __run(x)
    else:
        raise SystemExit(err)
else:
    IS_LOADED = True



# Function
##############################################################
def __rgb_to_hex(rgb_color):
    """Convert RGB to HEX"""
    hex_color = "#"
    for i in rgb_color:
        hex_color += ("{:02x}".format(int(i)))
    return hex_color

def __preprocess(raw):
    if IS_LOADED:
        image = __cv2.resize(raw, (900, 600), interpolation = __cv2.INTER_AREA)
        image = image.reshape(image.shape[0]*image.shape[1], 3)
        return image

def __analyze(img, color_num: int = 3):
    """Analyze 'color_num' number of color in an image"""
    if IS_LOADED:
        clf = __KMeans(n_clusters = color_num)
        color_labels = clf.fit_predict(img)
        center_colors = clf.cluster_centers_
        counts = __Counter(color_labels)
        ordered_colors = [center_colors[i] for i in counts.keys()]
        hex_colors = [__rgb_to_hex(ordered_colors[i]) for i in counts.keys()]
        return hex_colors

def extract_color(image, color_num: int = 5):
    """
    Return a color list in picture
    
    image:
        Image file

    color_num: int
        Number of color want to extract
    """
    if IS_LOADED:
        img = __cv2.imread(image)
        img = __cv2.cvtColor(img, __cv2.COLOR_BGR2RGB)
        modified_image = __preprocess(img)
        hex_color = __analyze(modified_image, color_num)
        return hex_color
    else:
        raise SystemExit("Unexpected error")