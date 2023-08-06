# Object_Detection_Toolkit
A tool kit for checking boxes in a dataset and visualize predictions' distribution

## Install
To install this tool, simply 
```
pip install Object_Detection_Toolkit
```
## Functions
There are few functions in the Visualizer object.
1. ```BoxVisualizer.show_boxes(**kargs)```: show all the boxes in a dataset, including there actual positions, histogram and heatmaps

2. ```BoxVisualizer.get_fpfn(**kargs)```: calculate FP, FN and correct predictions giving GT and Pred
3. ```BoxVisualizer.show_fpfn(**kargs)```: show FP, FN and correct boxes obtained from step 2

## Usage
To use, simply follow belows snippet:
```
from Object_Detection_Toolkit.Visualizer import BoxVisualizer

bv = BoxVisualizer(img_w=640, img_h=480)    # image size of your dataset

train_lbl = [...]                           # list of your train label txt
test_lbl = [...]                            # list of your test label txt
bv.show_boxes(labels=[train_lbl, test_lbl], 
              mode=['train', 'test'])       # show the boxes in a dataset

FP, FN, correct = bv.get_fpfn(**kargs)      # calculate FP, FN and Correct boxes
bv.show_fpfn(FP, FN, correct)               # show FP, FN and Correct boxes calculated just now
```

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