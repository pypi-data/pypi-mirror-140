import cv2
import numpy as np
import glob
from PIL import Image
from typing import List, Tuple, Union


def xy_to_homo(x:Union[float, int], 
               y:Union[float, int], 
               homo:np.array) -> Tuple:
    # homo in shape of [3,3]
    
    img_coord = np.array([x, y, 1])
    homo_coord = np.matmul(homo, img_coord)
    x_homo, y_homo, _ = homo_coord/homo_coord[2]
    
    return round(x_homo), round(y_homo)


def homo_to_xy(x_homo:Union[float, int],
               y_homo:Union[float, int], 
               homo:np.array) -> Tuple:
    # homo in shape of [3,3]
    
    homo_coord = np.array([x_homo, y_homo, 1])
    xy_coord = np.matmul(np.linalg.inv(homo), homo_coord)
    x, y, _ = xy_coord/xy_coord[2]
    
    return round(x), round(y)
