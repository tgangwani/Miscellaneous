from PIL import Image
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from operator import sub, add
from math import exp
from math import log
from multiprocessing import Process, Manager
import sys
from random import randint

serial = False   # serial or parallel implementation
imageName = sys.argv[1]
numSegments = int(sys.argv[2])
_id = sys.argv[3]   #unique id to identify run
pixels = list()
w_i_j = list()
numPixels = 0
outImg = None
transformationM = None  # transformation matrix
manager = Manager()
count = 0
pixelMean = None

# EM-Parameters
segmentProb = np.zeros(numSegments) 
segmentMean = np.zeros((numSegments, 3))

def readImage():
    global numPixels, outImg, transformationM, pixelMean
    im = Image.open(imageName) #Can be many different formats.
    #im = Image.open("tiny.png") #Can be many different formats.
    pix = im.load()
    outImg = Image.new(im.mode, im.size)    
    
    data = list()
    for c in range(im.size[1]):
        for r in range(im.size[0]):
            data.append(pix[r, c])
    
    # dataframe with the pixel data            
    df = pd.DataFrame(data)
    #df.drop(df.columns[[3]], axis=1, inplace=True)
    
    pixelMean = tuple(df.mean().astype(int))
    df = df - df.mean()

    # do Cholesky decomposition (AA') of the cov matrix of data, and multiply 
    # the data by inv(A) to get data with cov matrix = I. We assume this to be 
    # the cov matrix of all the normal distributions
    covMat = np.cov(df, rowvar=0)
    transformationM = np.linalg.cholesky(covMat)
    df = pd.DataFrame((np.dot(np.linalg.inv(transformationM), df.T)).T)
    for index, row in df.iterrows():
        pixels.append(row)
    numPixels = len(pixels)

# random initialization for clustering
def randomInit():
  global segmentProb, segmentMean
  rands = [randint(0, numPixels) for _ in range(numSegments)]
  segmentMean = np.asarray([pixels[r] for r in rands])
  rands = list(map(lambda x:x/float(sum(rands)), rands))
  segmentProb = np.asarray(rands)

# kmeans for initial clustering estimate     
def kmeans():
    #km = KMeans(n_clusters=numSegments, n_jobs=numSegments)
    km = KMeans(n_clusters=numSegments, n_init=1)
    labels = list(km.fit_predict(pixels))
    
    # initialize EM-parameters based on K-means results
    for i in range(numSegments):
        segmentProb[i] = (labels.count(i))/numPixels
    
        # list of all pixels in cluster i
        pixel_ids = [a for a,b in enumerate(labels) if b == i]
        mean_vec = np.array([1/numPixels]*3)  # smooths data
        for pixel_id in pixel_ids:
          mean_vec = np.add(mean_vec, pixels[pixel_id])
                
        segmentMean[i] = mean_vec/labels.count(i)

def e():
    for pixel in pixels:
        w_j = list()
        for segment in range(numSegments):
            _product = segmentProb[segment] 
            e = exp(-0.5 * pow(np.linalg.norm(list(map(sub, pixel, segmentMean[segment]))), 2))
            _product *= e
            w_j.append(_product)        
            
        # normalize w_j
        w_j = list(map(lambda x : x/sum(w_j), w_j))
        w_i_j.append(w_j)
        
def e_parallel(i, peices):
    
    w_i_j_local = []
    chunk = int(numPixels/numSegments) # chunk of pixels for each thread
    _start = i*chunk            
    _end = None
    if i == numSegments-1:
      _end = numPixels
    else:
      _end = (i+1)*chunk
        
    for pixel in pixels[_start:_end]:
        w_j = list()
        for segment in range(numSegments):
            _product = segmentProb[segment] 
            e = exp(-0.5 * pow(np.linalg.norm(list(map(sub, pixel, segmentMean[segment]))), 2))
            _product *= e
            w_j.append(_product)        
            
        # normalize w_j
        w_j = list(map(lambda x : x/sum(w_j), w_j))
        w_i_j_local.append(w_j)
    
    peices[i] = w_i_j_local
    return 

def m():
    # update the parameters      
    for i in range(numSegments):
        # pie-j 
        segmentProb[i] = sum(list(map(lambda x:x[i], w_i_j)))/numPixels
                
        # u-j
        num = np.array([.001/numPixels]*3)  # smooths data        
        denom = sum(list(map(lambda x:x[i], w_i_j)))
        for p in range(numPixels):
            num = np.add(num, pixels[p]*w_i_j[p][i])
        
        assert(denom!=0)
        segmentMean[i] = num / denom 

    return

def m_parallel(i, _segmentProb, _segmentMean):
    # update the parameters      
    
    # pie-j 
    _segmentProb[i] = sum(list(map(lambda x:x[i], w_i_j)))/numPixels

    # u-j
    num = np.array([.001/numPixels]*3)  # smooths data        
    denom = sum(list(map(lambda x:x[i], w_i_j)))
    for p in range(numPixels):
        num = np.add(num, pixels[p]*w_i_j[p][i])
    
    assert(denom!=0)
    _segmentMean[i] = num / denom 
    
    return

def myfunc(p, segment):
  inner = log(segmentProb[segment]) 
  inner -= 0.5 * pow(np.linalg.norm(list(map(sub, pixels[p], segmentMean[segment]))), 2)
  return inner*w_i_j[p][segment]

def l_parallel(i, peices):
    
    chunk = int(numPixels/numSegments) # chunk of pixels for each thread
    _start = i*chunk            
    _end = None
    if i == numSegments-1:
      _end = numPixels
    else:
      _end = (i+1)*chunk
       
    peices[i] = 0.
    
    vfunc = np.vectorize(myfunc)
    pix = np.array(list(range(_start, _end)))
    for segment in range(numSegments):
      inner = vfunc(pix, segment)
      peices[i] += sum(inner)
   
    # non-vectorized version of above code
    #for p in range(_start, _end):
    #  for segment in range(numSegments):
    #    inner = log(segmentProb[segment]) 
    #    inner -= 0.5 * pow(np.linalg.norm(list(map(sub, pixels[p], segmentMean[segment]))), 2)
    #    peices[i] += inner*w_i_j[p][segment]

def em():
    global segmentProb, segmentMean
    likelihood = float('-inf')

    while True:
        w_i_j[:] = []  # clear w_i_j matrix

        if serial:
          e()
        else:
          peices = manager.dict()
          jobs = []
          for i in range(numSegments):
            p = Process(target=e_parallel, args=(i, peices))
            jobs.append(p)
            p.start()
           
          for p in jobs:
            p.join()

          for key in sorted(peices.keys()):
            w_i_j.extend(peices[key])
        
        print("E Done")

        # calculate change in likelihood, and check for convergence   
        peices = manager.dict()
        jobs = []
        for i in range(numSegments):
          p = Process(target=l_parallel, args=(i, peices))
          jobs.append(p)
          p.start()
         
        for p in jobs:
          p.join()                                             

        l = sum(peices.values())  
        print('Likelihood=', l)
        # convergence criteria
        if l < likelihood or (l - likelihood)/abs(l) < 0.000001:
            break

        likelihood = l            
        
        if serial:
          m()
        else:
          _segmentProb = manager.dict()
          _segmentMean = manager.dict()
          jobs = []
          for i in range(numSegments):
            p = Process(target=m_parallel, args=(i, _segmentProb, _segmentMean))
            jobs.append(p)
            p.start()
           
          for p in jobs:
            p.join()
          
          for k,v in _segmentProb.items():
            segmentProb[k] = v
          for k,v in _segmentMean.items():
            segmentMean[k] = v

        print("M Done")
        
        print("++Parameters++")
        print(segmentProb)
        print(segmentMean)
        print("++")
        segmentImage()

def getSegment(pixel):
    distances = [(np.linalg.norm(list(map(sub, pixel, segmentMean[segment]))), segment) for segment in range(numSegments)]
    minD = min(distances)
    return segmentMean[minD[1]]

def segmentImage():
    global count
    outPixels = list()
    
    #for each pixel, get the cluster mean with the max prob.
    for p in range(numPixels):
        _max = w_i_j[p].index(max(w_i_j[p]))
        outPixels.append(segmentMean[_max])
    
    #for pixel in pixels:
    #    outPixels.append(getSegment(pixel))
     
    # re-apply the transformation to get the image
    outPixels = (np.dot(transformationM, np.array(outPixels).T)).T
    outImg.putdata([tuple(map(add, tuple(x), pixelMean)) for x in outPixels.astype(int).tolist()])
    outImg.save(imageName+"_"+str(numSegments)+"_"+str(count)+".jpg")
    count += 1
    print("Output Image Created")

if __name__=="__main__":
    readImage()
    print("Reading Done")
    #randomInit()
    #print("RandomInit Done")
    kmeans()
    print("KMeans Done")
    em()
    #segmentImage()
