#!/usr/bin/env python

import algorithms
import os

#filename = 'iris.data'  # expects csv
filename = 'gtd.data' # expects csv
filename = os.curdir + "/" + filename                  

# pass fully qualified file name to run()
# TODO: use 'argparse' module to take this from command line
algorithms.run(filename, 'perceptron', {'testSplit':0.2, 'learningRate':0.005, \
'maxIterations':10000})
