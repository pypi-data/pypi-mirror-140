import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
import shutil
from tqdm import tqdm_notebook as tqdm


class DataCleaning:
    def __init__(self, 
                 img_w:int, 
                 img_h:int):
        self.img_w = img_w
        self.img_h = img_h
        self.area = img_w*img_h
    
    def clean(self, 
              lbl_file:str,
              lbl_savepath:str,
              area_threshold:float):
        
        area_threshold *= self.area

        # readlines and filter out small boxes
        with open(lbl_file, 'r') as f:
            lines = f.readlines()

        # rewrite to new dir based on the box area filtering
        with open(lbl_savepath,'a') as f:
            for line in lines:
                cls, xc, yc, w, h = line.split(' ')
                width, height = int(float(w)*self.img_w), int(float(h)*self.img_h)
                # remove small boxes
                if (width*height) > area_threshold:
                    f.write(line)
