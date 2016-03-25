import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from math import log
from math import exp
from scipy.misc import logsumexp
np.set_printoptions(threshold=np.nan)

numTopics = 30 # number of clusters
documents = list()
documentsSparse = list()

# EM-Parameters
topicProb = np.zeros(numTopics) 
wordProb = None
numDocs = None
vocabLen = None
numWords = None

def readFile():
    global wordProb, numDocs, vocabLen, numWords
    with open('docword.nips.txt') as f:
        numDocs = int(f.readline().rstrip('\n'))
        vocabLen = int(f.readline().rstrip('\n')) 
        numWords = int(f.readline().rstrip('\n'))
        wordProb = np.zeros((numTopics, vocabLen))        
        
    f.close()    
    
    #df = pd.read_csv('test.txt', header=None, skiprows=3, sep=r"\s+", names=["docID", "wordID", "count"])
    df = pd.read_csv('docword.nips.txt.orig', header=None, skiprows=3, sep=r"\s+", names=["docID", "wordID", "count"])
    
    # create the document vectors    
    for i in range(numDocs):
        d = np.zeros(vocabLen)
        indices = list(df[df["docID"]==i+1]["wordID"])
        indices = list(map(lambda x:x-1, indices))    # python index from 0
        vals = list(df[df["docID"]==i+1]["count"])
        d[indices] = vals
        documentsSparse.append(list(zip(indices, vals)))
        documents.append(d)
     
# kmeans for initial clustering estimate     
def kmeans():
    km = KMeans(n_clusters=numTopics)
    labels = list(km.fit_predict(documents))
    
    # initialize EM-parameters based on K-means results
    for i in range(numTopics):
        topicProb[i] = (labels.count(i))/numDocs
    
        # list of all documents in cluster i
        doc_ids = [a for a,b in enumerate(labels) if b == i]
        word_vec = np.array([1/numWords]*vocabLen)  # smooths data
        for doc_id in doc_ids:
            word_vec = np.add(word_vec, documents[doc_id])
                
        wordProb[i] = word_vec/np.sum(word_vec)
        
    
# expectation step of EM
def e():
    w_i_j = list()  # for each document, we store numTopics values in this
    for document in documentsSparse:
        log_vec = list()
        w_j = list()
        for topic in range(numTopics):
            _wordProb = wordProb[topic]
            m_log = log(topicProb[topic]) 
            for idx, val in document:
                m_log += val*log(_wordProb[idx])
            log_vec.append(m_log)
         
        # Nice trick to calculate the prob(hidden variable) for each document. We can't
        # do product of probabilities since the FP number becomes too small for the machine
        # We go to the log domain (Piazza post)
        max_log_vec = max(log_vec)
        log_vec = list(map(lambda x:x - max_log_vec, log_vec))
        les = logsumexp(log_vec)
        log_vec = list(map(lambda x:x - les, log_vec))
        
        w_j = [exp(x) for x in log_vec]
        w_i_j.append(w_j)
          
    return w_i_j      
    
# maximization step of EM
def m(w_i_j):
    # update the parameters    
    for i in range(numTopics):
        # pie-j 
        topicProb[i] = sum(list(map(lambda x:x[i], w_i_j)))/numDocs
                
        # p-j
        num = np.array([1/numWords]*vocabLen)  # smooths data
        denom = 0
        for d in range(len(documents)):
            num = np.add(num, documents[d]*w_i_j[d][i])
            denom += sum(documents[d])*w_i_j[d][i]
        
        assert(denom!=0)
        wordProb[i] = num / denom 

    return
    
def em():

    likelihood = float('-inf')

    while True:
        w_i_j = e()
         
        # calculate change in likelihood, and check for convergence   
        l = 0. 
        for d in range(len(documents)):
            for t in range(numTopics):
                _wordProb = wordProb[t]
                inner = log(topicProb[t]) 
                for idx, val in documentsSparse[d]:
                    inner += val*log(_wordProb[idx])
                
                l += inner*w_i_j[d][t]
        
        print('Likelihood=', l)
        # convergence criteria
        if l < likelihood or (l - likelihood)/abs(l) < 0.000001:
            break

        likelihood = l             
        m(w_i_j)
    
if __name__=="__main__":
    readFile()
    print("Reading Done")
    kmeans()
    em()
    print("Topic Prob")        
    print(topicProb)
    print(sum(topicProb))    
    
    print("Word Prob")
    for w in wordProb:
        s = sorted(list(zip(w, list(range(vocabLen)))), reverse=True)
        print(s[0:10])
        print([x[1] for x in s[0:10]])
        print(sum(w))
        print('\n')
