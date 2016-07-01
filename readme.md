# Motion Tracking
Practical assignment for the CG course in [PUC_RS](http://www.inf.pucrs.br/~pinho/CG-PPGCC/Trabalhos/T2-2016-1/T1-2016-1.html)

# Files
The *main.py* contains the the methods for showning the video.
And for the user interaction.
It draws the trackers from the *Tracker* class or the *Vector* class

The *tracking* file contains the methods for the three implemented tracking algorithms.

The *utils* file is the utility methods used to help the conversions and image processing
to help me do the tracking

# Branches
The [0.2](https://github.com/rodsnjr/motion_tracking/tree/0.2) branch of this repository is where the *tracker* identification and labeling approach was made as discussed in class.

# Libraries used
All algorithms used were hand made, only with the help of:
* Numpy for the array processing
* OpenCV for the circle and line drawings and video frame readings/writing
* Python 3.5.1 with [miniconda](http://conda.pydata.org/miniconda.html) distribution.
