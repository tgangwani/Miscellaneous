The two files run the 'expectation-minimization' algorithm on multinomial and gaussian mixture models. Please read each question for a description of what the corresponding python file implements.  
segmentation.py file includes a parallel implementation of EM using the 'multiprocessing' module. Initial clustering is done using KMEANS.


"FILE : topics.py"
The UCI Machine Learning dataset repository hosts several datasets recording word counts for documents here. You will use the NIPS dataset. You will find (a) a table of word counts per document and (b) a vocabulary list for this dataset at the link. You must implement the multinomial mixture of topics model, lectured in class. For this problem, you should write the clustering code yourself (i.e. not use a package for clustering).
Cluster this to 30 topics, using a simple mixture of multinomial topic model, as lectured in class.
Produce a graph showing, for each topic, the probability with which the topic is selected.
Produce a table showing, for each topic, the 10 words with the highest probability for that topic.


"FILE : segmentation.py"
Image segmentation using EM You can segment an image using a clustering method - each segment is the cluster center to which a pixel belongs. In this exercise, you will represent an image pixel by its r, g, and b values (so use color images!). Use the EM algorithm applied to the mixture of normal distribution model lectured in class to cluster image pixels, then segment the image by mapping each pixel to the cluster center with the highest value of the posterior probability for that pixel. You must implement the EM algorithm yourself (rather than using a package). We will release a set of test images shortly; till then, use any color image you care to.
Segment each of the test images to 10, 20, and 50 segments. You should display these segmented images as images, where each pixel's color is replaced with the mean color of the closest segment
