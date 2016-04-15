#!/usr/bin/env python

from .base import classifier
from .base import dataset
import numpy as np
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('info.log', mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class perceptron(classifier):
  """
  multi-class perceptron 
  """
  def __init__(self, d : 'dataset', **kwds):
    super().__init__()                    
    assert isinstance(d, dataset)

    # the weight matrix is rxd, r=#labels, d=featureDimension+1
    self.weights = np.zeros([d.num_labels, d.features_dim])
    self.learningRate = kwds['learningRate']
    self.maxIterations = kwds['maxIterations']
    self.dataset = d
  
  def eval(self):
    logger.info('Begin evaluating Perceptron')
    fd = open('eval.txt', 'w')

    for _id, feature in zip(self.dataset.eventids_eval, \
        self.dataset.features_eval):
      prediction = self.dataset.labelMap[self.getLabel(feature)]
      fd.write("Eventid:" + str(_id) +  "\tPredicted group:" + prediction+"\n")

    fd.close()

  def test(self):
    logger.info('Begin testing Perceptron')

    mistakes = int(0)
    for feature, label in zip(self.dataset.features_test, self.dataset.labels_test):
      prediction = self.getLabel(feature)
      if prediction != label:
        mistakes = mistakes + 1

    print('Test accuracy={:f}'.format(1-mistakes/len(self.dataset.labels_test)))

  def getLabel(self, feature) -> 'label':
    prediction = np.argmax(np.dot(self.weights, feature))
    return prediction

  def train(self):
    logger.info('Begin training Perceptron')
    logger.info("#Training Samples=%i" %len(self.dataset.labels_train))
 
    iterations = int(0)
    mistakes = int(0)

    while True:
      
      iterations = iterations + 1 
      if iterations == self.maxIterations:
        logger.info('Reached maximum iteration count. Terminating training')
        print('Training accuracy={:f}'.format(1-mistakes/len(self.dataset.labels_train)))
        break

      mistakes = 0  # reset
      for feature, label in zip(self.dataset.features_train, self.dataset.labels_train):
        prediction = self.getLabel(feature)
        
        # mistake-bound perceptron algorithm using Keslers's construction. If
        # case of a misprediction, we increase weights corresponding to the
        # correct label, and decrease weights corresponding to the predicted
        # label
        if prediction != label:
          u_mat = np.zeros(self.weights.shape)
          u_mat[label,:] = self.learningRate*feature
          u_mat[prediction,:] = (-1.)*self.learningRate*feature
           
          # update the weights matrix 
          self.weights = np.add(self.weights, u_mat)
          mistakes = mistakes + 1
      
      if not mistakes:
        logger.info('Training complete. No mistakes on training data')
        break
      else:
        logger.debug("Completed iteration %i  #Mistakes %i" %(iterations, mistakes))
