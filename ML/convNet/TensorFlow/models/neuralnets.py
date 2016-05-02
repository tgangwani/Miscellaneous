import tensorflow as tf                                   
import datetime
import os

class neuralnet(object):
  """
  all neural net arch. classes derive from this base class
  """

  def __init__(self):
    self.sess = tf.Session()

    # tensorboard 
    tensorboardOut = os.getcwd() + "/tensorboard_logs/" + '-'.join(str(datetime.datetime.now()).split(' ')) 
    if not os.path.exists(tensorboardOut):
      os.makedirs(tensorboardOut)
    self.summary_writer = tf.train.SummaryWriter(tensorboardOut)

  def weight_variable(self, shape : 'list'): 
    """
    template to create weight matrix
    """
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

  def bias_variable(self, shape : 'list'): 
    """
    template to create bais vector
    """
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

  def conv2d(self, x, W, stride : 'int', padding='SAME'):
    """
    Convolution layer
    """
    return tf.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding=padding)

  def max_pool_2x2(self, x, padding='SAME'):
    """
    2x2 Max-pool layer
    """
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding=padding)

  def __str__(self):
    """
    purely virtual
    """
    raise NotImplementedError(':__str__')

  def run(self):
    """
    purely virtual
    """
    raise NotImplementedError(':run')
