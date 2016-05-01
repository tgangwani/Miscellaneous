#!/usr/bin/env python

import sys
from datasets import mnist
from enum import Enum

class selection(str, Enum):
  """
  class to return the dataset object from an input string describing the dataset
  """

  #add datasets here..
  mnist = 'mnist'

  @property
  def method(self):
    return selection.get_(self)
  
  @classmethod
  def get_(cls, a):
    if a is cls.mnist:
      return mnist  #class obj 
    else:
      raise KeyError("Unrecognized option %s" % a)

# init dataset object
data = selection('mnist').method()

# run nn1 type neural network on the dataset
data.run('nn1')
