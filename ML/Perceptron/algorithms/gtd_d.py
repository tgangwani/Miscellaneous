#!/usr/bin/env python

from .base import dataset
import pandas as pd
import numpy as np

class gtd(dataset):
  """
  class for the gtd dataset
  """
  def __init__(self, filename):

    # typedefs ('float' instead of 'int', since pandas has trouble when
    # dtype=int has Nan in the input file)
    categorical = np.float32 
    boolean = np.float32 

    # dictionary of important features (manually selected) to start analysis
    # we could use PCA/RandomForest/other-techniques to further reduce dimensionality 
    self.relevantFeatures = {
        'eventid':int,
        'extended':boolean,
        'country':categorical,
        'region':categorical,
        'latitude':np.float32,
        'longitude':np.float32,
        'attacktype1':categorical,
        'success':boolean,
        'suicide':boolean,
        'crit1':boolean,
        'crit2':boolean,
        'crit3':boolean,
        'multiple':boolean,
        'targtype1':categorical,
        'natlty1':categorical,
        'guncertain1':boolean,
        'claimed':boolean,
        'weaptype1':categorical,
        'nkill':np.float32,
        'nwound':np.float32,
        'property':boolean,
        'ishostkid':boolean,
        'INT_LOG':boolean,
        'INT_IDEO':boolean,
        'INT_MISC':boolean,
        'INT_ANY':boolean,
        'gname':str
    }
    
    super().__init__(filename)
    self.readFile(filename)

  def readFile(self, filename):
    # read data into a data-frame
    data = pd.read_csv(filename, header=0, skiprows=0,\
        sep=r",", na_values=" NaN", dtype=self.relevantFeatures)

    #select relevant features
    data = data[list(self.relevantFeatures.keys())] 

    # ad-hoc : dropping the rows with a NaN. We could do something intelligent
    # here like deducing the hidden/missing variables
    data.dropna(inplace=True)

    # separate the dataframe to be predicted
    evalFrame = data[data['gname']=='Unknown']

    # fill the labels (group-name) and features
    data = data[data['gname']!='Unknown']
    self.labels = list(data['gname']) 
    data.drop(['gname', 'eventid'], axis=1, inplace=True)
    self.features=np.array(data)
    
    # add a column of 1's to the feature vector since we'll absort theta into the
    # w-matrix
    self.features = np.append(self.features, np.ones([self.features.shape[0], 1]), axis=1)

    # fill maps
    for label, index in zip(set(self.labels), range(len(set(self.labels)))):
      self.labelMap[index] = label
      self.reverseLabelMap[label] = index

    # change the labels on input data to whole numbers
    for index in range(len(self.labels)):
      self.labels[index] = self.reverseLabelMap[self.labels[index]]

    self.num_labels = self.labelMap.__len__() # number of 'unique' labels
    self.features_dim = self.features.shape[1] # dimensionality of data

    # fill the features for evaluation using the 'evalFrame' dataframe that was
    # created earlier
    self.eventids_eval = list(evalFrame['eventid'])  # event-ids for the incidents with unknown group
    evalFrame.drop(['gname', 'eventid'], axis=1, inplace=True)
    self.features_eval = np.array(evalFrame)

    # add a column of 1's to the feature vector 
    self.features_eval = np.append(self.features_eval, np.ones([self.features_eval.shape[0], 1]), axis=1)
