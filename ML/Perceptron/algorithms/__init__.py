from .iris_d import iris # iris database
from .gtd_d import gtd # gtd database
from enum import Enum                 
from .perceptron import perceptron 

class algo(str, Enum):
  """
  insert all supported algorithms here
  """
  perceptron = 'perceptron'

  @property
  def method(self):
    return algo.get_method(self) 

  @classmethod
  def get_method(cls, a) -> 'class object':
    if a is cls.perceptron:
      return perceptron
    else:
      raise KeyError("Unrecognized algorithm %s" % a)

def run(filename : 'str', algorithm : 'str', kwds):
  d = gtd(filename)
  d.splitData(kwds['testSplit'])
                          
  # select the algorithm to run and train                        
  sel = algo(algorithm).method(d, **kwds)
  sel.train()
  sel.test()
  sel.eval()
