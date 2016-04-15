#!/usr/bin/env python

import os
import numpy as np
from sklearn.cross_validation import train_test_split

class classifier(object):
  """
  based class from which each classification algorithm is derived
  """

  def __init__(self):
    pass

  def test(self):
    """
    purely virutal method
    """                      
    raise NotImplementedError(':test')

  def train(self):
    """
    purely virutal method
    """                      
    raise NotImplementedError(':train')

  def eval(self):
    """
    purely virutal method
    """                      
    raise NotImplementedError(':eval')

class dataset():
  """
  class to store information related to input/output data
  """
  def __init__(self, filename):
    if not os.path.exists(filename):
      raise LookupError('Input file not found %s', filename)

    self.labelMap = {} # stores maps {label_names -> whole_numbers}            
    self.reverseLabelMap = {} # stores maps {whole_numbers -> label_names}
    self.features = []
    self.labels = []

  def splitData(self, testSplit : 'float'):
    """
    uses the sklearn.cross_validation module to perform a random splitting of
    the input data
    """
    self.features_train, self.features_test, self.labels_train, self.labels_test = \
      train_test_split(self.features, self.labels, test_size=testSplit)
