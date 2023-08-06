import os
from typing import List, Tuple
from ODToolkit._utils import box_iou
import numpy as np


def get_fpfn(gt_lbl: List, 
             pred_lbl: List, 
             img_w: int,
             img_h: int,
             iou_thresh: float) -> Tuple:
        FP = []
        FN = []
        TP = []
        TN = 0
        pred_root = os.path.split(pred_lbl[0])[0]

        for i, _ in enumerate(gt_lbl):
            with open(gt_lbl[i], 'r') as f:
                gt_lines = f.readlines()
                gt_box = []
                for line in gt_lines:
                    cls, xc, yc, w, h = line.split(' ')

                    xc, yc, h, w = float(xc), float(yc), float(h), float(w)
                    xc, yc, h, w = int(img_w*xc), int(img_h*yc), int(img_h*h), int(img_w*w)

                    xc, yc, x2, y2 = xc-w//2, yc-h//2, xc+w//2, yc+h//2
                    gt_box.append([xc, yc, x2, y2])

            path, fname = os.path.split(gt_lbl[i])
            pred_file = pred_root+'/'+fname

            pred_box = []
            if pred_file in pred_lbl:
                with open(pred_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        cls, conf, xc, yc, w, h = line.split(' ')
                        xc, yc, h, w = float(xc), float(yc), float(h), float(w)
                        xc, yc, h, w = int(img_w*xc), int(img_h*yc), int(img_h*h), int(img_w*w)

                        xc, yc, x2, y2 = xc-w//2, yc-h//2, xc+w//2, yc+h//2
                        pred_box.append([xc, yc, x2, y2])

            # compare iou and find out fp and fn
            if pred_box == [] and gt_box != []:
                for gtb in gt_box:
                    FN.append(gtb)
                    xc, yc, x2, y2 = gtb

            elif gt_box == [] and pred_box != []:
                for pdb in pred_box:
                    FP.append(pdb)
            elif gt_box == [] and pred_box == []:
                TN += 1
            else:      
                for pdb in pred_box:
                    iou_fp = []
                    for gtb in gt_box:
                        iou_val = box_iou(np.array(pdb).reshape(1,4), np.array(gtb).reshape(1,4))
                        iou_fp.append(iou_val.item())
                    iou_fp = np.array(iou_fp)
                    if all(i < iou_thresh for i in iou_fp): # false positive
                        FP.append(pdb)
                    else:
                        # means there is a gt box satisfy the iou_thresh
                        TP.append(pdb)

                for gtb in gt_box:
                    iou_fn = []
                    for pdb in pred_box:
                        iou_val = box_iou(np.array(pdb).reshape(1,4), np.array(gtb).reshape(1,4))
                        iou_fn.append(iou_val.item())
                    iou_fn = np.array(iou_fn)
                    if all(i < iou_thresh for i in iou_fn): # false negative
                        xc, yc, x2, y2 = gtb
                        FN.append(gtb)
                        
        return FP, FN, TP, TN