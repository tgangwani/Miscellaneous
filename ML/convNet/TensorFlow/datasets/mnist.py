import sys
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from models import neuralnet 

class mnist(neuralnet):
  """
  define new nn* classes within this class to create new neural net
  architectures. Each nn* class needs __str__() and arch(nn) 
  """

  class nn1(object):
    
    def __str__(self):
      """
      print architecture
      """
      desc = "==Conv. net==\n \
          [Convolution layer]\n \
          [Max-pool layer]\n \
          [Convolution layer]\n \
          [Max-pool layer]\n \
          [Fully-connected layer]\n \
          [Softmax layer]"
      return desc

    def arch(self, nn) -> 'final node of the tensor flow graph (y_conv)':
      """
      defines the conv. net architecture
      """

      print(self)

      # first conv. layer 
      # 5x5 filter, 1 input channel, 32 output channels
      W_conv1 = nn.weight_variable([5, 5, 1, 32])
      b_conv1 = nn.bias_variable([32])
      stride1 = 1
      h_conv1 = tf.nn.relu(nn.conv2d(nn.x_image, W_conv1, stride1) + b_conv1)
      
      # first pooling layer (2x2) 
      h_pool1 = nn.max_pool_2x2(h_conv1)

      # second conv. layer 
      # 5x5 filter, 32 input channel, 64 output channels
      W_conv2 = nn.weight_variable([5, 5, 32, 64])
      b_conv2 = nn.bias_variable([64])
      stride2 = 1
      h_conv2 = tf.nn.relu(nn.conv2d(h_pool1, W_conv2, stride2) + b_conv2)

      # second pooling layer (2x2) 
      h_pool2 = nn.max_pool_2x2(h_conv2)

      # reshape (flatten) output
      h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])

      # first fully connected layer
      W_fc1 = nn.weight_variable([7 * 7 * 64, 1024])
      b_fc1 = nn.bias_variable([1024])
      h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

      # dropout
      h_fc1_drop = tf.nn.dropout(h_fc1, nn.keep_prob)

      # second (final) fully connected layer (softmax)
      W_fc2 = nn.weight_variable([1024, 10])
      b_fc2 = nn.bias_variable([10])
      y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

      return y_conv


  class nn2(object):
    
    def __str__(self):
      """
      print architecture
      """
      desc = "==Conv. net==\n \
          [Convolution layer]\n \
          [Max-pool layer]\n \
          [Convolution layer]\n \
          [Convolution layer]\n \
          [Fully-connected layer]\n \
          [Softmax layer]"
      return desc

    def arch(self, nn) -> 'final node of the tensor flow graph (y_conv)':
      """
      defines the conv. net architecture
      """

      print(self)

      # first conv. layer 
      # 5x5 filter, 1 input channel, 32 output channels
      W_conv1 = nn.weight_variable([5, 5, 1, 32])
      b_conv1 = nn.bias_variable([32])
      stride1 = 1
      h_conv1 = tf.nn.relu(nn.conv2d(nn.x_image, W_conv1, stride1, 'VALID') + b_conv1) 
      # outputs a 24x24x32 image
      
      # first pooling layer (2x2) 
      h_pool1 = nn.max_pool_2x2(h_conv1) 
      # outputs a 12x12x32 image

      # second conv. layer 
      # 3x3 filter, 32 input channel, 32 output channels
      W_conv2 = nn.weight_variable([3, 3, 32, 32])
      b_conv2 = nn.bias_variable([32])
      stride2 = 1
      h_conv2 = tf.nn.relu(nn.conv2d(h_pool1, W_conv2, stride2, 'VALID') + b_conv2)
      # outputs a 10x10x32 image

      # third conv. layer
      # 3x3 filter, 32 input channel, 32 output channels
      W_conv3 = nn.weight_variable([3, 3, 32, 32])
      b_conv3 = nn.bias_variable([32])
      stride3 = 1
      h_conv3 = tf.nn.relu(nn.conv2d(h_conv2, W_conv3, stride3, 'VALID') + b_conv3)
      # outputs a 8x8x32 image

      # reshape (flatten) output
      h_conv3_flat = tf.reshape(h_conv3, [-1, 8*8*32])

      # first fully connected layer
      W_fc1 = nn.weight_variable([8 * 8 * 32, 1024])
      b_fc1 = nn.bias_variable([1024])
      h_fc1 = tf.nn.relu(tf.matmul(h_conv3_flat, W_fc1) + b_fc1)

      # dropout
      h_fc1_drop = tf.nn.dropout(h_fc1, nn.keep_prob)

      # second (final) fully connected layer (softmax)
      W_fc2 = nn.weight_variable([1024, 10])
      b_fc2 = nn.bias_variable([10])
      y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

      return y_conv


  # more classes here ..  


  def __init__(self):
    self.data = input_data.read_data_sets('MNIST_data', one_hot=True)
    super().__init__()

  def run(self, arch : 'str'):
    """
    function to select neural net
    """
    if not hasattr(self, arch):
      print("Unrecognized neural net type %s" % arch)
      sys.exit(1)

    # placeholders for feature vector and labels
    x = tf.placeholder(tf.float32, shape=[None, 784])
    y_ = tf.placeholder(tf.float32, shape=[None, 10])
    
    # dropout probability
    self.keep_prob = tf.placeholder(tf.float32)

    # reshape input image
    self.x_image = tf.reshape(x, [-1,28,28,1])
     
    # get the output node from the architecture-defining object
    obj = getattr(self, arch)()
    y_conv = obj.arch(self)

    # define the loss function here (TODO: parameterize?). We use cross-entropy
    cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))

    # define the gradient update method here (TODO: parameterize?)
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

    correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    # summary-op for tensorboard
    summary_op = tf.scalar_summary("training accuracy", accuracy)
    self.summary_writer.add_graph(self.sess.graph)

    # init tensorflow variables 
    self.sess.run(tf.initialize_all_variables())

    # stochastic gradient descent (mini-batch training)
    # TODO: parameterize numbers used in here)
    for i in range(500):
      batch = self.data.train.next_batch(50)

      # gather summary and write, every 100 steps
      if i%100 == 0:

        summary_op_str = self.sess.run(summary_op, feed_dict={
            x:batch[0], y_: batch[1], self.keep_prob: 1.0})
        self.summary_writer.add_summary(summary_op_str, i)
        print(summary_op_str)

      self.sess.run(train_step, feed_dict={x: batch[0], y_: batch[1], self.keep_prob: 0.5})

    # get test accuracy
    print("test accuracy %g"%(self.sess.run(accuracy, feed_dict={
        x: self.data.test.images, y_: self.data.test.labels, self.keep_prob: 1.0})))

    self.sess.close()
