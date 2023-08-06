import os
import glob
from tqdm import tqdm_notebook as tqdm
import shutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import ipywidgets
from ipywidgets import interact
import cv2
import numpy as np
import ipywidgets as widgets
from typing import List


class DatasetMaker:
    def __init__(self, img_path, lbl_path, img_type='*.jpg', lbl_type='*.txt'):
        self.img_path = img_path
        self.lbl_path = lbl_path
        self.img_type = img_type
        self.lbl_type = lbl_type
        
        self.scene = dict()
        self.img = []
        self.lbl = []
        self.boxes = []
        self.data_pair = dict()
        self.aug_train_img = [] # for augmentation later
        self.aug_train_lbl = [] # for augmentation later
        print("image path: {}\nlabel path: {}\nimage type: {}\nlabel type: {}\n".format(self.img_path,
                                                                                        self.lbl_path,
                                                                                        self.img_type,
                                                                                        self.lbl_type))
    def _reset(self):
        self.scene = dict()
        self.img = []
        self.lbl = []
        self.boxes = []
        self.data_pair = dict()
    
    # allow the user to change dataset folder and make it into train/test split
    def make_another(self, img_path, lbl_path, img_type='*.jpg', lbl_type='*.txt'):
        self.img_path = img_path
        self.lbl_path = lbl_path
        self.img_type = img_type
        self.lbl_type = lbl_type
        
        self._reset()
        print("image path: {}\nlabel path: {}\nimage type: {}\nlabel type: {}\n".format(self.img_path,
                                                                                        self.lbl_path,
                                                                                        self.img_type,
                                                                                        self.lbl_type))
    def check_data(self) -> None:
                
        imgs = self.img_path + self.img_type
        lbls = self.lbl_path + self.lbl_type
        
        self.img = sorted(glob.glob(imgs))
        self.lbl = sorted(glob.glob(lbls))
        
        print('images:', len(self.img))
        print('labels:', len(self.lbl))

        scene = dict()

        for i in self.img:
            _, fname = os.path.split(i)
            s = fname[:10]
            if not s in scene:
                scene[s] = 1
            else:
                scene[s] += 1

        name = []
        for k, v in scene.items():
            name.append(k)
        name = sorted(name)

        for n in name:
            print(n, '---', scene[n])

        # check labels
        lbls = {'not_labeled':0, 'labeled':0}
        for l in self.lbl:
            with open(l, 'r') as f:
                lines = f.readlines()
            if len(lines) == 0:
                lbls['not_labeled'] += 1 
            else:
                lbls['labeled'] += 1 
        print(lbls)
    
    def get_scenes(self):
        
        print('tick the data for testing, the rest will be training')
        print('total images:{}'.format(len(self.img)))
        print('total labels:{}'.format(len(self.lbl)))

        for i in self.img:
            _, fname = os.path.split(i)
            s = fname[:10]
            if not s in self.scene:
                self.scene[s] = 1
            else:
                self.scene[s] += 1

        name = []
        for k, v in self.scene.items():
            name.append(k)
        name = sorted(name)
        
        #print('\nscenes:        num:')
        for n in name:
            msg = '{} --- {}'.format(n, self.scene[n])
            # for sure there will be only 1 k-v pair
            self.data_pair[msg] = widgets.Checkbox(False, description=msg)
        
        for _, b in self.data_pair.items():
            display(b)
            
    def get_box_info(self):
        for _, b in self.data_pair.items():
            print(b.value)

            
    def split_train_test(self, 
                         img_train='./images/train/', 
                         img_test='./images/test/', 
                         lbl_train='./labels/train/', 
                         lbl_test='./labels/test/'):
        test_split = []
        for k, b in self.data_pair.items():
            if b.value: # if the box is checked, it is a test set
                test_split.append(k.split(' --- ')[0])

        # make dirs
        os.makedirs(img_train, exist_ok=True)
        os.makedirs(img_test, exist_ok=True)

        os.makedirs(lbl_train, exist_ok=True)
        os.makedirs(lbl_test, exist_ok=True)
        
        print('{} will be test datasets, the rest are all training data'.format(test_split))
        
        # move to target folder
        print('moving images to target folders')
        for i in tqdm(self.img):
            _, fname = os.path.split(i)
            if fname[:10] in test_split:
                dst = img_test+fname
                shutil.copy2(i, dst)
            else:
                dst = img_train+fname
                shutil.copy2(i, dst)
        
        print('moving labels to target folders')
        for i in tqdm(self.lbl):
            _, fname = os.path.split(i)
            if fname[:10] in test_split:
                dst = lbl_test+fname
                shutil.copy2(i, dst)
            else:
                dst = lbl_train+fname
                shutil.copy2(i, dst)

        print('training image length: ', len(glob.glob(img_train + '*')))
        print('testing image length: ', len(glob.glob(img_test + '*')))
        
        print('training label length: ', len(glob.glob(lbl_train + '*')))
        print('testing label length: ', len(glob.glob(lbl_test + '*')))
        
        # store the list
        self.aug_train_img = sorted(glob.glob(img_train + '*'))
        self.aug_train_lbl = sorted(glob.glob(lbl_train + '*'))
        
    def _plot(self, img, lbl, idx, **kwargs):
        homograph = kwargs['homograph']
        verbose = kwargs['verbose']
        homo = kwargs['homo']
        
        with open(lbl[idx], 'r') as f:
                lines = f.readlines()

        # show image and draw box
        image = Image.open(img[idx])
        img_w,img_h = image.size
        if verbose:
            print(lbl[idx])
            print(img_w, img_h)

        plt.imshow(image)

        for line in lines:

            cls, x1, y1, w, h = line.split(' ')

            x1, y1, h, w = float(x1), float(y1), float(h), float(w)
            x1, y1, h, w = int(img_w*x1), int(img_h*y1), int(img_h*h), int(img_w*w)

            rect = patches.Rectangle((x1-w//2, y1-h//2), 
                                     width=w, height=h, 
                                     linewidth=1, edgecolor='r', facecolor='none')
            plt.gca().add_patch(rect)
            if verbose:
                print(line)
                print('box area: {} pixel, {:.2f}% of total area'.format(h*w, h*w/(img_w*img_h)*100))

        plt.title('Image')
        plt.axis('off')

        if homograph:
            assert homo is not None, "homography matrix is not provided"
            im_dst = cv2.warpPerspective(np.array(image), homo, [700, 700])
            plt.figure(figsize=[20,20])
            plt.imshow(im_dst)
        
        
    def visualize(self, **kwargs):
        n = len(self.img)
        plt.figure(figsize=[20,20])

        def view_image(i):
            self._plot(img=self.img, lbl=self.lbl, idx=i, **kwargs)
        interact(view_image, i=(0,n-1))
    
    
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
    
    
    def _augmentation(self,
                      train_img, train_lbl, savepath_img, savepath_lbl, **kwargs):
        area_threshold = kwargs['area_threshold']
        width = kwargs['width']
        height = kwargs['height']
        R=kwargs['R']
        mask_percentage = kwargs['mask_percentage']
        mask_top= kwargs['mask_top']
        quit =kwargs['quit']
        
        THRESHOLD_AREA = int(area_threshold*width*height)
        margin = int(mask_percentage*height)
        area = width*height

        with open(train_lbl, 'r') as f:
            lines = f.readlines()

        # some quick return algorithm
        # 1. if no label, then directly return
        # 2. if all small boxes, directly return
        if lines == []:
            return -1
        big_box = 0
        for line in lines:
            cls, xc, yc, w, h = line.split(' ')
            xc, yc, h, w = float(xc), float(yc), float(h), float(w)
            xc, yc, h, w = int(width*xc), int(height*yc), int(height*h), int(width*w)

            if h*w <= THRESHOLD_AREA:
                continue
            else:
                big_box+=1
        if big_box == 0:
            return -1

        # if there are some big boxes in the image, process it and create aug files
        image = np.array(Image.open(train_img))
        new_im = image.copy()

        occ = [] # put all boxes in to this list
        with open(savepath_lbl, 'w') as f:
            f.write('')

        for line in lines:
            with open(savepath_lbl, 'a') as f:
                f.write(line)

            cls, xc, yc, w, h = line.split(' ')

            xc, yc, h, w = float(xc), float(yc), float(h), float(w)
            xc, yc, h, w = int(width*xc), int(height*yc), int(height*h), int(width*w)

            y1 = max(0, yc - h/2)
            x1 = max(0, xc - w/2)
            y2 = min(height, y1+h)
            x2 = min(width, x1+w)

            if h*w <= THRESHOLD_AREA:
                continue
            else:
                occ.append([cls, x1, y1, x2, y2]) # x1y1x2y2

        # now we make sure in occ and occ_new, all are big boxes
        occ_new = occ.copy()
        if len(occ) > 3: # if too many boxes, we don't copy-paste that much
            R = 1
        for _ in range(R):
            for box in occ:
                _, x1, y1, x2, y2 = box
                h, w = y2-y1, x2-x1

                valid = False
                val_cnt = 0 # check if while loop is a endless loop
                while not valid: # keep finding valid position to place the fake box
                    dx = np.random.randint(0, width-w)
                    if mask_top:
                        dy = np.random.randint(margin, height-h)
                    else:
                        dy = np.random.randint(0, margin-h)

                    res = []
                    val_cnt+=1
                    if val_cnt > quit: # if bad-luck, we give up this box
                        break 

                    for boxn in occ_new:
                        cls, x1n, y1n, x2n, y2n = boxn
                        hn, wn = y2n-y1n, x2n-x1n

                        res.append(self._valid_x(dx, x1n, x2n) or self._valid_x(dy, y1n, y2n))

                    if np.all(np.array(res, dtype=bool)):
                        valid = True
                        with open(savepath_lbl, 'a') as f:
                            # cls, xc, yc, w, h
                            line = ' '.join([str(i) for i in [cls, (dx+w/2)/width, (dy+h/2)/height, w/width, h/height]])
                            f.write(line+'\n')


                if val_cnt <=quit: # if lucky, we move to new round, if not, we give up this box
                    patch = image[int(y1):int(y1+h), int(x1):int(x1+w), :]

                    if np.random.rand() < 0.5: # vertical random flip
                        patch = patch[::-1, :, :]
                    if np.random.rand() < 0.5: # horizontal random flip
                        patch = patch[:, ::-1, :]

                    new_im[int(dy):int(dy+h), int(dx):int(dx+w), :] = patch

                    # update occ_new in x1y1x2y2
                    occ_new.append([cls, dx, dy, dx+w, dy+h])

        image_ready = Image.fromarray(new_im)
        image_ready.save(savepath_img)
        
    
    def create_aug_dataset(self, savepath_img:str, savepath_lbl:str, repeat: int, **kwargs):

        # create folders
        os.makedirs('{}'.format(savepath_img), exist_ok=True)
        os.makedirs('{}'.format(savepath_lbl), exist_ok=True)

        failed = 0
        invalid = 0
        for i, l in tqdm(zip(self.aug_train_img, self.aug_train_lbl), total = len(self.aug_train_img)):
            _, fname = os.path.split(i)
            name, ext = fname.split('.')
            #print(name)
            cnt = 0
            while cnt<repeat:
                try:
                    status = self._augmentation(train_img=i, train_lbl=l,  
                                                savepath_img=savepath_img + '{}_{}.jpg'.format(name, cnt),
                                                savepath_lbl=savepath_lbl + '{}_{}.txt'.format(name, cnt),
                                                **kwargs)
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
        n_aug_img = sorted(glob.glob('{}/*'.format(savepath_img)))
        print(len(n_aug_img))

        n_aug_lbl = sorted(glob.glob('{}/*'.format(savepath_lbl)))
        print(len(n_aug_lbl))
        
        print('Done! {s1} of images failed, {s2} of invalid thus no augmentation applied.\nAmong {s3} valid images, with repeat factor <{s4}>,\ntotal images after augmentaion: {s5} + {s6}*{s7} = {s8}'.format(s1=failed, s2=invalid,s3=len(self.aug_train_img)-invalid,s4=repeat, s5=invalid, s6=len(self.aug_train_img)-invalid, s7=repeat, s8=len(n_aug_img)))
