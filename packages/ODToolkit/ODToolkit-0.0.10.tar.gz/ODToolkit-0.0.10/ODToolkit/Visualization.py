import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
from typing import List, Tuple
import os
from ODToolkit.Analysis import get_fpfn


class BoxVisualizer:
    def __init__(self, 
                 img_h:int, 
                 img_w:int) -> None:
        self.h = img_h
        self.w = img_w
        self.area = self.h*self.w

    def show_boxes(self, 
                  labels: List[List], 
                  mode: List[str])->None:

        assert len(labels) == len(mode), "labels and mode need to have same length, but got {} and {}".format(len(labels),
                                                                                                              len(mode))
        plt.figure(figsize=[5*len(mode), 20])
        for idx, (data, name) in enumerate((zip(labels, mode))):
            area = []
            height, width = [], []
            aspect_ratio = []

            plt.subplot(4,len(labels),2*len(labels)+idx+1) # plot out the boxes
            plt.ylim(0,self.h)
            plt.xlim(0,self.w)

            # heatmap
            heat = np.zeros((self.h, self.w))

            for file in data:
                with open(file,'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        cls, xc, yc, w, h = line.split(' ')
                        xc, yc, h, w = float(xc), 1-float(yc), float(h), float(w) # 1-y because coordinate of y reverts
                        area.append(h*w*self.area)
                        height.append(h)
                        width.append(w)
                        aspect_ratio.append(h/w)

                        xc, yc, h, w = int(self.w*xc), int(self.h*yc), int(self.h*h), int(self.w*w)
                        rect = patches.Rectangle((xc-w//2, yc-h//2), 
                                                 width=w, height=h, 
                                                 linewidth=1, edgecolor='r', facecolor='none')
                        plt.gca().add_patch(rect)

                        # heatmap
                        heat[int(1-yc-h/2):int(1-yc+h/2), int(xc-w/2):int(xc+w/2)] += 1.

            plt.title('{}: box actual position'.format(name))

            area = np.array(area)
            msg = '{}: max area: {}, min area: {}, avg area: {}'.format(name, area.max(), area.min(), area.mean())
            plt.subplot(4,len(labels),idx+1)
            plt.hist(area, bins=100)
            plt.title('{}: histogram for box area'.format(name))

            plt.subplot(4,len(labels),1*len(labels)+idx+1)
            plt.scatter(width, height)
            plt.title('{}: width-height scatter plot'.format(name))

            plt.subplot(4,len(labels),3*len(labels)+idx+1)
            plt.imshow(heat)
            plt.title('{}: heatmap of boxes'.format(name))

            print('{}: max aspect_ratio:{}, min aspect_ratio:{}'.format(name, max(aspect_ratio), min(aspect_ratio)))
            
    def show_fpfn(self, 
                  FP:List, 
                  FN:List, 
                  TP:List,
                  TN:int,
                  scene: str,
                  figsize=[15,20]):

        def read_box(box:List, color:str) -> List:
            temp = []
            # heatmap
            heat = np.zeros((self.h, self.w))
            for box in box:
                x1, y1, x2, y2 = box
                w, h = x2-x1, y2-y1
                rect = patches.Rectangle((x1, y1), 
                                         width=w, height=h,
                                         linewidth=1, edgecolor=color, facecolor='none')
                temp.append(y1)
                heat[int(y1):int(y2), int(x1):int(x2)] += 1.
                plt.gca().add_patch(rect)
            return temp, heat
        
        # confusion matrix
        x = ["Garbage_GT","BG_GT"]
        y = ["Garbage_Pred", "BG_Pred"]

        result = np.array([len(TP), len(FP), len(FN), TN]).reshape(2,2)
        
        plt.figure(figsize=[20,15])
        plt.suptitle("Evaluation for {}".format(scene), fontsize=22)
        plt.subplot(3,4,1)
        plt.imshow(result)
        plt.title('confusion matrix')

        # Show all ticks and label them with the respective list entries
        plt.xticks(np.arange(len(x)), labels=x, fontsize=12)
        plt.yticks(np.arange(len(y)), labels=y, fontsize=12)

        for i in range(len(x)):
            for j in range(len(y)):
                text = plt.gca().text(j, i, result[i, j],
                               ha="center", va="center", color="r", fontsize=16)

        
        # spacial distribution
        plt.subplot(3,4,2)
        plt.imshow(np.ones((self.h,self.w,3)))
        fpy, heat_fpy = read_box(FP, 'red')
        plt.title('FP boxes')

        plt.subplot(3,4,3)
        plt.imshow(np.ones((self.h,self.w,3)))
        fny, heat_fny = read_box(FN, 'blue')
        plt.title('FN boxes')

        plt.subplot(3,4,4)
        plt.imshow(np.ones((self.h,self.w,3)))
        cy, heat_cy = read_box(TP, 'green')
        plt.title('TP boxes')
        
        # haetmap
        plt.subplot(3,4,6)
        plt.imshow(heat_fpy)
        plt.title('heatmap of FP')

        plt.subplot(3,4,7)
        plt.imshow(heat_fny)
        plt.title('heatmap of FN')

        plt.subplot(3,4,8)
        plt.imshow(heat_cy)
        plt.title('heatmap of TP')
        
        # y histogram
        plt.subplot(3,4,10)
        plt.hist(fpy, bins=100, orientation='horizontal')
        plt.ylim(0, self.h)
        plt.gca().invert_yaxis()
        plt.title('histogram of FP')

        plt.subplot(3,4,11)
        plt.hist(fny,bins=100, orientation='horizontal')
        plt.ylim(0, self.h)
        plt.gca().invert_yaxis()
        plt.title('histogram of FN')

        plt.subplot(3,4,12)
        plt.hist(cy,bins=100, orientation='horizontal')
        plt.ylim(0, self.h)
        plt.gca().invert_yaxis()
        plt.title('histogram of TP')