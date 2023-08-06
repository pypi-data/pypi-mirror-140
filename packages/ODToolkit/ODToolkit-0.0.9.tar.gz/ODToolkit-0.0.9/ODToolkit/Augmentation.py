import os
import glob
from tqdm import tqdm_notebook as tqdm
import shutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import cv2
import numpy as np
from typing import Union


class Augmentation:
    def __init__(self):
        pass
    
    def _valid_x(self, x_target, x1, x2):
        '''
        x1-x2 represents width or height
        thus, for a valid x proposal, we just want to make sure there is no overlapping
        '''

        diff = x2-x1
        if (x_target+diff) < x1 or x_target > x2:
            return True
        else:
            return False
    
    
    def augment(self,
                train_img: str, 
                train_lbl: str, 
                savepath_img: str, 
                savepath_lbl: str, 
                R: int,
                mask_percentage:float,
                mask_top:bool,
                quit: int)-> Union[int, None]:
        
        image = np.array(Image.open(train_img))
        
        height, width, _ = image.shape
        margin = int(mask_percentage*height)

        with open(train_lbl, 'r') as f:
            lines = f.readlines()

        # ---step1: check boxes
        # 1. if no boxes, then directly return
        if lines == []:
            return -1

        # ---step2: store boxes into list
        # 2 things are done here: 1. write original boxes into new file, 2. store original boxes into list
        new_im = image.copy()
        existing_box = [] # put all boxes in to this list
        
        with open(savepath_lbl, 'w') as f:
            f.write('')

        for line in lines:
            with open(savepath_lbl, 'a') as f:
                f.write(line)

            cls, xc, yc, w, h = line.split(' ')

            xc, yc, h, w = float(xc), float(yc), float(h), float(w)
            xc, yc, h, w = int(width*xc), int(height*yc), int(height*h), int(width*w)
            
            # boundary check
            y1 = max(0, yc - h/2)
            x1 = max(0, xc - w/2)
            y2 = min(height, y1+h)
            x2 = min(width, x1+w)
            
            if y1 <= margin:
                continue
            
            existing_box.append([cls, x1, y1, x2, y2]) # x1y1x2y2

        # ---step 3: augmentation
        # existing_box is to select original boxes for augmentation
        # existing_box_new is to store new copy-pasted boxes and write into file
        existing_box_new = existing_box.copy()
        if len(existing_box) > 3: # if too many boxes, we don't copy-paste that much
            R = 1
        for _ in range(R):
            for box in existing_box:
                _, x1, y1, x2, y2 = box
                h, w = y2-y1, x2-x1

                valid = False
                val_cnt = 0 # check if while loop is a endless loop
                while not valid: # keep finding valid position to place the fake box
                    candidate_x = np.random.randint(0, width-w) if width-w!=0 else 0
                    # allow to copy-paste onto top p% region or not
                    if mask_top:
                        candidate_y = np.random.randint(margin, height-h) if height-h!=0 else 0
                    else:
                        candidate_y = np.random.randint(0, margin-h) if margin-h!=0 else 0
                        
                    if candidate_x == candidate_y == 0: # both are 0, no need to try anymore
                        break

                    res = [] # list used for checking if candidate x and y are valid or not
                    val_cnt+=1
                    if val_cnt > quit: # if bad-luck, we give up this box
                        break 

                    for boxn in existing_box_new:
                        cls, x1n, y1n, x2n, y2n = boxn
                        hn, wn = y2n-y1n, x2n-x1n

                        res.append(self._valid_x(candidate_x, x1n, x2n) or self._valid_x(candidate_y, y1n, y2n))
                        
                    # if both x and y candidate in list res gives True, we adopt this anchor for copy-paste augmentation
                    if np.all(np.array(res, dtype=bool)):
                        valid = True
                        with open(savepath_lbl, 'a') as f:
                            # cls, xc, yc, w, h
                            line = ' '.join([str(i) for i in [cls, (candidate_x+w/2)/width, (candidate_y+h/2)/height, w/width, h/height]])
                            f.write(line+'\n')


                if val_cnt <=quit: # if lucky, we move to new round, if not, we give up this box
                    patch = image[int(y1):int(y1+h), int(x1):int(x1+w), :]

                    if np.random.rand() < 0.5: # vertical random flip
                        patch = patch[::-1, :, :]
                    if np.random.rand() < 0.5: # horizontal random flip
                        patch = patch[:, ::-1, :]

                    new_im[int(candidate_y):int(candidate_y+h), int(candidate_x):int(candidate_x+w), :] = patch

                    # update existing_box_new in x1y1x2y2
                    existing_box_new.append([cls, candidate_x, candidate_y, candidate_x+w, candidate_y+h])

        image_ready = Image.fromarray(new_im)
        image_ready.save(savepath_img)
        
    def create_aug_dataset(self, 
                           train_img: str, 
                           train_lbl: str, 
                           savepath_img: str, 
                           savepath_lbl: str,
                           repeat: int,
                           R: int,
                           mask_percentage: float,
                           mask_top: bool,
                           quit: int):

        # create folders
        os.makedirs('{}'.format(savepath_img), exist_ok=True)
        os.makedirs('{}'.format(savepath_lbl), exist_ok=True)
        
        _, fname = os.path.split(train_img)
        name, ext = fname.split('.')
        cnt = 0
        while cnt<repeat:
            try:
                status = self.augment(train_img=train_img, 
                                      train_lbl=train_lbl, 
                                      savepath_img=savepath_img + '{}_{}.jpg'.format(name, cnt), 
                                      savepath_lbl=savepath_lbl + '{}_{}.txt'.format(name, cnt), 
                                      R=R,
                                      mask_percentage=mask_percentage,
                                      mask_top=mask_top,
                                      quit=quit)
                if status == -1: # no label or invalid for augmentation
                    invalid += 1
                    shutil.copy2(i, savepath_img + '{}.jpg'.format(name))
                    shutil.copy2(l, savepath_lbl + '{}.txt'.format(name))
                    break
                else:
                    cnt+=1
            except Exception as e:
                print('Error: ', e)
                break
