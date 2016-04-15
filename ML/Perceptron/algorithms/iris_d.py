#!/usr/bin/env python

from .base import dataset
import pandas as pd
import numpy as np

class iris(dataset):
  """
  class for the iris dataset
  """
  def __init__(self, filename):
    super().__init__(filename)
    self.readFile(filename)

  def readFile(self, filename):
    # read data into a data-frame
    data = pd.read_csv(filename, header=None, skiprows=0, sep=r",")
    self.features = np.array(data.ix[:,0:3])
    self.labels = list(data.ix[:,4])
    
    # add a column of 1's to the feature vector since we'll absort theta into the
    # w-matrix
    ones = np.ones([self.features.shape[0], 1])
    self.features = np.append(self.features, ones, axis=1)

    # fill maps
    for label, index in zip(set(self.labels), range(len(set(self.labels)))):
      self.labelMap[index] = label
      self.reverseLabelMap[label] = index

    # change the labels on input data to whole numbers
    for index in range(len(self.labels)):
      self.labels[index] = self.reverseLabelMap[self.labels[index]]

    self.num_labels = self.labelMap.__len__() # number of 'unique' labels
    self.features_dim = self.features.shape[1] # dimensionality of data

