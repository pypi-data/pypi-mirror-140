# Object_Detection_Toolkit
A tool kit for checking boxes in a dataset and visualize predictions' distribution

## PyPI
Project is listed under: https://pypi.org/project/ODToolkit/

## Install
To install this tool, simply 
```
pip install ODToolkit
```
## Functions
| **Component**                  | **Description**                                                         |
|--------------------------------|-------------------------------------------------------------------------|
| Analysis()                     | Module for False-Positive and False-Negative analysis                   |
| Transformation()               | Module for transformation between image xy plane and homography plane   |
| Visualization()                | Module for False-Positive and False-Negative visualization              |
| Dataset.DatasetMaker()         | Module for train/test split and sort into folders for training          |
## Usage
To use, simply follow belows snippet:

```
# ===================================
# demo for Analysis and Visualization
# ===================================
from ODToolkit import Analysis, Visualization

# get FP, FN, correct
FP, FN, correct = Analysis.get_fpfn(gt_lbl=gt_lbl,       # 假定已经准备好了
                                    pred_lbl=pred_lbl,   # 假定已经准备好了
                                    img_w=640,
                                    img_h=480,
                                    iou_thresh=0.25)

# visualize FP, FN, correct
visualizer = Visualization.BoxVisualizer(img_w=640, img_h=480)
visualizer.show_fpfn(FP, FN, correct, figsize=[15,10])
```
![sample](https://github.com/BarCodeReader/ODToolkit/blob/master/asset/show_fpfn.png)

## Unit-test
For unit-test, we use ```Behave```, which provides a very flexible environment for all kinds of tests

To view a sample, go to ```unit_tests``` folder and check ```*.feature``` and ```steps/*.py``` files

To run tests, simply:
```
behave unit_tests/               # run all tests
behave unit_tests/xxx.feature    # run particular test you want
```

## To contribute
If you want to contribute to this project, please submit a pull request with unit tests.
